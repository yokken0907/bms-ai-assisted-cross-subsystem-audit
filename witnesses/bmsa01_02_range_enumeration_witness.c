#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

/*
 * Controlled, range-independent sensitivity enumeration for BMSA-01.
 * The five range labels are the IVT-S variants retained in the audited
 * BMSA-01 Phase-5 evidence.  They are not an assertion about deployed
 * hardware.  The semantic replay is the exact SOC counting expression:
 *     current_mA * timeStep_s / 12600000 mAs * 100 percent.
 * The invalid flag is intentionally varied but not consumed, matching the
 * frozen consumer expression.  The zero-current row is the BMSA-02 control.
 */

static double soc_delta_percent(double current_a, double time_step_s) {
    const double capacity_m_as = 12600000.0;
    return ((current_a * 1000.0) * time_step_s / capacity_m_as) * 100.0;
}

int main(void) {
    const double ranges_a[] = {100.0, 300.0, 500.0, 1000.0, 2500.0};
    const double fractions[] = {0.0, 0.1, 0.5, 1.0};
    const unsigned validity_flags[] = {0u, 1u};
    size_t scenarios = 0u;
    size_t nonzero_invalid_propagations = 0u;
    size_t validity_pair_equalities = 0u;
    double maximum_absolute_delta = 0.0;
    bool pass = true;

    for (size_t r = 0u; r < sizeof(ranges_a) / sizeof(ranges_a[0]); r++) {
        for (size_t f = 0u; f < sizeof(fractions) / sizeof(fractions[0]); f++) {
            double paired[2] = {0.0, 0.0};
            for (size_t v = 0u; v < sizeof(validity_flags) / sizeof(validity_flags[0]); v++) {
                (void)validity_flags[v];
                paired[v] = soc_delta_percent(ranges_a[r] * fractions[f], 1.0);
                scenarios++;
                if ((validity_flags[v] == 1u) && (fractions[f] > 0.0) && (fabs(paired[v]) > 0.0)) {
                    nonzero_invalid_propagations++;
                }
                if (fabs(paired[v]) > maximum_absolute_delta) {
                    maximum_absolute_delta = fabs(paired[v]);
                }
            }
            if (fabs(paired[0] - paired[1]) < 1.0e-12) {
                validity_pair_equalities++;
            } else {
                pass = false;
            }
            if ((fractions[f] == 0.0) && (fabs(paired[0]) > 1.0e-12)) {
                pass = false;
            }
        }
    }

    pass = pass && (scenarios == 40u) && (nonzero_invalid_propagations == 15u) &&
           (validity_pair_equalities == 20u) && (fabs(maximum_absolute_delta - 19.841269841269842) < 1.0e-9);

    printf("{\"pass\":%s,\"scenario_count\":%zu,\"range_variant_count\":5,"
           "\"fractions\":[0,0.1,0.5,1.0],\"validity_flags\":[0,1],"
           "\"validity_pair_equalities\":%zu,\"nonzero_invalid_propagations\":%zu,"
           "\"zero_current_control_delta_pct\":0,\"maximum_absolute_delta_pct\":%.12f}\n",
           pass ? "true" : "false", scenarios, validity_pair_equalities, nonzero_invalid_propagations,
           maximum_absolute_delta);
    return pass ? 0 : 1;
}
