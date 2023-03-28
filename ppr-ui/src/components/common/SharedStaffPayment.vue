<template>
  <div id="staff-payment-container">
    <v-row no-gutters>
      <v-col v-if="displaySideLabel" cols="12" sm="3" class="pr-4 pb-4">
        <label class="title-label" :class="{'error-text': invalidSection}">Payment</label>
      </v-col>

      <v-col cols="12" :sm="displaySideLabel ? 9 : 12">
        <v-radio-group class="payment-group" v-model="paymentOption">
          <!-- Cash or Cheque radio button and form -->
          <v-radio id="fas-radio" class="mb-0" label="Cash or Cheque" :value="StaffPaymentOptions.FAS" />
          <v-form class="mt-4 ml-8" ref="fasForm" v-model="fasFormValid">
            <v-text-field
              filled
              id="routing-slip-number-textfield"
              label="Routing Slip Number"
              :value="staffPaymentData.routingSlipNumber"
              :rules="validate ? routingSlipNumberRules : []"
              :disabled="paymentOption === StaffPaymentOptions.BCOL || paymentOption === StaffPaymentOptions.NO_FEE"
              @keyup="staffPaymentData.routingSlipNumber = staffPaymentData.routingSlipNumber.trim()"
              @focus="paymentOption = StaffPaymentOptions.FAS"
              @input="emitStaffPaymentData({ option: StaffPaymentOptions.FAS, routingSlipNumber: $event })"
            />
          </v-form>

          <!-- BC Online radio button and form -->
          <v-radio id="bcol-radio" class="mb-0 pt-2" label="BC Online" :value="StaffPaymentOptions.BCOL" />
          <v-form class="mt-4 ml-8" ref="bcolForm" v-model="bcolFormValid">
            <v-text-field
              filled
              id="bcol-account-number-textfield"
              label="BC Online Account Number"
              :value="staffPaymentData.bcolAccountNumber"
              :rules="validate ? bcolAccountNumberRules : []"
              :disabled="paymentOption === StaffPaymentOptions.FAS || paymentOption === StaffPaymentOptions.NO_FEE"
              @keyup="staffPaymentData.bcolAccountNumber = staffPaymentData.bcolAccountNumber.trim()"
              @focus="paymentOption = StaffPaymentOptions.BCOL"
              @input="emitStaffPaymentData({ option: StaffPaymentOptions.BCOL, bcolAccountNumber: $event })"
            />
            <v-text-field
              filled
              id="dat-number-textfield"
              label="DAT Number"
              :value="staffPaymentData.datNumber"
              :rules="validate ? datNumberRules : []"
              :disabled="paymentOption === StaffPaymentOptions.FAS || paymentOption === StaffPaymentOptions.NO_FEE"
              @keyup="staffPaymentData.datNumber = staffPaymentData.datNumber.trim()"
              @focus="paymentOption = StaffPaymentOptions.BCOL"
              @input="emitStaffPaymentData({ option: StaffPaymentOptions.BCOL, datNumber: $event })"
            />
            <FolioNumberInput
              ref="folioNumberInputRef"
              :folioNumber="staffPaymentData.folioNumber"
              :disabled="paymentOption === StaffPaymentOptions.FAS || paymentOption === StaffPaymentOptions.NO_FEE"
              @focus="paymentOption = StaffPaymentOptions.BCOL"
              @emitFolioNumber="paymentOption === StaffPaymentOptions.BCOL &&
                emitStaffPaymentData({ option: StaffPaymentOptions.BCOL, folioNumber: $event })"
              validate="true"
            />
          </v-form>

          <!-- No Fee radio button -->
          <v-radio id="no-fee-radio" class="mb-0 pt-2" label="No Fee" :value="StaffPaymentOptions.NO_FEE" />

          <template v-if="displayPriorityCheckbox">
            <v-divider class="mt-6"></v-divider>

            <!-- Priority checkbox -->
            <v-checkbox
              id="priority-checkbox"
              class="priority-checkbox mt-6 pt-0"
              label="Priority (add $100.00)"
              hide-details
              :input-value="staffPaymentData.isPriority"
              :disabled="paymentOption === StaffPaymentOptions.NO_FEE"
              @change="emitStaffPaymentData({ isPriority: !!$event })"
            />
          </template>
        </v-radio-group>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, ref, toRefs, watch, nextTick } from '@vue/composition-api'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import { FolioNumberInput } from '@bcrs-shared-components/folio-number-input'
// eslint-disable-next-line no-unused-vars
import { FormIF, StaffPaymentIF } from '@bcrs-shared-components/interfaces'

