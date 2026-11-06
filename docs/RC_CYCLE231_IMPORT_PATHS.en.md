# RC231 — deterministic Python CI import paths

## Trigger

GitHub run `42233651517` failed in the first RC230 inventory promotion guard, launched with `python3 -m unittest tools.tests.test_rc230_inventory_promotion -q` and no `PYTHONPATH`. The current inventory facade was imported as `tools.verify_rc_current_inventory`, but imported sibling `ci_inventory_reference_guard` as a top-level module. The earlier local test harness had inadvertently supplied `PYTHONPATH=tools`, masking the failure.

## Repair

Add the canonical sibling tools directory to `sys.path` inside `verify_rc_current_inventory.py` before importing helper modules. Retain the existing unqualified verifier module name so historical tests and `verify_rc_release_status` continue to receive the expected `verify_rc_cycleNNN_inventory` name. Test both direct script and package-based unittest entry points without `PYTHONPATH` from the repository root, as done in GitHub Actions. New independent pre-npm check executes these commands. Do not weaken fail-closed inventory or Git index checks.

## Safety / progress

RC230 source inventory is historical and immutable. RC231 is the sole current inventory. No application logic, security, database, image publication or user permissions modified. Certified 85.25% unchanged; current full CI RC231 still requires GitHub execution. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
