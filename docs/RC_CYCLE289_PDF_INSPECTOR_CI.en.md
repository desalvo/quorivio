# RC289 — PDF quality-gate dependency provisioning

## Evidence

Full CI [42666096697](https://github.com/desalvo/quorivio/actions/runs/42666096697), Production quality gate: `tools.tests.test_rc287_result_formatting.test_six_published_pdfs_are_current_and_illustrated` failed with `ModuleNotFoundError: No module named 'fitz'`. The earlier RC287 and RC286 tests both need PyMuPDF to inspect embedded images in six bilingual PDF manuals; the dependency was only installed at the later real-screenshot publication step.

## Corrective change

Install and smoke-test pinned `pymupdf==1.26.7` before the two early manual gates, retaining the existing later image-dependent PDF tests and current-commit screenshot capture. A new pre-install contract fails if the provisioner is absent, unpinned, moved after the tests or if either PDF contract is removed. It contains negative-case mutation tests. No application functionality or image-evidence semantics are changed.

## Verification

Run `python3 -m unittest tools.tests.test_rc289_pdf_ci_order tools.tests.test_rc287_result_formatting tools.tests.test_rc286_authoring_manuals -q`, and run the full CI after committing the release. The full CI remains pending until GitHub verifies the provisioning step and the remaining runtime gates.
