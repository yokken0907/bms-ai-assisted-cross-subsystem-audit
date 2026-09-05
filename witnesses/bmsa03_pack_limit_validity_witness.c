#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

/* Bounded replay of the exact pack-limit pre-encoding expression and the
 * 0..409500 W / 100 W-per-bit signal preparation boundary.  The validity flag
 * is varied but not consumed, matching the frozen callback lineage. */

static double pack_power_w(int32_t current_m_a, int32_t battery_voltage_m_v) {
    return ((double)current_m_a / 1000.0) * ((double)battery_voltage_m_v / 1000.0);
}

static uint32_t encode_power(double power_w) {
    if (power_w < 0.0) {
        power_w = 0.0;
    }
    if (power_w > 409500.0) {
        power_w = 409500.0;
    }
    return (uint32_t)(power_w / 100.0);
}

int main(void) {
    const int32_t currents_m_a[] = {0, 2400};
    const int32_t voltages_m_v[] = {400000, INT32_MAX};
    const unsigned invalid_flags[] = {0u, 1u};
    size_t scenarios = 0u;
    size_t propagated_invalid_nonzero = 0u;
    size_t saturated_invalid_nonzero = 0u;
    bool pass = true;

    for (size_t c = 0u; c < 2u; c++) {
        for (size_t v = 0u; v < 2u; v++) {
            const unsigned invalid = invalid_flags[v];
            const double power = pack_power_w(currents_m_a[c], voltages_m_v[v]);
            const uint32_t encoded = encode_power(power);
            scenarios++;
            if ((invalid == 1u) && (currents_m_a[c] != 0)) {
                if (power > 0.0) {
                    propagated_invalid_nonzero++;
                }
                if (encoded == 4095u) {
                    saturated_invalid_nonzero++;
                }
            }
            if ((currents_m_a[c] == 0) && ((fabs(power) > 1.0e-12) || (encoded != 0u))) {
                pass = false;
            }
        }
    }

    const double nominal_w = pack_power_w(2400, 400000);
    const double sentinel_w = pack_power_w(2400, INT32_MAX);
    pass = pass && (scenarios == 4u) && (fabs(nominal_w - 960.0) < 1.0e-9) &&
           (fabs(sentinel_w - 5153960.7528) < 1.0e-6) && (encode_power(nominal_w) == 9u) &&
           (encode_power(sentinel_w) == 4095u) && (propagated_invalid_nonzero == 1u) &&
           (saturated_invalid_nonzero == 1u);

    printf("{\"pass\":%s,\"scenario_count\":%zu,\"nominal_power_w\":%.4f,"
           "\"nominal_encoded_raw\":%u,\"invalid_sentinel_power_w\":%.4f,"
           "\"invalid_sentinel_encoded_raw\":%u,\"propagated_invalid_nonzero\":%zu,"
           "\"saturated_invalid_nonzero\":%zu,\"zero_current_control_raw\":0}\n",
           pass ? "true" : "false", scenarios, nominal_w, encode_power(nominal_w), sentinel_w,
           encode_power(sentinel_w), propagated_invalid_nonzero, saturated_invalid_nonzero);
    return pass ? 0 : 1;
}
