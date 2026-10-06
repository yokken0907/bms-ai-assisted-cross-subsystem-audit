# RAUC B6 separate implementation/static-contract checks v1.0.0

Target frozen source: `rauc/rauc` @ `1a412fe80badb9cf91f5374ea2ef791de4db55a9`

Same-author witnesses are deliberately separate from the RAUC implementation. They test bounded C representation/arithmetic/parser propositions only; they are not external replication and do not simulate RAUC hardware, kernel, or field behavior.

Compile command: `gcc -std=c11 -Wall -Wextra -Werror -O0 b6_static_witnesses.c -o b6_static_witnesses`
Compile return code: 0
Run return code: 0

## Output

```text
C001 sector64=4294967296 narrowed=0
C002 target=4294971391 before=4294967040 after_plus_512=256 monotonic=no
C003 start=18446744073709551104 size=1024 wrapped_sum=512
C007 interval_sec=3000000 INT_MAX=2147483647 exceeds_safe_int_mul=yes mathematical_ms=3000000000
C008a input=1Kgarbage parsed=1024 unconsumed_tail=Kgarbage
C008b base=9223372036854775808 shift=10 scaled_mod_2^64=0
C009 interval_ms=86400000 factor=213503982335 product_mod_2^64=34448384 mathematical_exceeds_uint64=yes
```

## Interpretation

- C001: a 64-bit sector count of UINT32_MAX+1 narrows to 0 in uint32_t.
- C002: a 32-bit byte counter can wrap while the target remains a larger 64-bit size.
- C003: an aligned 64-bit start+size can wrap to a small value.
- C007: an accepted-scale seconds value can require a millisecond product larger than INT_MAX; the witness avoids executing signed-overflow UB and checks the precondition with widened arithmetic.
- C008a: a parser with the frozen source's decimal-prefix/first-suffix-character structure accepts 1Kgarbage as 1024 while trailing text remains.
- C008b: the unsigned left shift can wrap modulo 2^64.
- C009: the mixed-width backoff product can exceed UINT64_MAX mathematically while the unsigned C product is reduced modulo 2^64.

No witness establishes target reachability by itself; reachability is adjudicated separately from frozen RAUC source.

Local package ZIP SHA-256: `1c3ec6def10e9d68f4544bcc79a6a1a567839cd30e2b84c1cb33d2091a1eb811`
