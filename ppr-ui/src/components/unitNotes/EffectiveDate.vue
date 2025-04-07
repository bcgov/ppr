<template>
  <div id="effective-date-container">
    <h2>
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${content.title}` }}
    </h2>
    <p class="mt-2">
      {{ content.description }}
    </p>
    <v-card
      id="effective-date-card"
      class="mt-8 px-7 pt-10 pb-3"
      :class="{ 'border-error-left': showBorderError }"
      flat
    >
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
        >
          <label
            class="generic-label"
            :class="{ 'error-text': showBorderError }"
          >
            {{ content.sideLabel }}
          </label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="px-1"
        >
          <v-radio-group
            v-model="effectiveDateType"
            class="pt-0 mt-0"
          >
            <v-radio
              :value="EffectiveDateTypes.IMMEDIATE"
              label="Immediate (date of registration)"
              data-test-id="immediate-date-radio"
            />
            <v-radio
              :value="EffectiveDateTypes.PAST"
              label="Date in the past"
              data-test-id="past-date-radio"
            />
          </v-radio-group>
          <v-form
            ref="effectiveDateForm"
            v-model="isEffectiveDateFormValid"
            class="date-selector"
          >
            <InputFieldDatePicker
              id="effective-date-picker"
              ref="effectiveDatePicker"
              title="Date"
              :initial-value="selectedPastDate"
              :disable-picker="isImmediateDateSelected"
              :input-rules="required('This field is required')"
              :max-date="maxDate"
              @emit-date="selectedPastDate = $event"
              @emit-cancel="selectedPastDate = ''"
              @emit-clear="selectedPastDate = ''"
            />
          </v-form>

          <p
            v-if="!isImmediateDateSelected && selectedPastDate"
            class="ml-8 mb-6"
            data-test-id="date-summary-label"
          >
            {{ content.dateSummaryLabel }} <br>
            <b>
              {{ shortPacificDate(effectiveDate) }}
            </b>
          </p>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { EffectiveDateTypes } from '@/enums/'
import { createDateFromPacificTime, localTodayDate, shortPacificDate } from '@/utils'
import type { ContentIF, FormIF } from '@/interfaces'
import { useInputRules } from '@/composables'
import InputFieldDatePicker from '@/components/common/InputFieldDatePicker.vue'

export default defineComponent({
  name: 'EffectiveDate',
  components: {
    InputFieldDatePicker
  },
  props: {
    validate: {
      type: Boolean,
      default: false
    },
    sectionNumber: {
      type: Number,
      default: null
    },
    content: {
      type: Object as () => ContentIF,
      default: () => {}
    }
  },
  emits: ['isValid', 'setStoreProperty'],
  setup (props, { emit }) {
    const { required } = useInputRules()

    const effectiveDatePicker = ref(null) as FormIF
    const effectiveDateForm = ref(null) as FormIF

    const date = new Date()

    const localState = reactive({
      isEffectiveDateFormValid: true,
      selectedPastDate: '', // date selected from the Date Picker

      effectiveDateType: EffectiveDateTypes.IMMEDIATE,
      effectiveDate: '',

      maxDate: computed((): string => localTodayDate(new Date(date.setDate(date.getDate() - 1)), true)),
      isImmediateDateSelected: computed((): boolean => localState.effectiveDateType === EffectiveDateTypes.IMMEDIATE),
      isEffectiveDateValid: computed((): boolean =>
        localState.isImmediateDateSelected ||
        (!localState.isImmediateDateSelected && !!localState.selectedPastDate)
      ),
      showBorderError: computed((): boolean => {
        return props.validate &&
        !localState.isImmediateDateSelected &&
        !(localState.isEffectiveDateFormValid && localState.selectedPastDate !== '')
      })

    })

    const buildFullDate = (): Date => {
      const YearMonthDay = localState.selectedPastDate.split('-')
      const year = parseInt(YearMonthDay[0])
      const month = parseInt(YearMonthDay[1]) - 1
      const day = parseInt(YearMonthDay[2])

      return createDateFromPacificTime(year, month, day)
    }

    watch(() => props.validate, async (val) => {
      if (val && !localState.isImmediateDateSelected) {
        effectiveDatePicker.value?.validate()
        effectiveDateForm.value?.validate()
      }
    })

    watch(
      () => [localState.effectiveDateType],
      () => {
        if (localState.isImmediateDateSelected) {
          // Let the API set the effective date
          localState.effectiveDate = ''
        } else if (props.validate) {
          effectiveDatePicker.value?.validate()
          effectiveDateForm.value.validate()
        } else if (localState.selectedPastDate) {
          // past date radio selected
          localState.effectiveDate = buildFullDate().toISOString()
        }
      }
    )

    watch(
      () => localState.selectedPastDate,
      () => {
        if (localState.selectedPastDate) {
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

    watch(() => localState.isEffectiveDateValid, (val: boolean) => {
      emit('isValid', val)
    }, { immediate: true })

    return {
      required,
      effectiveDatePicker,
      effectiveDateForm,
      EffectiveDateTypes,
      shortPacificDate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.v-radio {
  padding-bottom: 0.5rem;
}

.date-selector {
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
