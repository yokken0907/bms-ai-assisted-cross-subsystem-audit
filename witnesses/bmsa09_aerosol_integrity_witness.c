#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint16_t concentration;
    uint8_t status;
    uint8_t faults;
    uint8_t rolling_counter;
    uint8_t crc;
} Frame;

typedef struct {
    uint16_t concentration;
    uint8_t status;
    uint8_t faults;
    uint8_t stored_crc;
    unsigned writes;
} Database;

/* Mirrors the source callback's relevant acceptance semantics: the rolling
 * counter is not extracted and the CRC field is stored, not used as a gate. */
static bool source_callback_model(Database *db, Frame f) {
    (void)f.rolling_counter;
    if (f.status > 1u || f.faults > 3u) return false;
    db->concentration = f.concentration;
    db->status = f.status;
    db->faults = f.faults;
    db->stored_crc = f.crc;
    db->writes++;
    return true;
}

int main(void) {
    Database db = {0};
    Frame frames[3] = {
        {120u, 0u, 0u, 3u, 0x42u},
        {120u, 0u, 0u, 3u, 0x00u},
        {120u, 0u, 0u, 7u, 0xffu},
    };
    bool accepted[3];
    for (unsigned i = 0; i < 3u; ++i) accepted[i] = source_callback_model(&db, frames[i]);
    bool pass = accepted[0] && accepted[1] && accepted[2] && db.writes == 3u && db.stored_crc == 0xffu;
    printf("{\"pass\":%s,\"all_three_frames_written\":%s,\"repeated_counter_accepted\":%s,\"skipped_counter_accepted\":%s,\"arbitrary_crc_values_accepted_as_data\":%s,\"writes\":%u}\n",
        pass ? "true" : "false", db.writes == 3u ? "true" : "false",
        accepted[1] ? "true" : "false", accepted[2] ? "true" : "false",
        db.stored_crc == 0xffu ? "true" : "false", db.writes);
    return pass ? 0 : 1;
}
