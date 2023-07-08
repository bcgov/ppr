<template>
  <div id="effective-date-time-container">
    <h2>{{ content.title }}</h2>
    <p class="mt-2">{{ content.description }}</p>
    <v-card id="effective-date-time-card" flat rounded class="mt-8 px-7 py-10">
      <v-row no-gutters>
        <v-col cols="12" sm="3">
          <label class="generic-label" :class="{ 'error-text': false }">
            {{ content.sideLabel }}
          </label>
        </v-col>
        <v-col cols="12" sm="9" class="px-1">
          <v-radio-group v-model="effectiveDateType" column class="pt-0 mt-0">
            <v-radio
              :value="EffectiveDateTypes.IMMEDIATE"
              label="Immediate (date and time of registration)"
              data-test-id="immediate-date-radio"
            />
            <v-radio
              :value="EffectiveDateTypes.PAST"
              label="Date and time in the past"
              data-test-id="past-date-radio"
            />
          </v-radio-group>
          <v-form ref="effectiveDateTimeForm" class="date-time-selectors" v-model="isEffectiveDateTimeFormValid">
            <SharedDatePicker
              id="effective-date-picker"
              ref="effectiveDatePicker"
              title="Date"
              :initialValue="selectedPastDate"
              :disablePicker="isImmediateDateSelected"
              :inputRules="required('This field is required')"
              :maxDate="maxDate"
              @emitDate="selectedPastDate = $event"
              @emitCancel="selectedPastDate = ''"
              @emitClear="selectedPastDate = ''"
            />

            <div class="time-picker" data-test-id="time-picker-fields">
              <v-select
                id="hour-selector"
                ref="hourSelector"
                v-model="selectHour"
                filled
                class="mr-1"
                label="Hour"
                :items="hours"
                :rules="required('This field is required')"
                :disabled="isImmediateDateSelected"
              />
              <span class="px-2 pt-4" :class="{ disabled: isImmediateDateSelected }"> : </span>

              <v-select
                id="minute-selector"
                ref="minuteSelector"
                v-model="selectMinute"
                filled
                class="mr-1"
                label="Minute"
                :items="minutes"
                :rules="required('This field is required')"
                :disabled="isImmediateDateSelected"
              />

              <v-select
                id="period-selector"
                ref="periodSelector"
                v-model="selectPeriod"
                filled
                class="mr-1"
                :items="[PeriodTypes.AM, PeriodTypes.PM]"
                :disabled="isImmediateDateSelected"
              />

              <span class="timezone-label pt-4" :class="{ disabled: isImmediateDateSelected }"> Pacific time </span>
            </div>
          </v-form>

          <div
            v-if="!isImmediateDateSelected && selectedPastDate && isTimeSelected"
            class="ml-8"
            data-test-id="date-summary-label"
          >
            Caution on this home effective: <br />
            <b>
              {{ pacificDate(effectiveDate, true) }}
            </b>
          </div>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, ref, toRefs, watch } from 'vue-demi'
import { EffectiveDateTypes, PeriodTypes } from '@/enums/'
import { createUtcDate, localTodayDate, pacificDate } from '@/utils'
import { ContentIF, FormIF } from '@/interfaces'
import { useInputRules } from '@/composables'
import SharedDatePicker from '@/components/common/SharedDatePicker.vue'

export default defineComponent({
  name: 'EffectiveDateTime',
  components: {
    SharedDatePicker
  },
  props: {
    validate: {
      type: Boolean,
      default: false
    },
    content: {
      type: Object as () => ContentIF,
      default: () => {}
    }
  },
  emits: ['setStoreProperty'],
  setup (props, { emit }) {
    const { required } = useInputRules()

    const effectiveDatePicker = ref(null) as FormIF
    const effectiveDateTimeForm = ref(null) as FormIF

    const date = new Date()

    const localState = reactive({
      isEffectiveDateTimeFormValid: false,
      selectHour: null,
      selectMinute: null,
      selectPeriod: PeriodTypes.AM,
      selectedPastDate: '', // date selected from the Date Picker

      effectiveDateType: EffectiveDateTypes.IMMEDIATE,
      effectiveDate: '',

      hours: [...Array(12).keys()].map(num => (num + 1).toString()),
      minutes: [...Array(60).keys()].map(num => num.toString().padStart(2, '0')),
      maxDate: computed((): string => localTodayDate(new Date(date.setDate(date.getDate() - 1)))),
      isImmediateDateSelected: computed((): boolean => localState.effectiveDateType === EffectiveDateTypes.IMMEDIATE),
      isTimeSelected: computed((): boolean => localState.selectHour && localState.selectMinute)
    })

    const buildFullDate = (): Date => {
      let hours = parseInt(localState.selectHour)
      const minutes = parseInt(localState.selectMinute)

      // convert 12 am -> 0
      if (localState.selectPeriod === PeriodTypes.AM && localState.selectHour === 12) {
        hours = hours - 12
      }
      // convert 1-11 pm -> 13-23
      if (localState.selectPeriod === PeriodTypes.PM && localState.selectHour < 12) {
        hours = hours + 12
      }

      const date = new Date(localState.selectedPastDate)
      return createUtcDate(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), hours, minutes)
    }

    onBeforeMount((): void => {
      // set todays date as Immediate radio button is selected by default
      localState.effectiveDate = new Date().toISOString()
    })

    watch(
      () => [localState.effectiveDateType],
      () => {
        if (localState.isImmediateDateSelected) {
          // today's date radio selected
          localState.effectiveDate = new Date().toISOString()
        } else if (localState.isTimeSelected) {
          // past date radio selected and all time dropdowns are selected
          localState.effectiveDate = buildFullDate().toISOString()
        }
      }
    )

    watch(
      () => [localState.selectedPastDate, localState.selectHour, localState.selectMinute, localState.selectPeriod],
      () => {
        if (localState.isTimeSelected) {
          localState.effectiveDate = buildFullDate().toISOString()
        }
      }
    )

    watch(
      () => localState.effectiveDate,
      val => {
        emit('setStoreProperty', val)
      }
    )

    return {
      required,
      effectiveDatePicker,
      effectiveDateTimeForm,
      EffectiveDateTypes,
      PeriodTypes,
      pacificDate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.time-picker {
  display: flex;
  justify-content: space-between;
  align-content: center;
  .v-select {
    max-width: 148px;
  }

  .timezone-label {
    white-space: nowrap;
  }
}

.v-radio {
  padding-bottom: 0.5rem;
}

.date-time-selectors {
  margin-left: 2rem;
}

.disabled {
  color: $gray6;
}

.v-icon.v-icon.v-icon--disabled {
  color: $app-blue !important;
}
.v-input--is-disabled {
  opacity: 0.4;
}
</style>
