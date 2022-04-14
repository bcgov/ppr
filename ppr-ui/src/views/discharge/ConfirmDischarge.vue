<template>
  <v-container
    id="confirm-discharge"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      setAttach="#confirm-discharge"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Confirm and Complete Total Discharge</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Confirm your Total Discharge and complete the additional information before registering.
            </p>
          </div>
          <caution-box class="mt-9" :setMsg="cautionTxt" />
          <h2 class="pt-14">
            Registering Party for this Discharge
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
          <caution-box v-if="showRegMsg" :setMsg="cautionTxtRP" :setImportantWord="'Note'"/>
          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-15"
          />
          <h2 class="pt-15">2. Confirm</h2>
          <p class="ma-0 pt-4">
            You are about to submit a Total Discharge based on the following
            details:
          </p>
          <discharge-confirm-summary
            class="mt-6 soft-corners"
            :setRegNum="registrationNumber"
            :setRegType="registrationTypeUI"
            :setCollateralSummary="collateralSummary"
            :setShowErrors="showErrors"
            @valid="validConfirm = $event"
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
                :setRegistrationType="registrationTypeUI"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Register Total Discharge'"
                :setDisableSubmitBtn="isRoleStaffBcol"
                @back="goToReviewRegistration()"
                @cancel="showDialog()"
                @submit="submitDischarge()"
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
  CautionBox,
  DischargeConfirmSummary,
  FolioNumberSummary,
  CertifyInformation,
  StickyContainer
} from '@/components/common'
import { RegisteringPartyChange } from '@/components/parties/party'
import { BaseDialog } from '@/components/dialogs'
// local helpers/enums/interfaces/resources
import { ActionTypes, APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Throttle } from '@/decorators'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  DischargeRegistrationIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF, // eslint-disable-line no-unused-vars
  DebtorNameIF, // eslint-disable-line no-unused-vars
  RegTableNewItemI // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { AllRegistrationTypes } from '@/resources'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, getFinancingStatement, saveDischarge } from '@/utils'

@Component({
  components: {
    BaseDialog,
    CautionBox,
    DischargeConfirmSummary,
    FolioNumberSummary,
    RegisteringPartyChange,
    CertifyInformation,
    StickyContainer
  }
})
export default class ConfirmDischarge extends Vue {
  @Getter getConfirmDebtorName: DebtorNameIF
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getAddSecuredPartiesAndDebtors: AddPartiesIF
  @Getter getStateModel: StateModelIF
  @Getter isRoleStaffBcol: boolean

  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF
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

  private cautionTxt = 
    'The Registry will provide the Total Discharge Verification ' +
    'Statement to all Secured Parties named in this registration.'

  private cautionTxtRP = 'The Registry will not provide ' +
    'the verification statement for this total discharge to the Registering Party named above.'

  private collateralSummary = '' // eslint-disable-line lines-between-class-members
  private dataLoaded = false
  private dataLoadError = false
  private feeType = FeeSummaryTypes.DISCHARGE
  private financingStatementDate: Date = null
  private options: DialogOptionsIF = notCompleteDialog
  private showCancelDialog = false
  private showErrors = false
  private showRegMsg = false
  private submitting = false
  private tooltipTxt = 'The default Registering Party is based on your BC ' +
    'Registries user account information. This information can be updated within ' +
    'your account settings. You can change to a different Registering Party by ' +
    'using the Change button.'
  private validConfirm = false // eslint-disable-line lines-between-class-members
  private validFolio = true
  private validCertify = false

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

  private get stickyComponentErrMsg (): string {
    if ((!this.validConfirm || !this.validFolio) && this.showErrors) {
      return '< Please complete required information'
    }
    return ''
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

  private handleDialogResp (val: boolean): void {
    this.showCancelDialog = false
    if (!val) {
      this.setRegistrationNumber(null)
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
  }

  private goToReviewRegistration (): void {
    this.$router.push({
      name: RouteNames.REVIEW_DISCHARGE,
      query: { 'reg-num': this.registrationNumber }
    })
    this.emitHaveData(false)
  }

  private setFolioValid (valid: boolean): void {
    this.validFolio = valid
  }

  private showDialog (): void {
    this.showCancelDialog = true
  }

  @Throttle(2000)
  private async submitDischarge (): Promise<void> {
    if ((!this.validConfirm) || (!this.validFolio) || (!this.validCertify)) {
      this.showErrors = true
      return
    }

    const stateModel: StateModelIF = this.getStateModel
    this.submitting = true
    const apiResponse: DischargeRegistrationIF = await saveDischarge(stateModel)
    this.submitting = false
    if (apiResponse === undefined || apiResponse?.error !== undefined) {
      this.emitError(apiResponse?.error)
    } else {
      // set new added reg
      const newItem: RegTableNewItemI = {
        addedReg: apiResponse.dischargeRegistrationNumber,
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
