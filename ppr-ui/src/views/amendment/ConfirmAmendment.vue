<template>
  <v-container
    id="confirm-amendment"
    class="view-container pa-15 pt-4"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
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
          <h1>Review and Complete Amendment</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review your Amendment and complete the additional information before registering.
            </p>
          </div>
          <caution-box class="mt-9" style="margin-bottom: 60px;" :setMsg="cautionTxt" :setImportantWord="'Note'" />

          <v-row no-gutters class="summary-header pa-2 mt-4 rounded-top">
            <v-col cols="12" class="pa-2">
              <label class="pl-3">
                <v-icon color="darkBlue">mdi-file-document-multiple</v-icon>
                <span class="pl-3"><strong>Amendment</strong></span>
              </label>
            </v-col>
          </v-row>
          <div class="white ma-0 px-4 rounded-bottom">
            <div v-if="showLengthTrustIndenture">
              <registration-length-trust-amendment class="pt-4" :isSummary="true" />
            </div>

            <div v-if="showSecuredParties">
              <v-divider v-if="showLengthTrustIndenture"></v-divider>
              <h3 class="pt-6 px-3">Secured Parties</h3>
              <secured-party-summary
                class="secured-party-summary px-8"
                :setEnableNoDataAction="true"
              />
            </div>

            <div v-if="showDebtors" class="pa-4">
              <v-divider v-if="showSecuredParties || showLengthTrustIndenture"></v-divider>
              <h3 class="pt-6">Debtors</h3>
              <debtor-summary
                class="debtor-summary px-4"
                :setEnableNoDataAction="true"
              />
            </div>

            <div v-if="showVehicleCollateral || showGeneralCollateral">
              <!-- To do: add amended collateral -->
              <div v-if="showVehicleCollateral">
                <v-divider v-if="showSecuredParties || showDebtors || showLengthTrustIndenture"></v-divider>
                <vehicle-collateral
                  :isSummary="true"
                  :showInvalid="false"
                />
              </div>
              <div v-if="showGeneralCollateral" class="pt-6">
                <v-divider v-if="showSecuredParties || showDebtors ||
                          showVehicleCollateral || showLengthTrustIndenture"></v-divider>
                <gen-col-summary class="py-6 px-4"
                  :setShowAmendLink="false"
                  :setShowHistory="false"
                  :setShowViewLink="false"
                  :setShowConfirm="true"
                />
              </div>
            </div>

            <div class="pb-4" v-if="showDescription">
              <v-divider v-if="showSecuredParties || showDebtors || showVehicleCollateral ||
                               showGeneralCollateral || showLengthTrustIndenture"></v-divider>
              <amendment-description class="pt-4" :isSummary="true" />
            </div>

            <div v-if="showCourtOrder">
              <v-divider v-if="showSecuredParties || showDebtors || showVehicleCollateral ||
                              showGeneralCollateral || showDescription || showLengthTrustIndenture"></v-divider>
              <court-order class="py-8" :setSummary="true" />
            </div>

          </div>

          <h2 class="pt-14">
            Registering Party for this Amendment
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
            @registeringPartyOpen="regOpenClose($event)"
            :setShowErrorBar="showErrors && registeringOpen"
          />
          <caution-box v-if="showRegMsg" :setMsg="cautionTxtRP" :setImportantWord="'Note'" />
          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-10"
          />
          <certify-information
            @certifyValid="showErrors = false"
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
                :setSaveBtn="'Save and Resume Later'"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Register Amendment and Pay'"
                :setDisableSubmitBtn="isRoleStaffBcol"
                @back="goToReviewAmendment()"
                @save="saveDraft()"
                @cancel="cancel()"
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
  CautionBox,
  CourtOrder,
  CertifyInformation,
  FolioNumberSummary,
  StickyContainer
} from '@/components/common'
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { GenColSummary } from '@/components/collateral/generalCollateral'
import { SecuredPartySummary, DebtorSummary } from '@/components/parties/summaries'
import { RegisteringPartyChange } from '@/components/parties/party'
import { AmendmentDescription, RegistrationLengthTrustAmendment } from '@/components/registration'
import { VehicleCollateral } from '@/components/collateral/vehicleCollateral'

