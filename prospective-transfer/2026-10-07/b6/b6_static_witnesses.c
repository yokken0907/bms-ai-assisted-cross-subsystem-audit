#include <stdint.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

static void c001_mbr_narrowing(void) {
    uint64_t sector64 = (uint64_t)UINT32_MAX + 1u;
    uint32_t narrowed = (uint32_t)sector64;
    printf("C001 sector64=%" PRIu64 " narrowed=%" PRIu32 "\n", sector64, narrowed);
}
static void c002_clear_counter_width(void) {
    uint64_t target = (uint64_t)UINT32_MAX + 4096u;
    uint32_t before = UINT32_MAX - 255u;
    uint32_t after = before + 512u;
    printf("C002 target=%" PRIu64 " before=%" PRIu32 " after_plus_512=%" PRIu32 " monotonic=%s\n",
           target, before, after, after > before ? "yes" : "no");
}
static void c003_region_sum_wrap(void) {
    uint64_t start = UINT64_MAX - 511u;
    uint64_t size = 1024u;
    uint64_t wrapped = start + size;
    printf("C003 start=%" PRIu64 " size=%" PRIu64 " wrapped_sum=%" PRIu64 "\n", start, size, wrapped);
}
static void c007_polling_ms_intermediate(void) {
    int interval_sec = 3000000;
    int unsafe_as_int = interval_sec > INT_MAX / 1000;
    int64_t mathematical_ms = (int64_t)interval_sec * 1000;
    printf("C007 interval_sec=%d INT_MAX=%d exceeds_safe_int_mul=%s mathematical_ms=%" PRId64 "\n",
           interval_sec, INT_MAX, unsafe_as_int ? "yes" : "no", mathematical_ms);
}
static uint64_t mirror_binary_suffix(const char *s, const char **tail_out) {
    char *tail = NULL;
    uint64_t result = strtoull(s, &tail, 10);
    unsigned shift = 0;
    switch ((*tail) | 0x20) {
        case 'k': shift = 10; break;
        case 'm': shift = 20; break;
        case 'g': shift = 30; break;
        case 't': shift = 40; break;
        default: shift = 0; break;
    }
    if (tail_out) *tail_out = tail;
    return result << shift;
}
static void c008a_suffix_tail(void) {
    const char *tail = NULL;
    uint64_t v = mirror_binary_suffix("1Kgarbage", &tail);
    printf("C008a input=1Kgarbage parsed=%" PRIu64 " unconsumed_tail=%s\n", v, tail);
}
static void c008b_suffix_shift_wrap(void) {
    uint64_t base = UINT64_C(9223372036854775808);
    uint64_t scaled = base << 10;
    printf("C008b base=%" PRIu64 " shift=10 scaled_mod_2^64=%" PRIu64 "\n", base, scaled);
}
static void c009_polling_backoff_wrap(void) {
    uint64_t interval_ms = UINT64_C(86400000);
    uint64_t factor = UINT64_MAX / interval_ms + 1u;
    uint64_t product = interval_ms * factor;
    __uint128_t math = (__uint128_t)interval_ms * (__uint128_t)factor;
    int exceeds = math > UINT64_MAX;
    printf("C009 interval_ms=%" PRIu64 " factor=%" PRIu64 " product_mod_2^64=%" PRIu64 " mathematical_exceeds_uint64=%s\n",
           interval_ms, factor, product, exceeds ? "yes" : "no");
}
int main(void) {
    c001_mbr_narrowing();
    c002_clear_counter_width();
    c003_region_sum_wrap();
    c007_polling_ms_intermediate();
    c008a_suffix_tail();
    c008b_suffix_shift_wrap();
    c009_polling_backoff_wrap();
    return 0;
}
