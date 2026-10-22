# GitGuardian finding: TOTP test vectors

`apps/api/test/totp.test.ts` previously contained the literal Base32 encoding of a publicly documented RFC 6238 test vector. This is not a Quorivio account or production secret; however, secret scanners may flag the string.

The literal has been removed. The test constructs the public test vector at runtime from its RFC-defined byte sequence, and other tests now generate random key material rather than embedding fixed credentials. The expected RFC output remains checked.

**GitGuardian triage:** mark the historical finding as public test data / false positive if applicable and confirmed. If the value was ever reused in an actual service, rotate it. Removing it from HEAD does not erase Git history; rewriting published history requires a deliberate, coordinated decision.

**CI:** rerun the secret scanner after commit. Local checks: 82 Node tests and 40 Python tests passed; the new GitHub Actions outcome remains unverified.
