#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <math.h>

#define BS_NR_OF_STRINGS 1u
#define BS_NR_OF_MODULES_PER_STRING 1u
#define BS_NR_OF_TEMP_SENSORS_PER_MODULE 1u
#define LTC_N_LTC 1u
#define NULL_PTR ((void *)0)
#define FAS_TRAP 0
#define FAS_ASSERT(x) assert(x)

#define TSI_MINIMUM_TEMP_MEASUREMENT_RANGE_ddegC (-500)
#define TSI_MAXIMUM_TEMP_MEASUREMENT_RANGE_ddegC (1250)

typedef float float_t;
typedef enum { STD_OK = 0, STD_NOT_OK = 1 } STD_RETURN_TYPE_e;

enum {
    DIAG_ID_AFE_CELL_TEMPERATURE_MEAS_ERROR = 101,
    DIAG_ID_AFE_SPI = 201,
    DIAG_ID_AFE_COMMUNICATION_INTEGRITY = 202,
    DIAG_ID_AFE_MUX = 203,
    DIAG_ID_AFE_CONFIG = 204,
    DIAG_STRING = 1
};

typedef struct {
    uint8_t muxID;
    uint8_t muxCh;
} LTC_MUX_CH_CFG_s;

typedef struct {
    bool PEC_valid[BS_NR_OF_STRINGS][LTC_N_LTC];
} LTC_ERRORTABLE_s;

typedef struct {
    uint8_t state;
    int16_t cellTemperature_ddegC[BS_NR_OF_STRINGS][BS_NR_OF_MODULES_PER_STRING][BS_NR_OF_TEMP_SENSORS_PER_MODULE];
    bool invalidCellTemperature[BS_NR_OF_STRINGS][BS_NR_OF_MODULES_PER_STRING][BS_NR_OF_TEMP_SENSORS_PER_MODULE];
    uint16_t nrValidTemperatures[BS_NR_OF_STRINGS];
} DATA_BLOCK_CELL_TEMPERATURE_s;

typedef struct {
    LTC_ERRORTABLE_s *errorTable;
    DATA_BLOCK_CELL_TEMPERATURE_s *cellTemperature;
} LTC_DATA_MIN_s;

typedef struct {
    LTC_DATA_MIN_s ltcData;
    int tempMeasDiagErrorEntry;
} LTC_STATE_s;

static const uint8_t ltc_muxSensorTemperature_cfg[BS_NR_OF_TEMP_SENSORS_PER_MODULE] = {0u};

static unsigned g_diag_calls = 0;
static unsigned g_fatal_diag_calls = 0;
static unsigned g_db_writes = 0;
static STD_RETURN_TYPE_e g_last_diag_event = STD_OK;
static int g_last_diag_id = -1;

static STD_RETURN_TYPE_e DIAG_CheckEvent(STD_RETURN_TYPE_e event, int id, int scope, uint8_t stringNumber) {
    (void)scope;
    (void)stringNumber;
    g_diag_calls++;
    g_last_diag_event = event;
    g_last_diag_id = id;
    if (id == DIAG_ID_AFE_SPI || id == DIAG_ID_AFE_COMMUNICATION_INTEGRITY ||
        id == DIAG_ID_AFE_MUX || id == DIAG_ID_AFE_CONFIG) {
        g_fatal_diag_calls++;
    }
    return STD_OK;
}

#define DATA_WRITE_DATA(x) do { (void)(x); g_db_writes++; } while (0)

extern int16_t TS_Epc00GetTemperatureFromPolynomial(uint16_t adcVoltage_mV) {
    /* AXIVION Routine Generic-MissingParameterAssert: adcVoltage_mV: parameter accepts whole range */
    /* cspell:ignore vadc */
    float_t temperature_degC = 0.0f;
    float_t vadc_V           = adcVoltage_mV / 1000.0;
    float_t vadc2            = vadc_V * vadc_V;
    float_t vadc3            = vadc2 * vadc_V;
    float_t vadc4            = vadc3 * vadc_V;
    float_t vadc5            = vadc4 * vadc_V;
    float_t vadc6            = vadc5 * vadc_V;

    temperature_degC = (6.8405f * vadc6) - (74.815f * vadc5) + (317.48f * vadc4) - (669.16f * vadc3) +
                       (740.82f * vadc2) - (444.97f * vadc_V) + 166.48f;

    return (int16_t)(temperature_degC * 10.0f); /* Convert deg into deci &deg;C */
}

extern int16_t TSI_GetTemperature(uint16_t adcVoltage_mV) {
    return TS_Epc00GetTemperatureFromPolynomial(adcVoltage_mV);
}

int16_t LTC_ConvertMuxVoltagesToTemperatures(uint16_t adcVoltage_mV) {
    return TSI_GetTemperature(adcVoltage_mV); /* Convert degree Celsius to deci degree Celsius */
}

