<template>
  <v-container
    id="confirm-renewal"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      setAttach="#confirm-renewal"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <staff-payment-dialog
      attach=""
      class="mt-10"
      :setDisplay="staffPaymentDialogDisplay"
      :setOptions="staffPaymentDialogOptions"
      :setShowCertifiedCheckbox="false"
      @proceed="onStaffPaymentChanges($event)"
    />
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Review and Complete Renewal</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review your renewal and complete the additional information before registering.
            </p>
          </div>
           <h2 class="pt-14">
            Registering Party for this Renewal
            <v-tooltip
              class="pa-2"
              content-class="top-tooltip"
              top
              transition="fade-transition"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-icon class="ml-1" color="primary" v-bind="attrs" v-on="on">mdi-information-outline</v-icon>
              </template>
              <div class="pt-2 pb-2">
                {{ tooltipTxt }}
              </div>
            </v-tooltip>
          </h2>
          <registering-party-change
            class="pt-4"
            @registeringPartyOpen="setShowWarning()"
          />
          <caution-box v-if="showRegMsg" :setMsg="cautionTxt" :setImportantWord="'Note'" />
          <registration-length-trust-summary class="mt-10" :isRenewal="true"
          />
          <div v-if="showCourtOrderInfo">
            <court-order :setSummary="true" :isRenewal="true" class="pt-10" />
          </div>

          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-10"
          />
          <certify-information
            @certifyValid="validCertify = $event"
            :setShowErrors="showErrors"
            class="pt-10"
          />
        </v-col>
        <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
                :setErrMsg="stickyComponentErrMsg"
                :setRightOffset="true"
                :setShowButtons="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setRegistrationLength="registrationLength"
                :setRegistrationType="registrationTypeUI"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Register Renewal and Pay'"
                :setDisableSubmitBtn="isRoleStaffBcol"
                @back="goToReviewRenewal()"
                @cancel="showCancelDialog = true"
                @submit="submitButton()"
              />
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local components
import {
  FolioNumberSummary,
  CertifyInformation,
  CourtOrder,
  StickyContainer,
  CautionBox
} from '@/components/common'
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { RegisteringPartyChange } from '@/components/parties/party'

// local helpers/enums/interfaces/resources
import { ActionTypes, APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Throttle } from '@/decorators'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  RenewRegistrationIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF, // eslint-disable-line no-unused-vars
  DebtorNameIF, // eslint-disable-line no-unused-vars
  RegTableNewItemI // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
import { AllRegistrationTypes } from '@/resources'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, getFinancingStatement, saveRenewal } from '@/utils'

@Component({
  components: {
    BaseDialog,
    StaffPaymentDialog,
    CourtOrder,
    FolioNumberSummary,
    RegisteringPartyChange,
    RegistrationLengthTrustSummary,
    CertifyInformation,
    CautionBox,
    StickyContainer
  }
})
export default class ConfirmDischarge extends Vue {
  @Getter getConfirmDebtorName: DebtorNameIF
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getAddSecuredPartiesAndDebtors: AddPartiesIF
  @Getter getStateModel: StateModelIF
  @Getter getLengthTrust: LengthTrustIF
  @Getter isRoleStaffBcol: boolean
  @Getter isRoleStaffReg: boolean
  @Getter isRoleStaffSbc: boolean

  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF
  @Action setFeeSummary: ActionBindingIF
  @Action setRegistrationCreationDate: ActionBindingIF
  @Action setRegistrationExpiryDate: ActionBindingIF
  @Action setRegistrationNumber: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF
  @Action setRegTableNewItem: ActionBindingIF
  @Action setUnsavedChanges: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private collateralSummary = '' // eslint-disable-line lines-between-class-members
  private dataLoaded = false
  private dataLoadError = false
  private financingStatementDate: Date = null
  private options: DialogOptionsIF = notCompleteDialog
  private showCancelDialog = false
  private submitting = false
  private showRegMsg = false

  private staffPaymentDialogDisplay = false
  private staffPaymentDialogOptions: DialogOptionsIF = {
    acceptText: 'Submit Renewal',
    cancelText: 'Cancel',
    title: 'Staff Payment',
    label: '',
    text: ''
  }

  private showErrors = false
  private tooltipTxt = 'The default Registering Party is based on your BC ' +
    'Registries user account information. This information can be updated within ' +
    'your account settings. You can change to a different Registering Party by ' +
    'using the Change button.'

  private cautionTxt = 'The Registry will not provide ' +
    'the verification statement for this renewal to the Registering Party named above.'

  private validFolio = true
  private validCertify = false
  private feeType = FeeSummaryTypes.RENEW

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  // the number of the registration being discharged
  private get registrationNumber (): string {
    return (this.$route.query['reg-num'] as string) || ''
  }

