<template>
  <div id="staff-payment-container">
    <v-row noGutters>
      <v-col
        v-if="displaySideLabel"
        cols="12"
        sm="3"
        class="pr-4 pb-4"
      >
        <label
          class="generic-label"
          :class="{'error-text': invalidSection}"
        >Payment</label>
      </v-col>

      <v-col
        cols="12"
        :sm="displaySideLabel ? 9 : 12"
      >
        <v-radio-group
          v-model="staffPaymentData.option"
          class="payment-group"
        >
          <!-- Cash or Cheque radio button and form -->
          <v-radio
            id="fas-radio"
            class="mb-0"
            label="Cash or Cheque"
            :value="StaffPaymentOptions.FAS"
          />
          <v-form
            ref="fasForm"
            v-model="fasFormValid"
            class="mt-4 ml-8"
          >
            <v-text-field
              id="routing-slip-number-textfield"
              v-model="staffPaymentData.routingSlipNumber"
              variant="filled"
              color="primary"
              label="Routing Slip Number"
              :rules="routingSlipNumberRules"
              :disabled="staffPaymentData.option === StaffPaymentOptions.BCOL ||
                staffPaymentData.option === StaffPaymentOptions.NO_FEE"
              @focus="staffPaymentData.option = StaffPaymentOptions.FAS"
            />
          </v-form>

          <!-- BC Online radio button and form -->
          <v-radio
            id="bcol-radio"
            class="mb-0 pt-2"
            label="BC Online"
            :value="StaffPaymentOptions.BCOL"
          />
          <v-form
            ref="bcolForm"
            v-model="bcolFormValid"
            class="mt-4 ml-8"
          >
            <v-text-field
              id="bcol-account-number-textfield"
              v-model="staffPaymentData.bcolAccountNumber"
              class="pb-2"
              variant="filled"
              color="primary"
              label="BC Online Account Number"
              :rules="bcolAccountNumberRules"
              :disabled="staffPaymentData.option === StaffPaymentOptions.FAS
                || staffPaymentData.option === StaffPaymentOptions.NO_FEE"
              @focus="staffPaymentData.option = StaffPaymentOptions.BCOL"
            />
            <v-text-field
              id="dat-number-textfield"
              v-model="staffPaymentData.datNumber"
              class="pb-2"
              variant="filled"
              color="primary"
              label="DAT Number"
              :rules="datNumberRules"
              :disabled="staffPaymentData.option === StaffPaymentOptions.FAS
                || staffPaymentData.option === StaffPaymentOptions.NO_FEE"
              @focus="staffPaymentData.option = StaffPaymentOptions.BCOL"
            />
            <v-text-field
              id="folio-number-textfield"
              v-model="staffPaymentData.folioNumber"
              class="pb-2"
              variant="filled"
              color="primary"
              label="Folio Number (Optional)"
              :disabled="staffPaymentData.option === StaffPaymentOptions.FAS
                || staffPaymentData.option === StaffPaymentOptions.NO_FEE"
              @focus="staffPaymentData.option = StaffPaymentOptions.BCOL"
            />
          </v-form>

          <!-- No Fee radio button -->
          <v-radio
            id="no-fee-radio"
            class="mb-0 pt-2"
            label="No Fee"
            :value="StaffPaymentOptions.NO_FEE"
          />
        </v-radio-group>
        <template v-if="displayPriorityCheckbox">
          <v-divider class="mt-6" />

          <!-- Priority checkbox -->
          <v-checkbox
            id="priority-checkbox"
            v-model="staffPaymentData.isPriority"
            class="priority-checkbox mt-6 pt-0"
            label="Priority (add $100.00)"
            hideDetails
            :disabled="staffPaymentData.option === StaffPaymentOptions.NO_FEE"
          />
        </template>
        <!-- Useful for additional checkboxes or information -->
        <slot name="bottom-slot" />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from 'vue'
import { StaffPaymentOptions } from '@/enums'
import { FormIF, StaffPaymentIF } from '@/interfaces'
import { ValidationRule } from '@/shims-vue'

