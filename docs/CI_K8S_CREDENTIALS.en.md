# CI Kubernetes credentials acceptance

Independent wizard outputs intentionally differ because they contain freshly generated secrets. CI must compare repeat invocations in the same directory and avoid printing secret diffs. Execute `python3 tools/check_k8s_generation.py` to check stable regeneration, distinct credentials for two new installations, and private file permissions. The tool uses disposable temporary directories and does not deploy anything. GitHub CI rerun remains required.
