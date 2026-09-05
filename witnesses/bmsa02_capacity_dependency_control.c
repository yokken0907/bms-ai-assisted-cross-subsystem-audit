#include <math.h>
#include <stdbool.h>
#include <stdio.h>

static float indicated_remaining_after_actual_full_discharge(float configured_mAh, float retention) {
    const float actual_mAh = configured_mAh * retention;
    const float indicated_decrement_pct = 100.0f * actual_mAh / configured_mAh;
    return 100.0f - indicated_decrement_pct;
}

int main(void) {
    /* 3500 mAh is parsed from BC_CAPACITY_mAh in the frozen source.  Retention
     * points are controlled abstractions, not measurements of the foxBMS cell. */
    const float configured_mAh = 3500.0f;
    const float r100 = indicated_remaining_after_actual_full_discharge(configured_mAh, 1.0f);
    const float r90 = indicated_remaining_after_actual_full_discharge(configured_mAh, 0.9f);
    const float r80 = indicated_remaining_after_actual_full_discharge(configured_mAh, 0.8f);
    const bool pass = fabsf(r100) < 0.0001f && fabsf(r90 - 10.0f) < 0.0001f && fabsf(r80 - 20.0f) < 0.0001f;
    printf("{\"pass\":%s,\"configured_capacity_mAh\":3500,"
           "\"controlled_retention\":[1.0,0.9,0.8],"
           "\"indicated_remaining_pct_after_actual_full_discharge\":[%.6f,%.6f,%.6f]}\n",
           pass ? "true" : "false", r100, r90, r80);
    return pass ? 0 : 1;
}
