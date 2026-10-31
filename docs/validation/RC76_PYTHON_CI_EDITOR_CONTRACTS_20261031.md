# RC76 CI repair — evidence notes

- GitHub job 124557792918 on commit 39564e862a2ed431544cea22e0c0b39bd6794b34: npm build and Node suite succeeded, 1439 Python tests ran, 5 source-contract assertions failed.
- Updated legacy assertions while keeping requirements for permission fields, safe page-wide timing guard, private/rehearsal data boundaries, widget schema parity, and live dashboard integration.
- Added targeted preflight before npm; no unit test skipped, no production code or existing SHA-256 history modified.
- Current score 84.75%; no gate promotion until post-commit CI acceptance.