export default defineComponent({
  name: 'StaffPayment',
  components: {},
  props: {
    displaySideLabel: { type: Boolean, default: true },
    displayPriorityCheckbox: { type: Boolean, default: true },
    validate: { type: Boolean, default: false },
    invalidSection: { type: Boolean, default: false },
    staffPaymentDataProps: {
      type: Object,
      default: () => {
        return {
          option: StaffPaymentOptions.NONE,
          routingSlipNumber: '',
          bcolAccountNumber: '',
          datNumber: '',
          folioNumber: '',
          isPriority: false
        }
      }
    }
  },
  emits: ['valid', 'update:staffPaymentData'],
  setup (props, context) {
    const fasForm = ref(null) as FormIF
    const bcolForm = ref(null) as FormIF

    const localState = reactive({
      staffPaymentData: { ...props.staffPaymentDataProps } as StaffPaymentIF,
      fasFormValid: false,
      bcolFormValid: false,
      isValid: computed((): boolean => {
        return localState.staffPaymentData.option !== StaffPaymentOptions.NONE &&
            (localState.fasFormValid || localState.bcolFormValid ||
            (localState.staffPaymentData.option === StaffPaymentOptions.NO_FEE))
      }),
      /** Validation rules for Routing Slip Number. */
      routingSlipNumberRules: computed((): Array<ValidationRule> => {
        return [
          v => !!v || 'Enter FAS Routing Slip Number',
          v => /^\d{9}$/.test(v) || 'Routing Slip Number must be 9 digits'
        ]
      }),
      /** Validation rules for BCOL Number. */
      bcolAccountNumberRules: computed((): Array<ValidationRule> => {
        return [
          v => !!v || 'Enter BC Online Account Number',
          v => /^\d{6}$/.test(v) || 'BC Online Account Number must be 6 digits'
        ]
      }),
      /** Validation rules for DAT Number. */
      datNumberRules: computed((): Array<ValidationRule> => {
        return [
          v => !!v || 'Enter DAT Number',
          v => /^[A-Z]{1}[0-9]{7,9}$/.test(v) || 'DAT Number must be in standard format (eg, C1234567)'
        ]
      })
    })

    /** Validate Payment Type Forms **/
    const validatePaymentType = (): void => {
      if (props.validate){
        localState.staffPaymentData.option === StaffPaymentOptions.FAS && fasForm.value.validate()
        localState.staffPaymentData.option === StaffPaymentOptions.BCOL && bcolForm.value.validate()
      }
    }

    /** Clear inputs and reset form validations **/
    const clearInputs = (option: StaffPaymentOptions) => {
      fasForm.value.resetValidation()
      bcolForm.value.resetValidation()
      switch (option) {
        case StaffPaymentOptions.FAS:
          localState.staffPaymentData.bcolAccountNumber = ''
          localState.staffPaymentData.datNumber = ''
          localState.staffPaymentData.folioNumber = ''
          break
        case StaffPaymentOptions.BCOL:
          localState.staffPaymentData.routingSlipNumber = ''
          break
        default:
          localState.staffPaymentData.bcolAccountNumber = ''
          localState.staffPaymentData.datNumber = ''
          localState.staffPaymentData.folioNumber = ''
          localState.staffPaymentData.routingSlipNumber = ''
          break
      }
    }

    watch(() => localState.staffPaymentData, (data: StaffPaymentIF) => {
      context.emit('update:staffPaymentData', data)
    }, { deep: true })

    /** Called when payment option (radio group item) has changed. */
    watch(() => localState.staffPaymentData.option, async (option: StaffPaymentOptions): Promise<void> => {
      await nextTick()
      clearInputs(option)
      validatePaymentType()
    })

    /** Watches for changes to Staff Payment Data Validation flag. */
    watch(() => localState.isValid, async (isValid: boolean): Promise<void> => {
      context.emit('valid', isValid)
    })

    /** Watches validation prop **/
    watch(() => props.validate, async () => {
      validatePaymentType()
    })

    return {
      fasForm,
      bcolForm,
      StaffPaymentOptions,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