  private get registrationTypeUI (): UIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeUI || null
  }

  private get registrationType (): APIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeAPI || null
  }

  private get registrationLength (): RegistrationLengthI {
    return {
      lifeInfinite: this.getLengthTrust?.lifeInfinite || false,
      lifeYears: this.getLengthTrust?.lifeYears || 0
    }
  }

  private get stickyComponentErrMsg (): string {
    if (!this.validFolio && this.showErrors) {
      return '< Please complete required information'
    }
    return ''
  }

  private get showCourtOrderInfo (): boolean {
    return (this.getRegistrationType && this.registrationType === APIRegistrationTypes.REPAIRERS_LIEN)
  }

  private handleDialogResp (val: boolean): void {
    this.showCancelDialog = false
    if (!val) {
      this.setRegistrationNumber(null)
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
  }

  private async loadRegistration (): Promise<void> {
    if (!this.registrationNumber || !this.getConfirmDebtorName) {
      if (!this.registrationNumber) {
        console.error('No registration number given to discharge. Redirecting to dashboard...')
      } else {
        console.error('No debtor name confirmed for discharge. Redirecting to dashboard...')
      }
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      return
    }
    this.financingStatementDate = new Date()
    const financingStatement = await getFinancingStatement(
      true,
      this.registrationNumber
    )
    if (financingStatement.error) {
      this.dataLoadError = true
      this.emitError(financingStatement.error)
    } else {
      // set collateral summary
      if (
        financingStatement.generalCollateral &&
        !financingStatement.vehicleCollateral
      ) {
        this.collateralSummary = 'General Collateral and 0 Vehicles'
      } else if (financingStatement.generalCollateral) {
        this.collateralSummary = `General Collateral and ${financingStatement.vehicleCollateral.length} Vehicles`
      } else if (financingStatement.vehicleCollateral) {
        this.collateralSummary = `No General Collateral and ${financingStatement.vehicleCollateral.length} Vehicles`
      } else {
        this.collateralSummary += 'No Collateral'
      }
      if (financingStatement.vehicleCollateral?.length === 1) {
        this.collateralSummary = this.collateralSummary.replace('Vehicles', 'Vehicle')
      }
      // load data into the store
      const registrationType = AllRegistrationTypes.find((reg, index) => {
        if (reg.registrationTypeAPI === financingStatement.type) {
          return true
        }
      })
      const parties = {
        valid: true,
        registeringParty: null,
        securedParties: financingStatement.securedParties,
        debtors: financingStatement.debtors
      } as AddPartiesIF
      this.setRegistrationCreationDate(financingStatement.createDateTime)
      this.setRegistrationExpiryDate(financingStatement.expiryDate)
      this.setRegistrationNumber(financingStatement.baseRegistrationNumber)
      this.setRegistrationType(registrationType)
      this.setAddSecuredPartiesAndDebtors(parties)
    }
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  private goToReviewRenewal (): void {
    this.$router.push({
      name: RouteNames.RENEW_REGISTRATION,
      query: { 'reg-num': this.registrationNumber }
    })
    this.emitHaveData(false)
  }

  private setFolioValid (valid: boolean): void {
    this.validFolio = valid
  }

  private onStaffPaymentChanges (pay: boolean): void {
    if (pay) {
      this.submitRenewal()
    }
    this.staffPaymentDialogDisplay = false
  }

  private submitButton (): void {
    if ((!this.validFolio) || (!this.validCertify)) {
      this.showErrors = true
      return
    }
    if ((this.isRoleStaffReg) || (this.isRoleStaffSbc)) {
      this.staffPaymentDialogDisplay = true
    } else {
      this.submitRenewal()
    }
  }

  @Throttle(2000)
  private async submitRenewal (): Promise<void> {
    const stateModel: StateModelIF = this.getStateModel
    this.submitting = true
    const apiResponse: RenewRegistrationIF = await saveRenewal(stateModel)
    this.submitting = false
    if (apiResponse === undefined || apiResponse?.error !== undefined) {
      console.error(apiResponse?.error)
      this.emitError(apiResponse?.error)
    } else {
      // unset registration number
      this.setRegistrationNumber(null)
      // set new added reg
      const newItem: RegTableNewItemI = {
        addedReg: apiResponse.renewalRegistrationNumber,
        addedRegParent: apiResponse.baseRegistrationNumber,
        addedRegSummary: null,
        prevDraft: ''
      }
      this.setRegTableNewItem(newItem)
      // On success return to dashboard
      this.goToDashboard()
    }
  }

  private goToDashboard (): void {
    // unset registration number
    this.setRegistrationNumber(null)
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
    this.emitHaveData(false)
  }

  private setShowWarning (): void {
    const parties = this.getAddSecuredPartiesAndDebtors
    if (parties.registeringParty?.action === ActionTypes.EDITED) {
      this.showRegMsg = true
    } else {
      this.showRegMsg = false
    }
  }

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void {}

  /** Emits error to app.vue for handling */
  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

  /** Called when App is ready and this component can load its data. */
  @Watch('appReady')
  private async onAppReady (val: boolean): Promise<void> {
    // do not proceed if app is not ready
    if (!val) return
    // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
    if (!this.isAuthenticated || (!this.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      return
    }

    // get registration data from api and load into store
    this.submitting = true
    await this.loadRegistration()
    this.submitting = false

    // page is ready to view
    this.emitHaveData(true)
    this.dataLoaded = true
  }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
