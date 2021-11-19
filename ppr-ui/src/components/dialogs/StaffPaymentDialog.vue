<template>
  <v-dialog v-model="setDisplay" width="720px" persistent :attach="attach">
    <v-card id="staff-payment-dialog" class="pl-5 pr-1 pt-5">
      <v-row no-gutters>
        <v-col cols="11">
          <h3 class="dialog-title pb-6">Staff Payment</h3>
          <div>
            <div :class="{ invalidSection: showStaffPaymentInvalidSection }">
              <staff-payment-component
                :staffPaymentData="staffPaymentData"
                :validate="validate"
                :displaySideLabel="false"
                :displayPriorityCheckbox="false"
                @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
                @valid="valid = $event"
              />
            </div>
            <v-row no-gutters>
              <v-col class="pl-2">
                <v-checkbox
                  class="mt-2"
                  v-model="certify"
                  id="certify-checkbox"
                  label="Make this a Certified Search ($25.00)"
                />
              </v-col>
            </v-row>
          </div>
        </v-col>
        <v-col cols="1">
          <v-btn
            class="close-btn float-right"
            color="primary"
            icon
            :ripple="false"
            @click="proceed(false)"
          >
            <v-icon size="32px">mdi-close</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <v-row class="pb-6" justify="center" no-gutters>
        <v-col cols="auto">
          <v-btn
            id="cancel-btn"
            class="outlined dialog-btn"
            outlined
            @click="proceed(false)"
          >
            Cancel
          </v-btn>
        </v-col>
        <v-col class="pl-3" cols="auto">
          <v-btn
            id="accept-btn"
            class="primary dialog-btn"
            @click="proceed(true)"
          >
            Submit Search
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'

// Components
import { StaffPayment as StaffPaymentComponent } from '@bcrs-shared-components/staff-payment'

// Interfaces and Enums
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces' // eslint-disable-line no-unused-vars
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'

export default defineComponent({
  name: 'StaffPaymentDialog',
  components: {
    StaffPaymentComponent
  },
  props: {
    setAttach: { default: '' },
    setDisplay: { default: false }
  },
  emits: ['proceed'],
  setup (props, { emit }) {
    const { setStaffPayment } = useActions<any>(['setStaffPayment'])
    const { getStaffPayment } = useGetters<any>(['getStaffPayment'])
    const localState = reactive({
      validate: false,
      certify: false,
      valid: false,
      paymentOption: StaffPaymentOptions.NONE,
      attach: computed(() => {
        return props.setAttach
      }),
      display: computed(() => {
        return props.setDisplay
      }),
      staffPaymentData: computed(() => {
        let pd = getStaffPayment.value
        if (!pd) {
          pd = {
            option: StaffPaymentOptions.NO_FEE,
            routingSlipNumber: '',
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: '',
            isPriority: false
          }
        }
        return pd
      }),
      showStaffPaymentInvalidSection: computed(() => {
        let option
        if (getStaffPayment.value && getStaffPayment.value.option) {
          option = getStaffPayment.value.option
        } else {
          option = StaffPaymentOptions.NONE
        }
        // True if no option is selected
        return localState.validate && option === StaffPaymentOptions.NONE
      })
    })

    const proceed = (val: boolean) => {
      if (localState.valid) {
        setStaffPayment(localState.staffPaymentData)
        emit('proceed', val)
      } else {
        localState.validate = true
      }
    }

    /** Called when component's staff payment data has been updated. */
    const onStaffPaymentDataUpdate = (val: StaffPaymentIF) => {
      let staffPaymentData: StaffPaymentIF = {
        ...getStaffPayment.value,
        ...val
      }

      // disable validation
      localState.validate = false

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
::v-deep #staff-payment-container {
  padding: 0 !important;
  margin: 0 !important;
}

// override default radio input background colour
::v-deep .v-input--radio-group__input {
  background-color: white;
}

// remove margin below radio group
::v-deep .v-input--radio-group > .v-input__control > .v-input__slot {
  margin-bottom: 0 !important;
}

// hide messages below radio group
::v-deep .v-input--radio-group > .v-input__control > .v-messages {
  display: none;
}
</style>
