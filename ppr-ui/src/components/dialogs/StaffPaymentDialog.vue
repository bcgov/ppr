<template>
  <BaseDialog
    :set-display="display"
    :set-options="options"
    @proceed="proceed($event)"
  >
    <template #content>
      <StaffPayment
        :staff-payment-data="staffPaymentData"
        :validate="validating"
        :display-side-label="false"
        :display-priority-checkbox="false"
        @update:staff-payment-data="onStaffPaymentDataUpdate($event)"
        @valid="valid = $event"
      />
      <v-row
        v-if="showCertifiedCheckbox"
        no-gutters
      >
        <v-col>
          <v-checkbox
            id="certify-checkbox"
            v-model="certify"
            class="mt-2"
            label="Make this a Certified Search ($25.00)"
            hide-details
          />
        </v-col>
      </v-row>
    </template>
  </BaseDialog>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  nextTick,
  reactive,
  toRefs
} from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import StaffPayment from '@/components/common/StaffPayment.vue'
import { StaffPaymentOptions } from '@/enums'
import type { DialogOptionsIF, StaffPaymentIF } from '@/interfaces'

export default defineComponent({
  name: 'StaffPaymentDialog',
  components: {
    StaffPayment
  },
  props: {
    setOptions: {
      type: Object as () => DialogOptionsIF,
      default: () => {
        return {
          acceptText: 'Submit',
          cancelText: 'Cancel',
          text: '',
          title: 'Staff Payment'
        }
      }
    },
    setDisplay: {
      type: Boolean,
      default: false
    },
    setShowCertifiedCheckbox: {
      type: Boolean,
      default: false
    }
  },
  emits: ['proceed'],
  setup (props, { emit }) {
    const { setStaffPayment, setSearchCertified } = useStore()
    const { getStaffPayment } = storeToRefs(useStore())
    const localState = reactive({
      certify: false,
      valid: false,
      validating: false,
      paymentOption: StaffPaymentOptions.NONE,
      display: computed(() => {
        return props.setDisplay
      }),
      options: computed(() => {
        return props.setOptions
      }),
      showCertifiedCheckbox: computed(() => {
        return props.setShowCertifiedCheckbox
      }),
      staffPaymentData: computed(() => {
        let pd = getStaffPayment.value
        if (!pd) {
          pd = {
            option: StaffPaymentOptions.NONE,
            routingSlipNumber: '',
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: '',
            isPriority: false
          }
        }
        return pd
      })
    })

    const proceed = async (val: boolean): Promise<void> => {
      // Validate Forms
      localState.validating = true
      await nextTick()

      if (val) {
        if (localState.valid) {
          setSearchCertified(localState.certify)
          setStaffPayment(localState.staffPaymentData)
          emit('proceed', val)
        }
        // is false... they cancelled or closed the box
      } else {
        // blank payment data when closing the box
        const pd = {
          option: StaffPaymentOptions.NONE,
          routingSlipNumber: '',
          bcolAccountNumber: '',
          datNumber: '',
          folioNumber: '',
          isPriority: false
        }
        setStaffPayment(pd)
        // reset certified
        localState.certify = false
        localState.validating = false
        setSearchCertified(localState.certify)
        emit('proceed', val)
      }
    }

    /** Called when component's staff payment data has been updated. */
    const onStaffPaymentDataUpdate = (val: StaffPaymentIF) => {
      let staffPaymentData: StaffPaymentIF = {
        ...val
      }

      if (staffPaymentData.routingSlipNumber || staffPaymentData.bcolAccountNumber || staffPaymentData.datNumber) {
        localState.validating = true
      } else {
        if (localState.paymentOption !== staffPaymentData.option) {
          localState.validating = false
          localState.paymentOption = staffPaymentData.option
        }
      }

      // disable validation
      switch (staffPaymentData.option) {
        case StaffPaymentOptions.FAS:
          staffPaymentData = {
            option: StaffPaymentOptions.FAS,
            routingSlipNumber: staffPaymentData.routingSlipNumber,
            isPriority: staffPaymentData.isPriority,
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: ''
          }
          break

        case StaffPaymentOptions.BCOL:
          staffPaymentData = {
            option: StaffPaymentOptions.BCOL,
            bcolAccountNumber: staffPaymentData.bcolAccountNumber,
            datNumber: staffPaymentData.datNumber,
            folioNumber: staffPaymentData.folioNumber,
            isPriority: staffPaymentData.isPriority,
            routingSlipNumber: ''
          }
          break

        case StaffPaymentOptions.NO_FEE:
          staffPaymentData = {
            option: StaffPaymentOptions.NO_FEE,
            routingSlipNumber: '',
            isPriority: false,
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: ''
          }
          break

        case StaffPaymentOptions.NONE: // should never happen
          break
      }

      setStaffPayment(staffPaymentData)
    }

    return {
      proceed,
      onStaffPaymentDataUpdate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

// override internal whitespace
:deep(#staff-payment-container) {
  padding: 0 !important;
  margin: 0 !important;
}

// override default radio input background colour
:deep(.v-input--radio-group__input) {
  background-color: white;
}

// remove margin below radio group
:deep(.v-input--radio-group > .v-input__control > .v-input__slot) {
  margin-bottom: 0 !important;
}

// hide messages below radio group
:deep(.v-input--radio-group > .v-input__control > .v-messages) {
  display: none;
}

:deep(.theme--light.v-label),
:deep(.theme--light.v-input input) {
  color: $gray7;
}

:deep(.theme--light.v-label--is-disabled) {
  color: rgba(0, 0, 0, 0.38);
}

:deep(.v-application--is-ltr .v-text-field .v-label) {
  color: rgba(0, 0, 0, 0.6);
}
</style>
