#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

/* Configuration truth table.  In CHARGE state the documented/configuration
 * contract selects the CHARGE flag, while the audited executive conditional
 * selects the NORMAL flag. */

int main(void) {
    size_t scenarios = 0u;
    size_t mismatches = 0u;
    bool pass = true;

    for (unsigned normal = 0u; normal <= 1u; normal++) {
        for (unsigned charge = 0u; charge <= 1u; charge++) {
            const unsigned reference_charge_enabled = charge;
            const unsigned actual_charge_enabled = normal;
            scenarios++;
            if (reference_charge_enabled != actual_charge_enabled) {
                mismatches++;
            }
        }
    }
    pass = (scenarios == 4u) && (mismatches == 2u);
    printf("{\"pass\":%s,\"scenario_count\":%zu,\"reference_divergence_count\":%zu,"
           "\"truth_table\":[{\"normal\":0,\"charge\":0,\"actual\":0,\"reference\":0},"
           "{\"normal\":0,\"charge\":1,\"actual\":0,\"reference\":1},"
           "{\"normal\":1,\"charge\":0,\"actual\":1,\"reference\":0},"
           "{\"normal\":1,\"charge\":1,\"actual\":1,\"reference\":1}]}\n",
           pass ? "true" : "false", scenarios, mismatches);
    return pass ? 0 : 1;
}
