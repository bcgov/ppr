<template>
  <v-container class="view-container pa-15 pt-14" fluid style="min-width: 960px">
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div
      v-if="dataLoaded && !dataLoadError"
      class="container pa-0"
      style="min-width: 960px"
    >
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Amendment</h1>
          <div style="padding-top: 25px; max-width: 875px">
            <p class="ma-0">
              This is the current information for this registration as of
              <b>{{ asOfDateTime }}.</b><br /><br />
              To view the full history of this registration including descriptions of any
              amendments and any court orders, you will need to conduct a separate search.
              <span v-if="registrationType === registrationTypeRL">
                <br /><br />The only amendment allowed for a Repairer's Lien is the
                removal of some (but not all) of the vehicle collateral.
              </span>
            </p>
          </div>
          <caution-box class="mt-9" :setMsg="cautionTxt" :setImportantWord="'Note'" />
          <registration-length-trust-amendment
            v-if="registrationType !== registrationTypeRL"
            :setShowErrorBar="errorBar"
            @lengthTrustOpen="lengthTrustOpen = $event"
            class="mt-15"
          />
          <registration-length-trust-summary class="mt-15" v-else />
          <div class="summary-header mt-15 pa-4 rounded-top">
            <v-icon color="darkBlue">mdi-account-multiple-plus</v-icon>
            <label class="pl-3">
              <strong>Registering Party, Secured Parties, and Debtors</strong>
            </label>
          </div>
          <h3 class="pt-6">Original Registering Party</h3>
          <registering-party-summary class="pt-4" :setEnableNoDataAction="false" />
          <h3 class="pt-6">Secured Parties</h3>
          <secured-parties
            v-if="registrationType !== registrationTypeRL"
            @setSecuredPartiesValid="setValidSecuredParties($event)"
            @securedPartyOpen="securedPartyOpen = $event"
            :setShowInvalid="showInvalid"
            class="pt-4"
            :setShowErrorBar="errorBar"
          />
          <div v-if="!securedPartiesValid">
            <span v-if="isCrownError()" class="invalid-message">
              Your registration can only include one secured party
            </span>
            <span v-else class="invalid-message">
              Your registration must include at least one Secured Party
            </span>
          </div>
          <secured-party-summary
            v-if="registrationType === registrationTypeRL"
            class="secured-party-summary"
            :setEnableNoDataAction="false"
          />
          <h3 class="pt-6">Debtors</h3>
          <debtors
            v-if="registrationType !== registrationTypeRL"
            @setDebtorValid="setValidDebtor($event)"
            @debtorOpen="debtorOpen = $event"
            :setShowInvalid="showInvalid"
            :setShowErrorBar="errorBar"
          />
          <div class="pt-4" v-if="!debtorValid">
            <span class="invalid-message">
              Your registration must include at least one Debtor
            </span>
          </div>
          <debtor-summary
            v-if="registrationType === registrationTypeRL"
            class="debtor-summary"
            :setEnableNoDataAction="false"
          />
          <collateral
            @setCollateralValid="setValidCollateral($event)"
            @collateralOpen="collateralOpen = $event"
            :setShowErrorBar="errorBar"
            class="mt-15"
          />
          <div class="pt-4" v-if="!collateralValid">
            <span class="invalid-message">
              Your registration must include at least one form of Collateral
            </span>
          </div>
          <amendment-description
            class="mt-12"
            @valid="detailsValid = $event"
            :setShowErrors="showInvalid"
          />
          <court-order
            class="mt-8"
            :setShowErrors="showCourtInvalid"
            :setRequireCourtOrder="requireCourtOrder"
            @setCourtOrderValid="setCourtOrderValid($event)"
          />
        </v-col>
        <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
                :setRightOffset="true"
                :setShowButtons="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setRegistrationType="registrationTypeUI"
                :setCancelBtn="'Cancel'"
                :setBackBtn="'Save and Resume Later'"
                :setSubmitBtn="'Review and Complete'"
                :setErrMsg="amendErrMsg"
                @cancel="cancel()"
                @submit="confirmAmendment()"
                @back="saveDraft()"
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
import { cloneDeep, isEqual } from 'lodash'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local components
import { CautionBox, StickyContainer, CourtOrder } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { Debtors } from '@/components/parties/debtor'
import { SecuredParties } from '@/components/parties/party'
import {
  AmendmentDescription,
  RegistrationLengthTrustAmendment,
  RegistrationLengthTrustSummary
} from '@/components/registration'
import { Collateral } from '@/components/collateral'
import {
  RegisteringPartySummary,
  SecuredPartySummary,
  DebtorSummary
} from '@/components/parties/summaries'
// local helpers/enums/interfaces/resources
import {
  APIRegistrationTypes, // eslint-disable-line no-unused-vars
  RouteNames, // eslint-disable-line no-unused-vars
  UIRegistrationTypes, // eslint-disable-line no-unused-vars
  RegistrationFlowType, // eslint-disable-line no-unused-vars
  ActionTypes
} from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Throttle } from '@/decorators'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  CertifyIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  AddCollateralIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  DebtorNameIF, // eslint-disable-line no-unused-vars
  CourtOrderIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF, // eslint-disable-line no-unused-vars
  FinancingStatementIF, // eslint-disable-line no-unused-vars
  RegTableNewItemI // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { AllRegistrationTypes } from '@/resources'
