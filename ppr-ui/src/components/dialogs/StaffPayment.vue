<template>
<v-dialog v-model="display" width="720px" persistent :attach="attach">
  <v-row no-gutters>
        <v-col cols="11">
          <h2 class="dialog-title">Staff Payment</h2>
          <div class="pt-9">
            <div :class="{'invalid-section': invalidStaffPayment}">
              <staff-payment-component
                :staffPaymentData="getStaffPayment"
                :validate="validateStaffPayment"
                :invalidSection="invalidStaffPayment"
                @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
                @valid="setStaffPaymentValidity($event)"
              />
            </div>
          </div>
        </v-col>
        <v-col cols="1">
          <v-btn class="close-btn float-right" color="primary" icon :ripple="false" @click="proceed(false)">
            <v-icon size="32px">mdi-close</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <v-row justify="center" no-gutters>
    <v-col v-if="cancelText" cols="auto">
      <v-btn id="cancel-btn" class="outlined dialog-btn" outlined @click="proceed(false)">
        Cancel
      </v-btn>
    </v-col>
    <v-col v-if="acceptText" :class="{ 'pl-3': cancelText }" cols="auto">
      <v-btn id="accept-btn" class="primary dialog-btn" @click="proceed(true)">
        Accept
      </v-btn>
    </v-col>
  </v-row>
</v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'

// Components
import { StaffPayment as StaffPaymentComponent } from '@bcrs-shared-components/staff-payment'

// Interfaces and Enums
import { ActionBindingIF } from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'

@Component({
  components: {
    StaffPaymentComponent
  }
})
export default class StaffPayment extends Vue {
  // Global getters
  @Getter getAppValidate!: boolean
  @Getter getStaffPayment!: StaffPaymentIF

  // Global actions
  @Action setStaffPayment!: ActionBindingIF
  @Action setStaffPaymentValidity!: ActionBindingIF

  /** Prop to provide section number. */
  @Prop({ default: '' }) readonly sectionNumber: string

  /** Check validity state, only when prompted by app. */
  private get invalidStaffPayment (): boolean {
    return this.getAppValidate
  }

  /** Is true when prompted by the app AND the user has selected an option. */
  private get validateStaffPayment (): boolean {
    return this.getAppValidate && !!this.getStaffPayment?.option
  }

  onStaffPaymentDataUpdate (event: any) {
    let staffPaymentData: StaffPaymentIF = { ...this.getStaffPayment, ...event }

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

    this.setStaffPayment(staffPaymentData)
    this.emitHaveChanges()
  }

  @Emit('haveChanges')
  private emitHaveChanges (): void {}
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

::v-deep .v-input .v-label {
  font-weight: normal;
}

::v-deep .v-input--radio-group__input {
  .v-radio:not(:first-child) {
    padding-top: 2rem;
  }
  .v-input--checkbox {
    padding-top: 2rem;
  }
}

::v-deep .v-input--selection-controls__ripple {
  color: $gray7;
}

::v-deep .v-text-field__slot {
  .v-label {
    color: $gray7;
  }
}

</style>
