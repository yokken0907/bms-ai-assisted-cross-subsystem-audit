# B0 RAUC source-freeze record v1.0.1

Recorded before B1 candidate generation.

- target: rauc/rauc
- frozen commit: 1a412fe80badb9cf91f5374ea2ef791de4db55a9
- source acquisition: quiet git clone + detached checkout of exact commit
- cloc version: 1.98
- cloc include languages: C,C++
- cloc excluded directories: .git,build,dist,out,vendor,vendors,third_party,third-party,external,generated,gen
- non-generated C/C++ LOC: 36820
- C/C++ file count reported by cloc: 67
- deterministic source tar SHA-256: f0e4c65831e4242709d262b2451745108d78bb83c6f42567b2d3cd0369d48cd6
- complete non-.git file-manifest SHA-256: 7c0953624afee716c62ecebca37fc003f662b7c38a0266ac92e89636f549154e
- prior B0 source-freeze workflow run: 37503869800
- prior B0 source-freeze artifact digest: sha256:95a0188ec4de00648a67d3b5f99308de72d860b9fae1f8421939d634cfe3b1e2

## Frozen admissible evidence surfaces

Present in the frozen tree before B1:
- runtime implementation under src/
- public headers/contracts under include/ and src/bootloaders/*.h
- configuration/build surfaces including meson.build, meson_options.txt, service/config files
- contemporaneous documentation under docs/ and README.rst
- extensive tests under test/ and fuzz targets under fuzz/

No issue/PR/fix-history reconnaissance is part of this B0 record.