import { unsavedChangesDialog } from '@/resources/dialogOptions'
import {
  getFeatureFlag,
  getFinancingStatement,
  isSecuredPartyRestrictedList,
  pacificDate,
  saveAmendmentStatementDraft,
  setupAmendmentStatementFromDraft
} from '@/utils'

@Component({
  components: {
    AmendmentDescription,
    BaseDialog,
    CautionBox,
    CourtOrder,
    Collateral,
    Debtors,
    RegistrationLengthTrustAmendment,
    RegistrationLengthTrustSummary,
    RegisteringPartySummary,
    SecuredParties,
    SecuredPartySummary,
    DebtorSummary,
    StickyContainer
  }
})
export default class AmendRegistration extends Vue {
  @Getter getRegistrationType: RegistrationTypeIF;
  @Getter getAddSecuredPartiesAndDebtors: AddPartiesIF;
  @Getter getStateModel: StateModelIF;
  @Getter getLengthTrust: LengthTrustIF;
  @Getter getAmendmentDescription: string;
  @Getter getConfirmDebtorName: DebtorNameIF;
  @Getter getOriginalAddCollateral: AddCollateralIF;
  @Getter getOriginalAddSecuredPartiesAndDebtors: AddPartiesIF;
  @Getter getOriginalLengthTrust: LengthTrustIF;
  @Getter getAddCollateral: AddCollateralIF;
  @Getter getCourtOrderInformation: CourtOrderIF;
  @Getter hasUnsavedChanges: Boolean;

  @Action setAddCollateral: ActionBindingIF;
  @Action setStaffPayment: ActionBindingIF;
  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF;
  @Action setAmendmentDescription: ActionBindingIF;
  @Action setCourtOrderInformation: ActionBindingIF;
  @Action setFolioOrReferenceNumber: ActionBindingIF;
  @Action setLengthTrust: ActionBindingIF;
  @Action setOriginalAddCollateral: ActionBindingIF;
  @Action setOriginalAddSecuredPartiesAndDebtors: ActionBindingIF;
  @Action setOriginalLengthTrust: ActionBindingIF;
  @Action setRegistrationCreationDate: ActionBindingIF;
  @Action setRegistrationExpiryDate: ActionBindingIF;
  @Action setRegistrationNumber: ActionBindingIF;
  @Action setRegistrationType: ActionBindingIF;
  @Action setRegistrationFlowType: ActionBindingIF;
  @Action setCertifyInformation: ActionBindingIF;
  @Action setCollateralShowInvalid: ActionBindingIF;
  @Action setRegTableNewItem: ActionBindingIF;
  @Action setUnsavedChanges: ActionBindingIF;

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean;

  @Prop({ default: false })
  private isJestRunning: boolean;

  private cautionTxt =
    'The Registry will provide the verification statement to all Secured Parties named in this registration.';

  private dataLoaded = false; // eslint-disable-line lines-between-class-members
  private dataLoadError = false;
  private feeType = FeeSummaryTypes.AMEND;
  private financingStatementDate: Date = null;
  private debtorValid = true;
  private showInvalid = false;
  private showCourtInvalid = false;
  private securedPartiesValid = true;
  private registrationLengthTrustValid = true;
  private collateralValid = true;
  private courtOrderValid = true;
  private fromConfirmation = false;
  private requireCourtOrder = false;
  private debtorOpen = false;
  private securedPartyOpen = false;
  private errorBar = false;
  private collateralOpen = false;
  private lengthTrustOpen = false;
  private detailsValid = false;
  private amendErrMsg = '';
  private options: DialogOptionsIF = unsavedChangesDialog;
  private showCancelDialog = false;
  private submitting = false;

