#include "diag_cfg.h"
#include <inttypes.h>
#include <stdio.h>

_Static_assert(DIAG_DELAY_1000ms == 1000u, "DIAG_DELAY_1000ms mismatch");
_Static_assert(DIAG_DELAY_2000ms == 1000u, "exact-source DIAG_DELAY_2000ms expansion changed");

int main(void) {
    printf("DIAG_DELAY_1000ms=%" PRIu32 "\n", (uint32_t)DIAG_DELAY_1000ms);
    printf("DIAG_DELAY_2000ms=%" PRIu32 "\n", (uint32_t)DIAG_DELAY_2000ms);
    return 0;
}
