"""Regression for OCI smoke failure in GitHub Actions 40975979003.

Test the exact Node source passed to docker run -e without Docker or credentials.
These mock-only checks do not replace actual amd64/arm64 image execution.
"""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/ci_oci_runtime_smoke.sh'


def inline_probe() -> str:
    shell = SCRIPT.read_text(encoding='utf-8')
    return shell.split('--entrypoint node "$image" -e \'', 1)[1].split("' \"$target\"", 1)[0]


def invoke(target: str, *, runtime_arch: str = 'x64', uid: int = 1000,
           compiled: bool = True, npm: bool = False) -> subprocess.CompletedProcess:
    # Test-only patches are injected in the host child process. The real CI
    # script does not contain any mock, environment bypass or skip switch.
    prep = '''
const fs=require("fs");
Object.defineProperty(process,"arch",{value:process.argv[3]});
process.getuid=()=>Number(process.argv[4]);
fs.existsSync=p=>p==="/usr/local/bin/npm"?process.argv[6]==="yes":process.argv[5]==="yes";
fs.statSync=()=>({isFile:()=>process.argv[5]==="yes"});
const source=process.argv[1];process.argv[1]=process.argv[2];eval(source);
'''
    return subprocess.run(
        ['node', '-e', prep, inline_probe(), target, runtime_arch,
         str(uid), 'yes' if compiled else 'no', 'yes' if npm else 'no'],
        capture_output=True, text=True, timeout=10,
    )


class RuntimeArchitectureHotfix(unittest.TestCase):
    def test_real_amd64_mapping_accepts_x64_when_non_root(self):
        r = invoke('amd64', runtime_arch='x64')
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_arm64_mapping_accepts_arm64_when_non_root(self):
        r = invoke('arm64', runtime_arch='arm64')
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_mismatched_amd64_is_rejected(self):
        r = invoke('amd64', runtime_arch='arm64')
        self.assertEqual(r.returncode, 42, r.stderr)
        self.assertIn('architecture mismatch', r.stderr)

    def test_mismatched_arm64_is_rejected(self):
        self.assertEqual(invoke('arm64', runtime_arch='x64').returncode, 42)

    def test_root_process_rejected_independently_of_architecture(self):
        for target, arch in [('amd64', 'x64'), ('arm64', 'arm64')]:
            with self.subTest(target=target):
                r=invoke(target, runtime_arch=arch, uid=0)
                self.assertEqual(r.returncode, 45, r.stderr)
                self.assertIn('runs as root', r.stderr)

    def test_missing_compiled_assets_rejected(self):
        self.assertEqual(invoke('amd64', compiled=False).returncode, 43)

    def test_unwanted_npm_rejected(self):
        self.assertEqual(invoke('amd64', npm=True).returncode, 44)

    def test_shell_and_bad_argument_gates(self):
        self.assertEqual(subprocess.run(['bash','-n',str(SCRIPT)]).returncode, 0)
        for args in [('quorivio:test','x86'),('quorivio:test',),('oops;bad','arm64')]:
            r=subprocess.run(['bash',str(SCRIPT),*args],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode, 2, r.stderr)


if __name__ == '__main__':
    unittest.main()
