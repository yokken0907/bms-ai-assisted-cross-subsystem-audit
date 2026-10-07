# B0 source-freeze integrity reconciliation v1.0.0

Two preserved GitHub Actions source-freeze artifacts were downloaded and compared.

## Initial freeze
- run: `37503869800`
- artifact ID: `11430922452`
- artifact ZIP SHA-256: `95a0188ec4de00648a67d3b5f99308de72d860b9fae1f8421939d634cfe3b1e2`
- inner source tar SHA-256: `b6a082ce15bf7de9a5becb808bea1682e3a500f2889fe4d086b31fbf79c8cd83`
- archive root: `target/`

## Corrected B0-record freeze
- run: `37509459688`
- artifact ID: `11435380162`
- artifact ZIP SHA-256: `56c92ead78d41b86c1293a6c29e05b2052c12c60faf3a407799a8abe9c636986`
- inner source tar SHA-256: `f0e4c65831e4242709d262b2451745108d78bb83c6f42567b2d3cd0369d48cd6`
- archive root: `rauc-target/`
- cloc: 36,820 C LOC / 67 files

The package/tar hashes differ because the workflows used different archive root names and path-bearing manifest representations.

After stripping only the root name and comparing source bytes:
- files: 448 vs 448
- missing/extra paths: 0
- content hash mismatches: 0
- normalized relative-path/content manifest SHA-256 for both:
  `1608c6eeec94c9720958f1e2080c2d4c0685a8d461e9fcd1b0f5d2be3830d971`

Conclusion: the two preserved freezes contain the same target source bytes.