export default defineComponent({
  name: 'SharedStaffPayment',
  components: {
    FolioNumberInput
  },
  emits: ['valid', 'update:staffPaymentData'],
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
          routingSlipNumber: null,
          bcolAccountNumber: null,
          datNumber: null,
          folioNumber: null,
          isPriority: false
        }
      }
    }
  },
  setup (props, context) {
    const fasForm = ref(null) as FormIF
    const bcolForm = ref(null) as FormIF
    const folioNumberInputRef = ref(null)

    const localState = reactive({
      staffPaymentData: { ...props.staffPaymentDataProps } as StaffPaymentIF,
      paymentOption: StaffPaymentOptions.NONE,
      fasFormValid: false,
      bcolFormValid: false,
      isMounted: false
    })

    onMounted(async (): Promise<void> => {
      await nextTick()
      localState.isMounted = true
    })

    /** Validation rules for Routing Slip Number. */
    const routingSlipNumberRules = (): Array<Function> => [
      v => !!v || 'Enter FAS Routing Slip Number',
      v => /^\d{9}$/.test(v) || 'Routing Slip Number must be 9 digits'
    ]

    /** Validation rules for BCOL Account Number. */
    const bcolAccountNumberRules = (): Array<Function> => [
      v => !!v || 'Enter BC Online Account Number',
      v => /^\d{6}$/.test(v) || 'BC Online Account Number must be 6 digits'
    ]

    /** Validation rules for DAT Number. */
    const datNumberRules = (): Array<Function> => [
      v => !!v || 'Enter DAT Number',
      v => /^[A-Z]{1}[0-9]{7,9}$/.test(v) || 'DAT Number must be in standard format (eg, C1234567)'
    ]

    /** Emits an event to update the Staff Payment Data prop. */
    const emitStaffPaymentData = ({
      option = localState.staffPaymentData.option,
      routingSlipNumber = localState.staffPaymentData.routingSlipNumber || '',
      bcolAccountNumber = localState.staffPaymentData.bcolAccountNumber || '',
      datNumber = localState.staffPaymentData.datNumber || '',
      folioNumber = localState.staffPaymentData.folioNumber || '',
      isPriority = localState.staffPaymentData.isPriority || false
    }): StaffPaymentIF => {
      // return only the appropriate fields for each option
      switch (option) {
        case StaffPaymentOptions.FAS:
          context.emit(
            'update:staffPaymentData',
            { option, routingSlipNumber, isPriority } as StaffPaymentIF
          )
          return
        case StaffPaymentOptions.BCOL:
          context.emit(
            'update:staffPaymentData',
            { option, bcolAccountNumber, datNumber, folioNumber, isPriority } as StaffPaymentIF
          )
          return
        case StaffPaymentOptions.NO_FEE:
          context.emit(
            'update:staffPaymentData',
            { option } as StaffPaymentIF
          )
      }
    }

    /** Emits an event indicating whether this component is valid. */
    const emitValid = (): void => {
      console.log(localState.fasFormValid)
      console.log(localState.bcolFormValid)
      console.log(localState.staffPaymentData.option)

      context.emit(
        'valid',
        (localState.fasFormValid ||
          (localState.bcolFormValid && (context.refs.folioNumberInputRef as FormIF).validateFolioNumber()) ||
          (localState.staffPaymentData.option === StaffPaymentOptions.NO_FEE)
        )
      )
    }

    /** Called when payment option (radio group item) has changed. */
    watch(() => localState.paymentOption, async (val: number): Promise<void> => {
      switch (val) {
        case StaffPaymentOptions.FAS:
          // reset other form
          (context.refs.bcolForm as FormIF).resetValidation();
          (context.refs.folioNumberInputRef as FormIF).resetFolioNumberValidation();
          // enable validation for this form
          (context.refs.fasForm as FormIF).validate()
          await nextTick()
          // update data
          emitStaffPaymentData({ option: StaffPaymentOptions.FAS })
          break

        case StaffPaymentOptions.BCOL:
          // reset other form
          (context.refs.fasForm as FormIF).resetValidation();
          // enable validation for this form
          (context.refs.bcolForm as FormIF).validate()
          await nextTick()
          // update data
          emitStaffPaymentData({ option: StaffPaymentOptions.BCOL })
          break

        case StaffPaymentOptions.NO_FEE:
          // reset other forms
          (context.refs.fasForm as FormIF).resetValidation();
          (context.refs.bcolForm as FormIF).resetValidation();
          (context.refs.folioNumberInputRef as FormIF).resetFolioNumberValidation()
          await nextTick()
          // update data
          emitStaffPaymentData({ option: StaffPaymentOptions.NO_FEE, isPriority: false })
          break
      }
    })

    /** Watches for change to FAS and BCOL form validity. */
    watch(() => [localState.fasFormValid, localState.bcolFormValid], async (): Promise<void> => {
      await nextTick()
      // ignore initial condition
      if (!localState.isMounted) return
      emitValid()
    })

    /** Watches for changes to Staff Payment Data prop. */
    watch(() => localState.staffPaymentData, async (val: StaffPaymentIF): Promise<void> => {
      localState.paymentOption = val.option
      await nextTick()
      emitValid()
    }, { deep: true, immediate: true })

    return {
      fasForm,
      bcolForm,
      folioNumberInputRef,
      datNumberRules,
      StaffPaymentOptions,
      emitStaffPaymentData,
      routingSlipNumberRules,
      bcolAccountNumberRules,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#staff-payment-container {
  line-height: 1.2rem;
  font-size: $px-16;
}

.title-label {
  font-weight: bold;
  color: $gray9;
}

.payment-container {
  > label:first-child {
    font-weight: 700;
    margin-bottom: 2rem;
  }
}

.payment-group {
  margin-top: 0;
  padding-top: 0;

  ::v-deep > .v-input__control {
    margin-bottom: -12px;
  }
}
</style>
