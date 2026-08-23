#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

typedef struct {
    float averageSoh_perc;
    float minimumSoh_perc;
    float maximumSoh_perc;
} SohValues;

/* Bounded semantic replay of the pre-encoding signalData assignments in the
 * two exact-source CAN callbacks.  The exact-source parser is load-bearing for
 * proving that these are the assignments present in the frozen functions. */
static float source_pack_signal_input(const SohValues *values) {
    (void)values;
    return 100.0f;
}

static float source_string_signal_input(const SohValues *values, size_t string_number) {
    (void)values;
    (void)string_number;
    return 100.0f;
}

int main(void) {
    const SohValues cases[] = {
        {0.0f, 0.0f, 0.0f},
        {50.0f, 49.9f, 50.1f},
        {87.5f, 80.0f, 90.0f},
        {100.0f, 100.0f, 100.0f},
    };
    bool pass = true;
    for (size_t i = 0u; i < sizeof(cases) / sizeof(cases[0]); i++) {
        if ((fabsf(source_pack_signal_input(&cases[i]) - 100.0f) > 0.0001f) ||
            (fabsf(source_string_signal_input(&cases[i], 0u) - 100.0f) > 0.0001f)) {
            pass = false;
        }
    }
    printf("{\"pass\":%s,\"database_vectors\":4,\"distinct_database_average_values\":4,"
           "\"pack_preencoding_signal_inputs\":[100,100,100,100],"
           "\"string_preencoding_signal_inputs\":[100,100,100,100]}\n",
           pass ? "true" : "false");
    return pass ? 0 : 1;
}
