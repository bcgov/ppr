<template>
  <div id="expiry-date-time-container">
    <h2>
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${content.title}` }}
    </h2>
    <p class="mt-2">
      {{ content.description }}
    </p>
    <v-card
      id="expiry-date-time-card"
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
          <p
            v-if="hideContinuedExpiryDate"
            class="mb-6"
          >
            Date in the Future
          </p>
          <v-radio-group
            v-else
            v-model="expiryDateType"
            class="pt-0 mt-0"
          >
            <v-radio
              :value="EffectiveDateTypes.CONTINUED"
              label="Continued until further order of the court"
              data-test-id="continued-date-radio"
            />
            <v-radio
              :value="EffectiveDateTypes.FUTURE"
              label="Date in the future"
              data-test-id="future-date-radio"
            />
          </v-radio-group>
          <InputFieldDatePicker
            id="expiry-date-picker"
            ref="expiryDatePicker"
            title="Date"
            :class="{ 'ml-8' : !hideContinuedExpiryDate }"
            :initial-value="selectedFutureDate"
            :disable-picker="isContinuedDateSelected && !hideContinuedExpiryDate"
            :input-rules="required('This field is required')"
            :min-date="minDate"
            @emit-date="selectedFutureDate = $event"
            @emit-cancel="selectedFutureDate = ''"
            @emit-clear="selectedFutureDate = ''"
          />
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { EffectiveDateTypes } from '@/enums/'
import { createDateFromPacificTime, localTodayDate } from '@/utils'
import type { ContentIF, FormIF } from '@/interfaces'
import { useInputRules } from '@/composables'
import InputFieldDatePicker from '@/components/common/InputFieldDatePicker.vue'

export default defineComponent({
  name: 'ExpiryDate',
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
    },
    hideContinuedExpiryDate: {
      type: Boolean,
      default: false
    }
  },
  emits: ['isValid', 'setStoreProperty'],
  setup (props, { emit }) {
    const { required } = useInputRules()

    const expiryDatePicker = ref(null) as FormIF
    const date = new Date()

    const localState = reactive({
      selectedFutureDate: '', // date selected from the Date Picker

      expiryDateType: props.hideContinuedExpiryDate ? EffectiveDateTypes.FUTURE : EffectiveDateTypes.CONTINUED,
      expiryDateTime: '',

      minDate: computed((): string => localTodayDate(new Date(date.setDate(date.getDate() + 1)))),
      isContinuedDateSelected: computed((): boolean => localState.expiryDateType === EffectiveDateTypes.CONTINUED),
      isExpiryDateValid: computed(
        (): boolean =>
          localState.isContinuedDateSelected || (!localState.isContinuedDateSelected && !!localState.selectedFutureDate)
      ),
      showBorderError: computed(
        (): boolean => props.validate && !localState.isContinuedDateSelected && localState.selectedFutureDate === ''
      )
    })

    // build a full UTC date based on selected future date
    const buildFullDate = (): Date => {
      const YearMonthDay = localState.selectedFutureDate.split('-')
      const year = parseInt(YearMonthDay[0])
      const month = parseInt(YearMonthDay[1]) - 1
      const day = parseInt(YearMonthDay[2])
      return createDateFromPacificTime(year, month, day)
    }

    watch(
      () => props.validate,
      async val => {
        if (val && !localState.isContinuedDateSelected) {
          expiryDatePicker.value?.validate()
        }
      }
    )

    watch(
      () => [localState.expiryDateType],
      () => {
        if (localState.isContinuedDateSelected) {
          // Continued Expiry Date is optional
          localState.expiryDateTime = ''
        } else if (props.validate) {
          expiryDatePicker.value?.validate()
        } else if (localState.selectedFutureDate !== '') {
          // future date radio selected
          localState.expiryDateTime = buildFullDate().toISOString()
        }
      }
    )

    watch(
      () => [localState.selectedFutureDate],
      () => {
        if (localState.selectedFutureDate !== '') {
          localState.expiryDateTime = buildFullDate().toISOString()
        }
      }
    )

    watch(
      () => localState.expiryDateTime,
      val => {
        emit('setStoreProperty', val)
      }
    )

    watch(
      () => localState.isExpiryDateValid,
      (val: boolean) => {
        emit('isValid', val)
      },
      { immediate: true }
    )

    return {
      required,
      expiryDatePicker,
      EffectiveDateTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.time-picker {
  display: flex;
  gap: 5px;
  justify-content: space-between;
  align-content: center;
  max-width: 600px;
  .v-select {
    max-width: 148px;
  }

  .time-separator {
    margin-right: 2px;
  }

  .period-selector:deep(.v-input__slot) {
    height: 58px;
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
