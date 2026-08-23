#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

typedef enum { SEND_UNLOCK, WAIT_UNLOCK_ACK, NEXT_STATE } State;
typedef enum { NO_RESPONSE, SUCCESS, ERROR_RESPONSE } Response;

typedef struct {
    State state;
    uint8_t reception_tries;
    unsigned sends;
} Driver;

static void step(Driver *d, Response response) {
    if (d->state == SEND_UNLOCK) {
        d->sends++;
        d->state = WAIT_UNLOCK_ACK;
    } else if (d->state == WAIT_UNLOCK_ACK) {
        if (response == SUCCESS) {
            d->reception_tries = 0u;
            d->state = NEXT_STATE;
        } else if (response == ERROR_RESPONSE) {
            d->reception_tries = 0u;
            d->state = SEND_UNLOCK;
        } else {
            d->reception_tries++;
            /* Exact selected source branch has no threshold action here. */
        }
    }
}

int main(void) {
    Driver lost = {SEND_UNLOCK, 0u, 0u};
    step(&lost, NO_RESPONSE);
    for (unsigned i = 0; i < 300u; ++i) step(&lost, NO_RESPONSE);
    bool lost_stalls = lost.state == WAIT_UNLOCK_ACK && lost.sends == 1u;

    Driver success = {SEND_UNLOCK, 0u, 0u};
    step(&success, NO_RESPONSE);
    step(&success, SUCCESS);
    bool success_progresses = success.state == NEXT_STATE;
    bool pass = lost_stalls && success_progresses;
    printf("{\"pass\":%s,\"no_response_300_cycles_stays_waiting\":%s,\"no_retry_transmission\":%s,\"success_response_progresses\":%s,\"tries_after_uint8_wrap\":%u}\n",
        pass ? "true" : "false", lost_stalls ? "true" : "false",
        lost.sends == 1u ? "true" : "false", success_progresses ? "true" : "false",
        (unsigned)lost.reception_tries);
    return pass ? 0 : 1;
}