extern int16_t TSI_GetMaximumPlausibleTemperature(void) {
    return TSI_MAXIMUM_TEMP_MEASUREMENT_RANGE_ddegC;
}

extern int16_t TSI_GetMinimumPlausibleTemperature(void) {
    return TSI_MINIMUM_TEMP_MEASUREMENT_RANGE_ddegC;
}

extern STD_RETURN_TYPE_e AFE_PlausibilityCheckTempMinMax(const int16_t cellTemperature_ddegC) {
    STD_RETURN_TYPE_e retval = STD_OK;

    const int16_t plausibleMaximumTemperature_ddegC = TSI_GetMaximumPlausibleTemperature();
    const int16_t plausibleMinimumTemperature_ddegC = TSI_GetMinimumPlausibleTemperature();

    /* General plausibility check: Maximum temperature may not be smaller than minimum */
    FAS_ASSERT(plausibleMaximumTemperature_ddegC >= plausibleMinimumTemperature_ddegC);

    if ((cellTemperature_ddegC > plausibleMaximumTemperature_ddegC) ||
        (cellTemperature_ddegC < plausibleMinimumTemperature_ddegC)) {
        /* Cell voltage measurement value out of measurement range */
        retval = STD_NOT_OK;
    }
    return retval;
}

static void LTC_SaveMuxMeasurement(
    LTC_STATE_s *ltc_state,
    uint16_t *pRxBuff,
    LTC_MUX_CH_CFG_s *muxseqptr,
    uint8_t stringNumber) {
    FAS_ASSERT(ltc_state != NULL_PTR);
    FAS_ASSERT(pRxBuff != NULL_PTR);
    FAS_ASSERT(muxseqptr != NULL_PTR);
    uint16_t val_ui           = 0;
    int16_t temperature_ddegC = 0;
    uint8_t sensor_idx        = 0;
    uint8_t ch_idx            = 0;
    uint16_t buffer_LSB       = 0;
    uint16_t buffer_MSB       = 0;

    /* pointer to measurement Sequence of Mux- and Channel-Configurations (1,0xFF)...(3,0xFF),(0,1),...(0,7)) */
    /* Channel 0xFF means that the multiplexer is deactivated, therefore no measurement will be made and saved*/
    if (muxseqptr->muxCh != 0xFF) {
        /* user multiplexer type -> connected to GPIO2! */
        if ((muxseqptr->muxID == 1) || (muxseqptr->muxID == 2)) {
            for (uint16_t i = 0; i < LTC_N_LTC; i++) {
                if (muxseqptr->muxID == 1) {
                    ch_idx = 0 + muxseqptr->muxCh; /* channel index 0..7 */
                } else {
                    ch_idx = 8 + muxseqptr->muxCh; /* channel index 8..15 */
                }

                if (ch_idx < (2u * 8u)) {
                    val_ui = *((uint16_t *)(&pRxBuff[6u + (1u * i * 8u)])); /* raw values, all mux on all LTCs */
                    /* ltc_user_mux.value[i*8*2+ch_idx] = (uint16_t)(((float_t)(val_ui))*100e-6f*1000.0f); */ /* Unit ->
                                                                                                                 in V ->
                                                                                                                 in mV
                                                                                                               */
                }
            }
        } else {
            /* temperature multiplexer type -> connected to GPIO1! */
            for (uint16_t i = 0; i < LTC_N_LTC; i++) {
                buffer_MSB = pRxBuff[4u + (i * 8u) + 1u];
                buffer_LSB = pRxBuff[4u + (i * 8u)];
                val_ui     = buffer_LSB | (buffer_MSB << 8);
                /* val_ui = *((uint16_t *)(&pRxBuff[4+i*8])); */
                /* GPIO voltage in 100uV -> * 0.1 ----  conversion to mV */
                temperature_ddegC = LTC_ConvertMuxVoltagesToTemperatures(val_ui / 10u); /* unit: deci &deg;C */
                sensor_idx        = ltc_muxSensorTemperature_cfg[muxseqptr->muxCh];
                /* wrong configuration! */
                if (sensor_idx >= BS_NR_OF_TEMP_SENSORS_PER_MODULE) {
                    FAS_ASSERT(FAS_TRAP);
                }
                /* Set bitmask for valid flags */

                /* Check LTC PEC error */
                if (ltc_state->ltcData.errorTable->PEC_valid[stringNumber][i] == true) {
                    /* Reset invalid flag */
                    ltc_state->ltcData.cellTemperature->invalidCellTemperature[stringNumber][i][sensor_idx] = false;

                    ltc_state->ltcData.cellTemperature->cellTemperature_ddegC[stringNumber][i][sensor_idx] =
                        temperature_ddegC;
                } else {
                    /* Set invalid flag */
                    ltc_state->ltcData.cellTemperature->invalidCellTemperature[stringNumber][i][sensor_idx] = true;
                }
            }
        }
    }
}

