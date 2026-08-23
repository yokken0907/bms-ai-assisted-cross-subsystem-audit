/*
 * BMSA-12 BMSA06-F01 bounded semantic replay.
 *
 * This is not a foxBMS target build.  It replays only the four source-level
 * contracts already established by the BMSA-06 Phase4 host-unit tests:
 *   1. zero valid temperatures retain INT16_MAX/INT16_MIN sentinels;
 *   2. those sentinels take all-OK thermal SOA branches while charging;
 *   3. the same occurs while discharging; and
 *   4. a threshold-499 fatal diagnosis counter is cleared by 500 OK events.
 *
 * Exact source identity, function lineage, and the canonical Phase4/Phase5
 * packages are checked separately.  No physical or deployed behavior is
 * represented here.
 */

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum {
    BMSA06_SENSOR_COUNT = 8,
    BMSA06_DIAG_THRESHOLD = 499,
};

typedef struct {
    int16_t minimum_ddegC;
    int16_t maximum_ddegC;
    uint16_t valid_count;
    float average_ddegC;
    bool return_not_ok;
} BMSA06_EXTREMA_s;

typedef struct {
    uint16_t counter;
    bool fatal_active;
} BMSA06_DIAG_STATE_s;

static BMSA06_EXTREMA_s BMSA06_CalculateExtrema(
    const int16_t temperatures_ddegC[BMSA06_SENSOR_COUNT],
    const bool invalid[BMSA06_SENSOR_COUNT]) {
    BMSA06_EXTREMA_s result = {
        .minimum_ddegC = INT16_MAX,
        .maximum_ddegC = INT16_MIN,
        .valid_count = 0u,
        .average_ddegC = 0.0F,
        .return_not_ok = false,
    };
    int32_t sum_ddegC = 0;

    for (size_t i = 0u; i < BMSA06_SENSOR_COUNT; i++) {
        if (!invalid[i]) {
            result.valid_count++;
            sum_ddegC += temperatures_ddegC[i];
            if (temperatures_ddegC[i] < result.minimum_ddegC) {
                result.minimum_ddegC = temperatures_ddegC[i];
            }
            if (temperatures_ddegC[i] > result.maximum_ddegC) {
                result.maximum_ddegC = temperatures_ddegC[i];
            }
        }
    }
    if (result.valid_count > 0u) {
        result.average_ddegC = (float)sum_ddegC / (float)result.valid_count;
    } else {
        result.return_not_ok = true;
    }
    return result;
}

static unsigned BMSA06_CountThermalOkEvents(
    const int16_t minimum_ddegC,
    const int16_t maximum_ddegC,
    const bool charging) {
    const int16_t maximum_msl_ddegC = charging ? 450 : 550;
    const int16_t maximum_rsl_ddegC = charging ? 400 : 500;
    const int16_t maximum_mol_ddegC = charging ? 350 : 450;
    const int16_t minimum_msl_ddegC = -200;
    const int16_t minimum_rsl_ddegC = -150;
    const int16_t minimum_mol_ddegC = -100;
    unsigned ok_events = 0u;

    if (maximum_ddegC < maximum_msl_ddegC) {
        ok_events++;
        if (maximum_ddegC < maximum_rsl_ddegC) {
            ok_events++;
            if (maximum_ddegC < maximum_mol_ddegC) {
                ok_events++;
            }
        }
    }
    if (minimum_ddegC > minimum_msl_ddegC) {
        ok_events++;
        if (minimum_ddegC > minimum_rsl_ddegC) {
            ok_events++;
            if (minimum_ddegC > minimum_mol_ddegC) {
                ok_events++;
            }
        }
    }
    return ok_events;
}

static void BMSA06_DiagNotOk(BMSA06_DIAG_STATE_s *state) {
    if (state->counter < BMSA06_DIAG_THRESHOLD) {
        state->counter++;
    } else if (state->counter == BMSA06_DIAG_THRESHOLD) {
        state->counter++;
        state->fatal_active = true;
    }
}

static void BMSA06_DiagOk(BMSA06_DIAG_STATE_s *state) {
    if (state->counter > 1u) {
        state->counter--;
    } else if (state->counter == 1u) {
        state->counter = 0u;
        state->fatal_active = false;
    }
}