  private get asOfDateTime (): string {
    // return formatted date
    if (this.financingStatementDate) {
      return `${pacificDate(this.financingStatementDate)}`
    }
    return `${pacificDate(new Date())}`
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  // the number of the registration being amended
  private get registrationNumber (): string {
    let regNum = this.$route.query['reg-num'] as string
    if (regNum && regNum.endsWith('-confirm')) {
      this.fromConfirmation = true
      regNum = regNum.replace('-confirm', '')
    }
    return regNum || ''
  }

  // the draft document id if loading data after the base registration.
  private get documentId (): string {
    return (this.$route.query['document-id'] as string) || ''
  }

  private get registrationTypeUI (): UIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeUI || null
  }

  private get registrationType (): APIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeAPI || null
  }

  private get registrationTypeRL (): string {
    return APIRegistrationTypes.REPAIRERS_LIEN
  }

  private cancel (): void {
    if (this.hasUnsavedChanges) this.showCancelDialog = true
    else this.goToDashboard()
  }

  private handleDialogResp (val: boolean): void {
    this.showCancelDialog = false
    if (!val) this.goToDashboard()
  }

  private async loadRegistration (): Promise<void> {
    if (!this.registrationNumber || (!this.getConfirmDebtorName && !this.documentId)) {
      if (!this.registrationNumber) {
        console.error(
          'No registration number given to amend. Redirecting to dashboard...'
        )
      } else {
        console.error(
          'No debtor name confirmed for this amendment. Redirecting to dashboard...'
        )
      }
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      return
    }
    // Conditionally load: could be coming back from confirm.
    if (this.fromConfirmation) {
      return
    }
    this.financingStatementDate = new Date()
    this.submitting = true
    const financingStatement = await getFinancingStatement(true, this.registrationNumber)
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
  }

  private async setStore (financingStatement: FinancingStatementIF): Promise<void> {
    // load data into the store
    const registrationType = AllRegistrationTypes.find((reg, index) => {
      if (reg.registrationTypeAPI === financingStatement.type) {
        return true
      }
    })
    const collateral = {
      valid: true,
      vehicleCollateral: financingStatement.vehicleCollateral || null,
      generalCollateral: financingStatement.generalCollateral
    } as AddCollateralIF
    const lengthTrust = {
      valid: true,
      trustIndenture: financingStatement.trustIndenture || false,
      lifeInfinite: financingStatement.lifeInfinite || false,
      lifeYears: financingStatement.lifeYears || null,
      surrenderDate: financingStatement.surrenderDate || null,
      lienAmount: financingStatement.lienAmount || null
    } as LengthTrustIF
    const parties = {
      valid: true,
      registeringParty: null, // will be taken from account info
      securedParties: financingStatement.securedParties,
      debtors: financingStatement.debtors
    } as AddPartiesIF
    const origParties = {
      registeringParty: financingStatement.registeringParty, // will be used for summary
      securedParties: financingStatement.securedParties,
      debtors: financingStatement.debtors
    } as AddPartiesIF
    const courtOrder: CourtOrderIF = {
      courtRegistry: '',
      courtName: '',
      fileNumber: '',
      effectOfOrder: '',
      orderDate: ''
    }
    const certifyInfo: CertifyIF = {
      valid: false,
      certified: false,
      legalName: '',
      registeringParty: null
    }
    this.setRegistrationCreationDate(financingStatement.createDateTime)
    this.setRegistrationExpiryDate(financingStatement.expiryDate)
    this.setRegistrationNumber(financingStatement.baseRegistrationNumber)
    this.setRegistrationType(registrationType)
    this.setAddCollateral(collateral)
    this.setLengthTrust(lengthTrust)
    this.setAddSecuredPartiesAndDebtors(cloneDeep(parties))
    this.setOriginalAddCollateral(cloneDeep(collateral))
    this.setOriginalLengthTrust(cloneDeep(lengthTrust))
    this.setOriginalAddSecuredPartiesAndDebtors(cloneDeep(origParties))
    this.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    // Reset anything left in the store that is amendment registration related.
    this.setAmendmentDescription('')
    this.setCourtOrderInformation(courtOrder)
    this.setFolioOrReferenceNumber('')
    this.setCertifyInformation(certifyInfo)
    this.setStaffPayment({
      option: -1,
      routingSlipNumber: '',
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: '',
      isPriority: false
    })
    if (this.documentId) {
      const stateModel: StateModelIF = await setupAmendmentStatementFromDraft(
        this.getStateModel,
        this.documentId
      )
      if (stateModel.registration.draft.error) {
        this.emitError(stateModel.registration.draft.error)
        this.$router.push({ name: RouteNames.DASHBOARD })
      } else {
        this.setAddCollateral(stateModel.registration.collateral)
        this.setLengthTrust(stateModel.registration.lengthTrust)
        this.setAddSecuredPartiesAndDebtors(stateModel.registration.parties)
        if (stateModel.registration.amendmentDescription) {
          this.setAmendmentDescription(stateModel.registration.amendmentDescription)
        }
        if (stateModel.registration.courtOrderInformation) {
          this.setCourtOrderInformation(stateModel.registration.courtOrderInformation)
        }
      }
    }
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  private async scrollToInvalid (): Promise<void> {
    if (this.lengthTrustOpen || !this.registrationLengthTrustValid) {
      const component = document.getElementById('length-trust-amendment')
      if (component) {
        await component.scrollIntoView({ behavior: 'smooth' })
        return
      }
    }
    if (this.securedPartyOpen || !this.securedPartiesValid) {
      const component = document.getElementById('secured-parties-component')
      if (component) {
        await component.scrollIntoView({ behavior: 'smooth' })
        return
      }
    }

    if (this.debtorOpen || !this.debtorValid) {
      const component = document.getElementById('debtors-component')
      if (component) {
        await component.scrollIntoView({ behavior: 'smooth' })
        return
      }
    }
    if (this.collateralOpen || !this.collateralValid) {
      const component = document.getElementById('collateral-component')
      if (component) {
        await component.scrollIntoView({ behavior: 'smooth' })
      }
    }

    if (!this.courtOrderValid) {
      const component = document.getElementById('court-order')
      if (component) {
        await component.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }

  private confirmAmendment (): void {
    this.validateSecuredParties()
    this.validateDebtors()
    if (
      this.collateralOpen ||
      this.securedPartyOpen ||
      this.debtorOpen ||
      this.lengthTrustOpen
    ) {
      this.amendErrMsg = '< You have unfinished changes'
      this.showInvalid = true
      this.errorBar = true
      this.scrollToInvalid()
      return
    }
    if (!this.hasAmendmentChanged() || !this.debtorValid || !this.securedPartiesValid) {
      this.amendErrMsg = '< Please make any required changes'
      return
    }
    const description = this.getAmendmentDescription
    if (
      this.debtorValid &&
      this.securedPartiesValid &&
      this.registrationLengthTrustValid &&
      this.collateralValid &&
      (!description || description.length <= 4000) &&
      this.courtOrderValid
    ) {
      this.$router.push({
        name: RouteNames.CONFIRM_AMENDMENT,
        query: { 'reg-num': this.registrationNumber }
      })
      this.emitHaveData(false)
    } else {
      this.showInvalid = true
      if (!this.collateralValid) {
        this.setCollateralShowInvalid(true)
      }
      if (!this.courtOrderValid) {
        this.showCourtInvalid = true
        this.amendErrMsg = '< You have unfinished changes'
      }
      this.scrollToInvalid()
    }
  }

  private hasAmendmentChanged (): boolean {
    let hasChanged = false
    if (
      !isEqual(
        this.getAddSecuredPartiesAndDebtors.securedParties,
        this.getOriginalAddSecuredPartiesAndDebtors.securedParties
      )
    ) {
      hasChanged = true
    }
    if (
      !isEqual(
        this.getAddSecuredPartiesAndDebtors.debtors,
        this.getOriginalAddSecuredPartiesAndDebtors.debtors
      )
    ) {
      hasChanged = true
    }
    if (!isEqual(this.getLengthTrust, this.getOriginalLengthTrust)) {
      hasChanged = true
    }
    if (
      !isEqual(
        this.getAddCollateral.vehicleCollateral,
        this.getOriginalAddCollateral.vehicleCollateral
      )
    ) {
      hasChanged = true
    }
    const gcLength = this.getAddCollateral.generalCollateral?.length
    const originalLength = this.getOriginalAddCollateral.generalCollateral?.length
    if (gcLength !== originalLength) {
      hasChanged = true
    }

    if (this.getAmendmentDescription) {
      hasChanged = true
    }

    const blankCourtOrder: CourtOrderIF = {
      courtName: '',
      courtRegistry: '',
      effectOfOrder: '',
      fileNumber: '',
      orderDate: ''
    }
    if (!isEqual(this.getCourtOrderInformation, blankCourtOrder)) {
      hasChanged = true
    }
    return hasChanged
  }

  @Throttle(2000)
  private async saveDraft (): Promise<void> {
    this.submitting = true
    const stateModel: StateModelIF = this.getStateModel
    const draft = await saveAmendmentStatementDraft(stateModel)
    this.submitting = false
    if (draft.error) {
      this.emitError(draft.error)
    } else {
      this.setUnsavedChanges(false)
      const prevDraftId =
        stateModel.registration?.draft?.amendmentStatement?.documentId || ''
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

  private goToDashboard (): void {
    // unset registration number
    this.setRegistrationNumber(null)
    this.$router.push({ name: RouteNames.DASHBOARD })
  }

  private setCourtOrderValid (valid): void {
    this.courtOrderValid = valid
    if (valid) {
      this.showCourtInvalid = false
      this.amendErrMsg = ''
    }
  }

  /** Emits error to app.vue for handling */
  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void {}

  /** Called when App is ready and this component can load its data. */
  @Watch('appReady')
  private async onAppReady (val: boolean): Promise<void> {
    // do not proceed if app is not ready
    if (!val) return
    // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
    if (
      !this.isAuthenticated ||
      (!this.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))
    ) {
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

  private setValidSecuredParties (val: boolean) {
    if (!val) {
      this.showInvalid = true
      this.amendErrMsg = '< Please make any required changes'
    } else {
      this.amendErrMsg = ''
    }
    this.securedPartiesValid = val
  }

  private setValidDebtor (val: boolean) {
    if (!val) {
      this.showInvalid = true
      this.amendErrMsg = '< Please make any required changes'
    } else {
      this.amendErrMsg = ''
    }
    this.debtorValid = val
  }

  private validateSecuredParties (): void {
    const sp = this.getAddSecuredPartiesAndDebtors.securedParties
    let securedPartyCount = 0
    if (this.registrationType === APIRegistrationTypes.SECURITY_AGREEMENT) {
      for (let i = 0; i < sp.length; i++) {
        // is valid if there is at least one secured party
        if (sp[i].action !== ActionTypes.REMOVED) {
          securedPartyCount++
        }
      }
      if (securedPartyCount >= 1) {
        this.setValidSecuredParties(true)
      } else {
        this.setValidSecuredParties(false)
      }
    }
  }

  private validateDebtors (): void {
    const sp = this.getAddSecuredPartiesAndDebtors.debtors
    let debtorCount = 0
    if (this.registrationType === APIRegistrationTypes.SECURITY_AGREEMENT) {
      for (let i = 0; i < sp.length; i++) {
        // is valid if there is at least one secured party
        if (sp[i].action !== ActionTypes.REMOVED) {
          debtorCount++
        }
      }
      if (debtorCount >= 1) {
        this.setValidDebtor(true)
      } else {
        this.setValidDebtor(false)
      }
    }
  }

  private isCrownError (): boolean {
    const sp = this.getAddSecuredPartiesAndDebtors.securedParties
    let securedPartyCount = 0
    if (isSecuredPartyRestrictedList(this.registrationType)) {
      for (let i = 0; i < sp.length; i++) {
        // is valid if there is at least one secured party
        if (sp[i].action !== ActionTypes.REMOVED) {
          securedPartyCount++
        }
      }
      if (securedPartyCount > 1) {
        return true
      }
    }
    return false
  }

  private setValidCollateral (val: boolean) {
    if (!val) {
      this.showInvalid = true
      this.errorBar = true
      const collateral = this.getAddCollateral
      collateral.showInvalid = true
      this.setAddCollateral(collateral)
      this.amendErrMsg = '< Please make any required changes'
    } else {
      this.amendErrMsg = ''
      this.errorBar = false
    }
    this.collateralValid = val
  }

  @Watch('securedPartyOpen')
  @Watch('debtorOpen')
  @Watch('collateralOpen')
  @Watch('lengthTrustOpen')
  private resetOpenError (isOpen: boolean): void {
    if (!isOpen) {
      this.errorBar = false
      this.amendErrMsg = ''
    }
  }

  @Watch('detailsValid')
  private resetValidationError (isValid: boolean): void {
    if (isValid) {
      this.errorBar = false
      this.amendErrMsg = ''
    }
  }
}
</script>

<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
.invalid-message {
  font-size: 14px;
}
</style>