// local helpers/enums/interfaces/resources
import { ActionTypes, APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import { Throttle } from '@/decorators'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  AddCollateralIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  AmendmentStatementIF, // eslint-disable-line no-unused-vars
  CertifyIF, // eslint-disable-line no-unused-vars
  CourtOrderIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF, // eslint-disable-line no-unused-vars
  DebtorNameIF, // eslint-disable-line no-unused-vars
  DraftIF, // eslint-disable-line no-unused-vars
  FinancingStatementIF, // eslint-disable-line no-unused-vars
  RegTableNewItemI // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars

import { AllRegistrationTypes } from '@/resources'
import { unsavedChangesDialog } from '@/resources/dialogOptions'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  getFeatureFlag,
  getFinancingStatement,
  saveAmendmentStatement,
  saveAmendmentStatementDraft
} from '@/utils'

@Component({
  components: {
    AmendmentDescription,
    BaseDialog,
    StaffPaymentDialog,
    CautionBox,
    CertifyInformation,
    FolioNumberSummary,
    RegisteringPartyChange,
    SecuredPartySummary,
    DebtorSummary,
    VehicleCollateral,
    GenColSummary,
    CourtOrder,
    RegistrationLengthTrustAmendment,
    StickyContainer
  }
})
export default class ConfirmAmendment extends Vue {
  @Getter getAddCollateral: AddCollateralIF
  @Getter getAddSecuredPartiesAndDebtors: AddPartiesIF
  @Getter getAmendmentDescription: string
  @Getter getCertifyInformation: CertifyIF
  @Getter getConfirmDebtorName: DebtorNameIF
  @Getter getCourtOrderInformation: CourtOrderIF
  @Getter getLengthTrust: LengthTrustIF
  @Getter getRegistrationNumber: string
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getStateModel: StateModelIF
  @Getter hasUnsavedChanges: Boolean
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

  @Prop({ default: false })
  private saveDraftExit: boolean

  private collateralSummary = '' // eslint-disable-line lines-between-class-members
  private dataLoaded = false
  private dataLoadError = false
  private registeringOpen = false
  private showRegMsg = false
  private financingStatementDate: Date = null
  private options: DialogOptionsIF = unsavedChangesDialog

  private staffPaymentDialogDisplay = false

  private staffPaymentDialogOptions: DialogOptionsIF = {
    acceptText: 'Submit Amendment',
    cancelText: 'Cancel',
    title: 'Staff Payment',
    label: '',
    text: ''
  }

  private showCancelDialog = false
  private showErrors = false

  private cautionTxt =
    'The Registry will provide the verification statement to all Secured Parties named in this registration.'

  private cautionTxtRP = 'The Registry will not provide ' +
    'the verification statement for this amendment to the Registering Party named above.'

  private tooltipTxt = 'The default Registering Party is based on your BC ' +
    'Registries user account information. This information can be updated within ' +
    'your account settings. You can change to a different Registering Party by ' +
    'using the Change button.'

  private validFolio = true
  private feeType = FeeSummaryTypes.AMEND

  private submitting = false

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

  private get showDescription (): boolean {
    if (this.getAmendmentDescription) {
      return true
    }
    return false
  }

  private get currentRegNumber (): string {
    return this.getRegistrationNumber || ''
  }

  private get showCourtOrder (): boolean {
    const courtOrder: CourtOrderIF = this.getCourtOrderInformation
    if (courtOrder &&
        (courtOrder?.courtName.length > 0 ||
         courtOrder?.courtRegistry.length > 0 ||
         courtOrder?.fileNumber.length > 0 ||
         courtOrder?.orderDate.length > 0 ||
         courtOrder?.effectOfOrder.length > 0)) {
      return true
    }
    return false
  }

  private get showLengthTrustIndenture (): boolean {
    const lengthTrust: LengthTrustIF = this.getLengthTrust
    if (lengthTrust.action) {
      return true
    }
    return false
  }

  private get showSecuredParties (): boolean {
    const parties: AddPartiesIF = this.getAddSecuredPartiesAndDebtors
    for (let i = 0; i < parties.securedParties.length; i++) {
      if (parties.securedParties[i].action) {
        return true
      }
    }
    return false
  }