int main(void) {
    int16_t temperatures_ddegC[BMSA06_SENSOR_COUNT];
    bool invalid[BMSA06_SENSOR_COUNT];
    for (size_t i = 0u; i < BMSA06_SENSOR_COUNT; i++) {
        temperatures_ddegC[i] = 123;
        invalid[i] = true;
    }

    const BMSA06_EXTREMA_s extrema = BMSA06_CalculateExtrema(temperatures_ddegC, invalid);
    const unsigned charging_ok_events =
        BMSA06_CountThermalOkEvents(extrema.minimum_ddegC, extrema.maximum_ddegC, true);
    const unsigned discharging_ok_events =
        BMSA06_CountThermalOkEvents(extrema.minimum_ddegC, extrema.maximum_ddegC, false);

    BMSA06_DIAG_STATE_s diagnosis = {.counter = 0u, .fatal_active = false};
    for (unsigned i = 0u; i < BMSA06_DIAG_THRESHOLD; i++) {
        BMSA06_DiagNotOk(&diagnosis);
    }
    const unsigned counter_after_499_not_ok = diagnosis.counter;
    const bool fatal_after_499_not_ok = diagnosis.fatal_active;
    BMSA06_DiagNotOk(&diagnosis);
    const unsigned counter_after_500th_not_ok = diagnosis.counter;
    const bool fatal_after_500th_not_ok = diagnosis.fatal_active;
    for (unsigned i = 0u; i < BMSA06_DIAG_THRESHOLD; i++) {
        BMSA06_DiagOk(&diagnosis);
    }
    const unsigned counter_after_499_ok = diagnosis.counter;
    const bool fatal_after_499_ok = diagnosis.fatal_active;
    BMSA06_DiagOk(&diagnosis);
    const unsigned counter_after_500th_ok = diagnosis.counter;
    const bool fatal_after_500th_ok = diagnosis.fatal_active;

    const bool pass = extrema.return_not_ok &&
        (extrema.minimum_ddegC == INT16_MAX) &&
        (extrema.maximum_ddegC == INT16_MIN) &&
        (extrema.valid_count == 0u) &&
        (extrema.average_ddegC == 0.0F) &&
        (charging_ok_events == 6u) &&
        (discharging_ok_events == 6u) &&
        (counter_after_499_not_ok == 499u) &&
        !fatal_after_499_not_ok &&
        (counter_after_500th_not_ok == 500u) &&
        fatal_after_500th_not_ok &&
        (counter_after_499_ok == 1u) &&
        fatal_after_499_ok &&
        (counter_after_500th_ok == 0u) &&
        !fatal_after_500th_ok;

    printf(
        "{\"case_id\":\"BMSA06-F01\","
        "\"zero_valid_temperature_state\":%s,"
        "\"minimum_ddegC\":%d,\"maximum_ddegC\":%d,"
        "\"valid_count\":%u,\"average_ddegC\":%.1f,"
        "\"charging_ok_events\":%u,\"discharging_ok_events\":%u,"
        "\"counter_after_499_not_ok\":%u,\"fatal_after_499_not_ok\":%s,"
        "\"counter_after_500th_not_ok\":%u,\"fatal_after_500th_not_ok\":%s,"
        "\"counter_after_499_ok\":%u,\"fatal_after_499_ok\":%s,"
        "\"counter_after_500th_ok\":%u,\"fatal_after_500th_ok\":%s,"
        "\"pass\":%s}\n",
        extrema.return_not_ok ? "true" : "false",
        (int)extrema.minimum_ddegC,
        (int)extrema.maximum_ddegC,
        (unsigned)extrema.valid_count,
        (double)extrema.average_ddegC,
        charging_ok_events,
        discharging_ok_events,
        counter_after_499_not_ok,
        fatal_after_499_not_ok ? "true" : "false",
        counter_after_500th_not_ok,
        fatal_after_500th_not_ok ? "true" : "false",
        counter_after_499_ok,
        fatal_after_499_ok ? "true" : "false",
        counter_after_500th_ok,
        fatal_after_500th_ok ? "true" : "false",
        pass ? "true" : "false");

    return pass ? EXIT_SUCCESS : EXIT_FAILURE;
}
