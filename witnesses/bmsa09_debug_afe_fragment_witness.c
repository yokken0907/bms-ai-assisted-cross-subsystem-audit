#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CELLS 18u
#define TEMPS 8u
#define V_PER_FRAME 4u
#define T_PER_FRAME 6u
#define TIMEOUT_MS 250u

typedef struct {
    int16_t cell[CELLS];
    int16_t temp[TEMPS];
    bool cell_invalid[CELLS];
    bool temp_invalid[TEMPS];
    uint32_t cell_header_timestamp;
    uint32_t temp_header_timestamp;
} Aggregate;

static void receive_voltage_fragment(Aggregate *a, unsigned mux, int16_t base, uint32_t now) {
    unsigned first = mux * V_PER_FRAME;
    for (unsigned i = 0; i < V_PER_FRAME && first + i < CELLS; ++i) {
        a->cell[first + i] = (int16_t)(base + (int16_t)i);
        a->cell_invalid[first + i] = false;
    }
    a->cell_header_timestamp = now;
}

static void receive_temperature_fragment(Aggregate *a, unsigned mux, int16_t base, uint32_t now) {
    unsigned first = mux * T_PER_FRAME;
    for (unsigned i = 0; i < T_PER_FRAME && first + i < TEMPS; ++i) {
        a->temp[first + i] = (int16_t)(base + (int16_t)i);
        a->temp_invalid[first + i] = false;
    }
    a->temp_header_timestamp = now;
}

static bool table_fresh(uint32_t now, uint32_t timestamp) {
    return (now - timestamp) <= TIMEOUT_MS;
}

int main(void) {
    Aggregate raw;
    Aggregate validated;
    memset(&raw, 0, sizeof(raw));
    memset(&validated, 0, sizeof(validated));
    for (unsigned i = 0; i < CELLS; ++i) raw.cell_invalid[i] = true;
    for (unsigned i = 0; i < TEMPS; ++i) raw.temp_invalid[i] = true;

    for (unsigned mux = 0; mux < 5u; ++mux) receive_voltage_fragment(&raw, mux, (int16_t)(3000 + mux * 10u), 100u + mux);
    for (unsigned mux = 0; mux < 2u; ++mux) receive_temperature_fragment(&raw, mux, (int16_t)(200 + mux * 10u), 110u + mux);
    validated = raw;
    const int16_t old_cell_16 = raw.cell[16];
    const int16_t old_cell_17 = raw.cell[17];
    const int16_t old_temp_6 = raw.temp[6];
    const int16_t old_temp_7 = raw.temp[7];

    for (uint32_t now = 1000u; now <= 1400u; now += 100u) {
        receive_voltage_fragment(&raw, 0u, (int16_t)(4000 + (int16_t)now), now);
        receive_temperature_fragment(&raw, 0u, (int16_t)(500 + (int16_t)(now / 10u)), now);
        if (table_fresh(now, raw.cell_header_timestamp) && table_fresh(now, raw.temp_header_timestamp)) {
            validated = raw;
        }
    }

    bool stale_cells_valid = !validated.cell_invalid[16] && !validated.cell_invalid[17] &&
        validated.cell[16] == old_cell_16 && validated.cell[17] == old_cell_17;
    bool stale_temps_valid = !validated.temp_invalid[6] && !validated.temp_invalid[7] &&
        validated.temp[6] == old_temp_6 && validated.temp[7] == old_temp_7;
    bool headers_fresh = table_fresh(1400u, raw.cell_header_timestamp) && table_fresh(1400u, raw.temp_header_timestamp);
    bool pass = stale_cells_valid && stale_temps_valid && headers_fresh;
    printf("{\"pass\":%s,\"cells_16_17_remain_old_and_valid\":%s,\"temps_6_7_remain_old_and_valid\":%s,\"aggregate_headers_fresh\":%s,\"voltage_fragments_required\":5,\"temperature_fragments_required\":2}\n",
        pass ? "true" : "false", stale_cells_valid ? "true" : "false",
        stale_temps_valid ? "true" : "false", headers_fresh ? "true" : "false");
    return pass ? 0 : 1;
}