  private get showDebtors (): boolean {
    const parties: AddPartiesIF = this.getAddSecuredPartiesAndDebtors
    for (let i = 0; i < parties.debtors.length; i++) {
      if (parties.debtors[i].action) {
        return true
      }
    }
    return false
  }

  private get showVehicleCollateral (): boolean {
    const addCollateral:AddCollateralIF = this.getAddCollateral
    if (!addCollateral.vehicleCollateral) {
      return false
    }
    for (let i = 0; i < addCollateral.vehicleCollateral.length; i++) {
      if (addCollateral.vehicleCollateral[i].action) {
        return true
      }
    }
    return false
  }

  private get showGeneralCollateral (): boolean {
    const addCollateral:AddCollateralIF = this.getAddCollateral
    if (!addCollateral.generalCollateral) {
      return false
    }
    for (let i = 0; i < addCollateral.generalCollateral.length; i++) {
      if (!addCollateral.generalCollateral[i].collateralId) {
        return true
      }
    }
    return false
  }

  private get collateralValid (): boolean {
    const addCollateral:AddCollateralIF = this.getAddCollateral
    return (addCollateral.valid || (!this.showGeneralCollateral && !this.showVehicleCollateral))
  }

  private get partiesValid (): boolean {
    const parties: AddPartiesIF = this.getAddSecuredPartiesAndDebtors
    return (parties.valid || (!this.showSecuredParties && !this.showDebtors))
  }

  private get courtOrderValid (): boolean {
    const courtOrder: CourtOrderIF = this.getCourtOrderInformation
    return (!courtOrder ||
            (courtOrder.courtName.length === 0 &&
            courtOrder.courtRegistry.length === 0 &&
            courtOrder.fileNumber.length === 0 &&
            courtOrder.orderDate.length === 0 &&
            courtOrder.effectOfOrder.length === 0) ||
            (courtOrder.courtName.length > 0 &&
            courtOrder.courtRegistry.length > 0 &&
            courtOrder.fileNumber.length > 0 &&
            courtOrder.orderDate.length > 0 &&
            courtOrder.effectOfOrder.length > 0))
  }

  private get certifyInformationValid (): boolean {
    return this.getCertifyInformation.valid
  }

  private get stickyComponentErrMsg (): string {
    if ((!this.validFolio || !this.courtOrderValid) && this.showErrors) {
      return '< Please complete required information'
    }
    if ((this.registeringOpen || !this.certifyInformationValid) && this.showErrors) {
      return '< You have unfinished changes'
    }
    return ''
  }

  private cancel (): void {
    if (this.hasUnsavedChanges) this.showCancelDialog = true
    else this.goToDashboard()
  }

  private handleDialogResp (val: boolean): void {
    this.showCancelDialog = false
    if (!val) this.goToDashboard()
  }

  private async scrollToInvalid (): Promise<void> {
    if (!this.validFolio) {
      const component = document.getElementById('folio-summary')
      await component.scrollIntoView({ behavior: 'smooth' })
      return
    }
    if (this.registeringOpen) {
      const component = document.getElementById('reg-party-change')
      await component.scrollIntoView({ behavior: 'smooth' })
      return
    }
    if (!this.courtOrderValid) {
      const component = document.getElementById('court-order-component')
      await component.scrollIntoView({ behavior: 'smooth' })
      return
    }
    if (!this.certifyInformationValid) {
      const component = document.getElementById('certify-information')
      await component.scrollIntoView({ behavior: 'smooth' })
    }
  }

  private async loadRegistration (): Promise<void> {
    if (!this.registrationNumber || !this.getConfirmDebtorName) {
      if (!this.registrationNumber) {
        console.error('No registration number this amendment. Redirecting to dashboard...')
      } else {
        console.error('No debtor name confirmed for this amendment. Redirecting to dashboard...')
      }
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      return
    }
    if (this.currentRegNumber === this.registrationNumber) {
      return
    }

    this.financingStatementDate = new Date()
    this.submitting = true
    const financingStatement = await getFinancingStatement(
      true,
      this.registrationNumber
    )
    if (financingStatement.error) {
      this.dataLoadError = true
      this.emitError(financingStatement.error)
    } else {
      await this.setStore(financingStatement)
      // give time for setStore to finish
      setTimeout(() => {
        this.setUnsavedChanges(false)
      }, 200)
    }
    this.submitting = false
  }

