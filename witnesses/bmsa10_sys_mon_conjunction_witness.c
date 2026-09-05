#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

static bool source_violation_gate(uint32_t now, uint32_t entered, uint32_t previous_duration,
                                  uint32_t cycle, uint32_t jitter) {
    uint32_t time_since_last_call = now - entered;
    uint32_t max_allowed_jitter = cycle + jitter;
    return (time_since_last_call > max_allowed_jitter) && (previous_duration > cycle);
}

int main(void) {
    const uint32_t cycle = 10u;
    const uint32_t jitter = 1u;
    bool on_time_short = source_violation_gate(11u, 0u, 10u, cycle, jitter);
    bool late_short = source_violation_gate(12u, 0u, 10u, cycle, jitter);
    bool on_time_long = source_violation_gate(11u, 0u, 11u, cycle, jitter);
    bool late_long = source_violation_gate(12u, 0u, 11u, cycle, jitter);
    bool pass = !on_time_short && !late_short && !on_time_long && late_long;
    printf("{\"pass\":%s,\"on_time_short_reports\":%s,\"late_with_short_previous_duration_reports\":%s,\"on_time_with_long_duration_reports\":%s,\"late_and_long_reports\":%s}\n",
        pass ? "true" : "false", on_time_short ? "true" : "false", late_short ? "true" : "false",
        on_time_long ? "true" : "false", late_long ? "true" : "false");
    return pass ? 0 : 1;
}
