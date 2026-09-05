#include <stdint.h>
#include <stdio.h>

enum substate_e {
    NORMAL_CLOSE_SECOND_STRING_CONTACTOR = 0,
    CHECK_STRING_CLOSED = 1,
    CHECK_ERROR_FLAGS = 2
};

struct trace_s {
    enum substate_e substate;
    unsigned plus_close_requests;
    unsigned number_of_closed_strings;
    unsigned closed_next_string;
    unsigned fatal_checks;
    unsigned standby_request_checks;
};

static void audited_step(struct trace_s *s, int minus_feedback_on, int plus_feedback_on) {
    (void)plus_feedback_on;
    if (s->substate == NORMAL_CLOSE_SECOND_STRING_CONTACTOR) {
        if (minus_feedback_on) {
            s->plus_close_requests++;
            s->substate = NORMAL_CLOSE_SECOND_STRING_CONTACTOR;
        }
    } else if (s->substate == CHECK_STRING_CLOSED) {
        if (plus_feedback_on) {
            s->number_of_closed_strings++;
            s->closed_next_string = 1u;
            s->substate = CHECK_ERROR_FLAGS;
        } else {
            s->fatal_checks++;
            s->standby_request_checks++;
        }
    }
}

static void reference_step(struct trace_s *s, int minus_feedback_on, int plus_feedback_on) {
    if (s->substate == NORMAL_CLOSE_SECOND_STRING_CONTACTOR) {
        if (minus_feedback_on) {
            s->plus_close_requests++;
            s->substate = CHECK_STRING_CLOSED;
        }
    } else if (s->substate == CHECK_STRING_CLOSED) {
        if (plus_feedback_on) {
            s->number_of_closed_strings++;
            s->closed_next_string = 1u;
            s->substate = CHECK_ERROR_FLAGS;
        }
    }
}

static unsigned actual_closest(const int32_t voltage[3], const int closed[3]) {
    unsigned selected = 255u;
    const int32_t closed_voltage = voltage[0];
    for (unsigned s = 0u; s < 3u; s++) {
        if (!closed[s]) {
            int32_t minimum_difference = INT32_MAX;
            int32_t d = closed_voltage > voltage[s] ? closed_voltage - voltage[s] : voltage[s] - closed_voltage;
            if (d <= minimum_difference) {
                minimum_difference = d;
                selected = s;
            }
        }
    }
    return selected;
}

static unsigned reference_closest(const int32_t voltage[3], const int closed[3]) {
    unsigned selected = 255u;
    int32_t minimum_difference = INT32_MAX;
    const int32_t closed_voltage = voltage[0];
    for (unsigned s = 0u; s < 3u; s++) {
        if (!closed[s]) {
            int32_t d = closed_voltage > voltage[s] ? closed_voltage - voltage[s] : voltage[s] - closed_voltage;
            if (d <= minimum_difference) {
                minimum_difference = d;
                selected = s;
            }
        }
    }
    return selected;
}

int main(void) {
    struct trace_s actual = {NORMAL_CLOSE_SECOND_STRING_CONTACTOR, 0u, 1u, 0u, 0u, 0u};
    struct trace_s reference = actual;
    for (unsigned i = 0u; i < 4u; i++) {
        audited_step(&actual, 1, 1);
        reference_step(&reference, 1, 1);
    }
    printf("actual_substate=%d actual_plus_requests=%u actual_closed=%u actual_count=%u actual_fatal_checks=%u actual_request_checks=%u\n",
           actual.substate, actual.plus_close_requests, actual.closed_next_string,
           actual.number_of_closed_strings, actual.fatal_checks, actual.standby_request_checks);
    printf("reference_substate=%d reference_plus_requests=%u reference_closed=%u reference_count=%u\n",
           reference.substate, reference.plus_close_requests, reference.closed_next_string,
           reference.number_of_closed_strings);

    const int closed[3] = {1, 0, 0};
    const int32_t voltages_a[3] = {100000, 100100, 102000};
    const int32_t voltages_b[3] = {100000, 102000, 104000};
    unsigned actual_a = actual_closest(voltages_a, closed);
    unsigned reference_a = reference_closest(voltages_a, closed);
    unsigned actual_b = actual_closest(voltages_b, closed);
    unsigned reference_b = reference_closest(voltages_b, closed);
    int32_t actual_b_difference = voltages_b[actual_b] - voltages_b[0];
    int32_t reference_b_difference = voltages_b[reference_b] - voltages_b[0];
    printf("closest_a_actual=%u closest_a_reference=%u\n", actual_a, reference_a);
    printf("closest_b_actual=%u closest_b_reference=%u actual_b_difference=%d reference_b_difference=%d\n",
           actual_b, reference_b, actual_b_difference, reference_b_difference);

    if (actual.substate != NORMAL_CLOSE_SECOND_STRING_CONTACTOR || actual.plus_close_requests != 4u ||
        actual.closed_next_string != 0u || actual.number_of_closed_strings != 1u ||
        actual.fatal_checks != 0u || actual.standby_request_checks != 0u) {
        return 10;
    }
    if (reference.closed_next_string != 1u || reference.number_of_closed_strings != 2u) {
        return 20;
    }
    if (actual_a != 2u || reference_a != 1u || actual_b != 2u || reference_b != 1u ||
        actual_b_difference != 4000 || reference_b_difference != 2000) {
        return 30;
    }
    return 0;
}