  private async setStore (financingStatement: FinancingStatementIF) {
    // load data into the store
    const registrationType = AllRegistrationTypes.find((reg, index) => {
      if (reg.registrationTypeAPI === financingStatement.type) {
        return true
      }
    })
    const parties = {
      valid: true,
      registeringParty: null, // will be taken from account info
      securedParties: financingStatement.securedParties,
      debtors: financingStatement.debtors
    } as AddPartiesIF
    this.setRegistrationCreationDate(financingStatement.createDateTime)
    this.setRegistrationExpiryDate(financingStatement.expiryDate)
    this.setRegistrationNumber(financingStatement.baseRegistrationNumber)
    this.setRegistrationType(registrationType)
    this.setAddSecuredPartiesAndDebtors(parties)
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  private goToReviewAmendment (): void {
    this.$router.push({
      name: RouteNames.AMEND_REGISTRATION,
      query: { 'reg-num': this.registrationNumber + '-confirm' }
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

  @Throttle(2000)
  private onStaffPaymentChanges (pay: boolean): void {
    if (pay) {
      this.submitAmendment()
    }
    this.staffPaymentDialogDisplay = false
  }

  private setFolioValid (valid: boolean): void {
    this.validFolio = valid
    this.showErrors = false
  }

  private regOpenClose (open: boolean): void {
    this.registeringOpen = open
    this.showErrors = false
    this.setShowWarning()
  }

  @Throttle(2000)
  private async saveDraft (): Promise<void> {
    const stateModel: StateModelIF = this.getStateModel
    this.submitting = true
    const draft: DraftIF = await saveAmendmentStatementDraft(stateModel)
    this.submitting = false
    if (draft.error) {
      this.emitError(draft.error)
    } else {
      this.setUnsavedChanges(false)
      const prevDraftId = stateModel.registration?.draft?.amendmentStatement?.documentId || ''
      // set new added reg
      const newItem: RegTableNewItemI = {
        addedReg: draft.amendmentStatement.documentId,
        addedRegParent: draft.amendmentStatement.baseRegistrationNumber,
        addedRegSummary: null,
        prevDraft: prevDraftId
      }
      this.setRegTableNewItem(newItem)
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      this.emitHaveData(false)
    }
  }

  @Throttle(2000)
  private submitButton (): void {
    if (!this.validFolio || !this.certifyInformationValid || this.registeringOpen) {
      this.showErrors = true
      this.scrollToInvalid()
      return
    }
    if ((this.isRoleStaffReg) || (this.isRoleStaffSbc)) {
      this.staffPaymentDialogDisplay = true
    } else {
      this.submitAmendment()
    }
  }

  private async submitAmendment (): Promise<void> {
    // Incomplete validation check: all changes must be valid to submit registration.
    if (this.collateralValid && this.partiesValid && this.courtOrderValid) {
      const stateModel: StateModelIF = this.getStateModel
      this.submitting = true
      const apiResponse: AmendmentStatementIF = await saveAmendmentStatement(stateModel)
      this.submitting = false
      if (apiResponse === undefined || apiResponse?.error !== undefined) {
        this.emitError(apiResponse?.error)
      } else {
        const prevDraftId = stateModel.registration?.draft?.amendmentStatement?.documentId || ''
        // set new added reg
        const newItem: RegTableNewItemI = {
          addedReg: apiResponse.amendmentRegistrationNumber,
          addedRegParent: apiResponse.baseRegistrationNumber,
          addedRegSummary: null,
          prevDraft: prevDraftId
        }
        this.setRegTableNewItem(newItem)
        // On success return to dashboard
        this.goToDashboard()
      }
    } else {
      // emit registation incomplete error
      const error: ErrorIF = {
        statusCode: 400,
        message: 'Registration incomplete: one or more changes is invalid.'
      }
      console.error(error)
      alert(error.message)
    }
  }

  private goToDashboard (): void {
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
    this.emitHaveData(false)
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
    await this.loadRegistration()

    // page is ready to view
    this.emitHaveData(true)
    this.dataLoaded = true
  }

  @Watch('saveDraftExit')
  private saveDraftExitHandler (val: boolean): void {
    this.saveDraft()
  }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.border-btm {
  border-bottom: 1px solid $gray3;
}
</style>
