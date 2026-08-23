#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define STRINGS 2u
#define MODULES 1u
#define CELLS_PER_MODULE 18u
#define WIRES (MODULES * (CELLS_PER_MODULE + 1u))

static void audited_expression(const uint8_t table[STRINGS][WIRES], int diagnosis_not_ok[STRINGS]) {
    uint8_t openWireDetected = 0u;
    for (uint8_t s = 0u; s < STRINGS; s++) {
        for (uint8_t m = 0u; m < MODULES; m++) {
            for (uint8_t wire = 0u; wire < (CELLS_PER_MODULE + 1u); wire++) {
                if (table[s][(wire + (m * (CELLS_PER_MODULE + 1u))) == 1u] > 0u) {
                    openWireDetected++;
                }
            }
        }
        diagnosis_not_ok[s] = (openWireDetected == 0u) ? 0 : 1;
    }
}

static void reference_expression(const uint8_t table[STRINGS][WIRES], int diagnosis_not_ok[STRINGS]) {
    for (uint8_t s = 0u; s < STRINGS; s++) {
        uint8_t openWireDetected = 0u;
        for (uint8_t m = 0u; m < MODULES; m++) {
            for (uint8_t wire = 0u; wire < (CELLS_PER_MODULE + 1u); wire++) {
                if (table[s][wire + (m * (CELLS_PER_MODULE + 1u))] > 0u) {
                    openWireDetected++;
                }
            }
        }
        diagnosis_not_ok[s] = (openWireDetected == 0u) ? 0 : 1;
    }
}

int main(void) {
    uint8_t table[STRINGS][WIRES];
    int actual[STRINGS] = {0, 0};
    int reference[STRINGS] = {0, 0};
    unsigned detected_indices = 0u;
    unsigned missed_indices = 0u;

    for (unsigned index = 0u; index < WIRES; index++) {
        memset(table, 0, sizeof(table));
        table[0][index] = 1u;
        audited_expression(table, actual);
        reference_expression(table, reference);
        printf("index=%u actual_string0=%d reference_string0=%d\n", index, actual[0], reference[0]);
        if (actual[0] != 0) {
            detected_indices++;
        } else {
            missed_indices++;
        }
        if (reference[0] != 1) {
            return 10;
        }
    }

    memset(table, 0, sizeof(table));
    table[0][1] = 1u;
    audited_expression(table, actual);
    reference_expression(table, reference);
    printf("carryover_actual_string1=%d carryover_reference_string1=%d\n", actual[1], reference[1]);
    printf("summary_detected_indices=%u summary_missed_indices=%u\n", detected_indices, missed_indices);

    if (detected_indices != 2u || missed_indices != 17u) {
        return 20;
    }
    if (actual[1] != 1 || reference[1] != 0) {
        return 30;
    }
    return 0;
}