extern void LTC_SaveTemperatures(LTC_STATE_s *ltc_state, uint8_t stringNumber) {
    FAS_ASSERT(ltc_state != NULL_PTR);
    STD_RETURN_TYPE_e cellTemperatureMeasurementValid = STD_OK;
    uint16_t numberValidMeasurements                  = 0;

    for (uint8_t m = 0u; m < BS_NR_OF_MODULES_PER_STRING; m++) {
        for (uint8_t ts = 0u; ts < BS_NR_OF_TEMP_SENSORS_PER_MODULE; ts++) {
            /* ------- 1. Check valid flag  -----------------
             * Is cell temperature valid because of previous PEC error
             * If so, everything okay, else set cell temperature measurement to invalid.
             */
            if (ltc_state->ltcData.cellTemperature->invalidCellTemperature[stringNumber][m][ts] == false) {
                /* Cell temperature is valid -> perform minimum/maximum plausibility check */

                /* ------- 2. Perform minimum/maximum measurement range check ---------- */
                if (STD_OK == AFE_PlausibilityCheckTempMinMax(
                                  ltc_state->ltcData.cellTemperature->cellTemperature_ddegC[stringNumber][m][ts])) {
                    numberValidMeasurements++;
                } else {
                    /* Invalidate cell temperature measurement */
                    ltc_state->ltcData.cellTemperature->invalidCellTemperature[stringNumber][m][ts] = true;
                    cellTemperatureMeasurementValid                                                 = STD_NOT_OK;
                }
            } else {
                /* Already invalid because of PEC Error */
                cellTemperatureMeasurementValid = STD_NOT_OK;
            }
        }
    }
    DIAG_CheckEvent(cellTemperatureMeasurementValid, ltc_state->tempMeasDiagErrorEntry, DIAG_STRING, stringNumber);

    ltc_state->ltcData.cellTemperature->nrValidTemperatures[stringNumber] = numberValidMeasurements;

    ltc_state->ltcData.cellTemperature->state++;
    DATA_WRITE_DATA(ltc_state->ltcData.cellTemperature);
}

int main(void) {
    DATA_BLOCK_CELL_TEMPERATURE_s block = {0};
    LTC_ERRORTABLE_s errors = {0};
    LTC_STATE_s state = {0};
    LTC_MUX_CH_CFG_s mux = {.muxID = 0u, .muxCh = 0u};
    uint16_t rx[12] = {0};

    state.ltcData.cellTemperature = &block;
    state.ltcData.errorTable = &errors;
    state.tempMeasDiagErrorEntry = DIAG_ID_AFE_CELL_TEMPERATURE_MEAS_ERROR;

    errors.PEC_valid[0][0] = true;
    block.invalidCellTemperature[0][0][0] = true;
    block.nrValidTemperatures[0] = 999u;
    block.state = 7u;

    /* Preregistered RDAUXA GPIO1 raw word 0x0000: rx[4]=LSB=0, rx[5]=MSB=0. */
    rx[4] = 0u;
    rx[5] = 0u;

    LTC_SaveMuxMeasurement(&state, rx, &mux, 0u);

    if (block.invalidCellTemperature[0][0][0] != false) return 21;
    if (block.cellTemperature_ddegC[0][0][0] <= TSI_MAXIMUM_TEMP_MEASUREMENT_RANGE_ddegC) return 22;
    if (AFE_PlausibilityCheckTempMinMax(block.cellTemperature_ddegC[0][0][0]) != STD_NOT_OK) return 23;
    if (g_diag_calls != 0u || g_fatal_diag_calls != 0u) return 24;

    LTC_SaveTemperatures(&state, 0u);

    if (block.invalidCellTemperature[0][0][0] != true) return 25;
    if (block.nrValidTemperatures[0] != 0u) return 26;
    if (block.state != 8u) return 27;
    if (g_diag_calls != 1u) return 28;
    if (g_last_diag_event != STD_NOT_OK) return 29;
    if (g_last_diag_id != DIAG_ID_AFE_CELL_TEMPERATURE_MEAS_ERROR) return 30;
    if (g_fatal_diag_calls != 0u) return 31;
    if (g_db_writes != 1u) return 32;

    printf("RAW_ADC_MV=0\n");
    printf("CONVERTED_TEMPERATURE_DDEGC=%d\n", block.cellTemperature_ddegC[0][0][0]);
    printf("BMSA06_PHASE5_RUN02R2_EXACT_ACQUISITION_BRIDGE_PASS\n");
    return 0;
}
