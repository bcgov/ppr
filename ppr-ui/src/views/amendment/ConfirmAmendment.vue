<template>
  <v-container
    v-if="dataLoaded"
    id="confirm-amendment"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <base-dialog
      setAttach="#confirm-amendment"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="cancel($event)"
    />
    <div class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Review and Confirm</h1>
          <caution-box class="mt-9" :setMsg="cautionTxt" />

          <v-row no-gutters class="summary-header pa-2 mt-4">
            <v-col cols="10" class="pa-2">
              <label class="pl-3">
                <strong>Amendment</strong>
              </label>
            </v-col>
            <v-col cols="2" class="pl-10">
                <v-btn
                  text
                  color="primary"
                  :class="[$style['smaller-button'], 'edit-btn']"
                  id="confirm-amend-btn"
                  @click="goToReviewAmendment()"
                >
                  <v-icon small>mdi-pencil</v-icon>
                  <span>Amend</span>
                </v-btn>
            </v-col>
          </v-row>
          <div class="white ma-0">
            <div v-if="showSecuredParties" class="pa-4">
              <h3>Secured Parties</h3>
              <secured-party-summary
                class="secured-party-summary"
                :setEnableNoDataAction="true"
              />
            </div>

            <div v-if="showDebtors" class="pa-4">
              <v-divider v-if="showSecuredParties"></v-divider>
              <h3>Debtors</h3>
              <debtor-summary
                class="debtor-summary"
                :setEnableNoDataAction="true"
              />
            </div>

            <div v-if="showVehicleCollateral || showGeneralCollateral">
              <!-- To do: add amended collateral -->
              <div v-if="showVehicleCollateral">
                <v-divider v-if="showSecuredParties || showDebtors"></v-divider>
                <vehicle-collateral
                  :isSummary="true"
                  :showInvalid="false"
                />
              </div>
              <div v-if="showGeneralCollateral">
                <v-divider v-if="showSecuredParties || showDebtors || showVehicleCollateral"></v-divider>
                <!-- To do: add general collateral summary -->
              </div>
            </div>

            <div class="pb-4">
              <v-divider v-if="showSecuredParties || showDebtors || showVehicleCollateral ||
                               showGeneralCollateral"></v-divider>
              <amendment-description class="pt-14" :isSummary="true" />
            </div>

            <div v-if="showCourtOrder">
              <v-divider></v-divider>
              <!-- To do: add court order summary -->
            </div>

            <div v-if="showLengthTrustIndenture">
              <v-divider></v-divider>
              <registration-length-trust-amendment class="pt-14" :isSummary="true" />
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
          <registering-party-summary
            class="pt-4"
            :setEnableNoDataAction="false"
          />
          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-10"
          />
          <!-- Certify goes here when available -->
        </v-col>
        <v-col class="pl-6" cols="3">
          <sticky-container
            :setErrMsg="stickyComponentErrMsg"
            :setRightOffset="true"
            :setShowButtons="true"
            :setShowFeeSummary="true"
            :setFeeType="feeType"
            :setRegistrationLength="registrationLength"
            :setRegistrationType="registrationTypeUI"
            :setBackBtn="'Save and Resume Later'"
            :setCancelBtn="'Cancel'"
            :setSubmitBtn="'Register and Pay'"
            @back="saveDraft()"
            @cancel="showDialog()"
            @submit="submitAmendment()"
          />
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
  FolioNumberSummary,
  StickyContainer
} from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { RegisteringPartySummary, SecuredPartySummary, DebtorSummary } from '@/components/parties/summaries'
import { AmendmentDescription, RegistrationLengthTrustAmendment } from '@/components/registration'
import { VehicleCollateral } from '@/components/collateral/vehicleCollateral'

// local helpers/enums/interfaces/resources
import { APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  AddCollateralIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  AmendmentStatementIF, // eslint-disable-line no-unused-vars
  CourtOrderIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF, // eslint-disable-line no-unused-vars
  DebtorNameIF, // eslint-disable-line no-unused-vars
  DraftIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars

import { RegistrationTypes } from '@/resources'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  convertDate,
  getFeatureFlag,
  getFinancingStatement,
  saveAmendmentStatement,
  saveAmendmentStatementDraft
} from '@/utils'
import { StatusCodes } from 'http-status-codes'

@Component({
  components: {
    AmendmentDescription,
    BaseDialog,
    CautionBox,
    FolioNumberSummary,
    RegisteringPartySummary,
    SecuredPartySummary,
    DebtorSummary,
    VehicleCollateral,
    RegistrationLengthTrustAmendment,
    StickyContainer
  }
})
export default class ConfirmAmendment extends Vue {
  @Getter getAddCollateral: AddCollateralIF
  @Getter getAddSecuredPartiesAndDebtors: AddPartiesIF
  @Getter getAmendmentDescription: string
  @Getter getConfirmDebtorName: DebtorNameIF
  @Getter getCourtOrderInformation: CourtOrderIF
  @Getter getLengthTrust: LengthTrustIF
  @Getter getRegistrationNumber: string
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getStateModel: StateModelIF

  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF
  @Action setFeeSummary: ActionBindingIF
  @Action setRegistrationCreationDate: ActionBindingIF
  @Action setRegistrationExpiryDate: ActionBindingIF
  @Action setRegistrationNumber: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private collateralSummary = '' // eslint-disable-line lines-between-class-members
  private dataLoaded = false
  private financingStatementDate: Date = null
  private options: DialogOptionsIF = {
    acceptText: 'Cancel Amendment',
    cancelText: 'Close',
    title: 'Cancel',
    label: '',
    text: 'This will discard all changes made and return you to My Personal Property Registry dashboard.'
  }

  private showCancelDialog = false
  private showErrors = false

  private cautionTxt =
    'The Secured Parties in the registration ' +
    'will receive a copy of the Amendment Verification Statement.'

  private tooltipTxt = 'The Registering Party is based on your ' +
    'account information and cannot be changed here. This information ' +
    'can be changed by updating your BC Registries account information.'

  private validFolio = true
  private feeType = FeeSummaryTypes.AMEND

  private get asOfDateTime (): string {
    // return formatted date
    if (this.financingStatementDate) {
      return `${convertDate(this.financingStatementDate, true, true)}`
    }
    return ''
  }

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

  private get detailDescription (): string {
    return this.getAmendmentDescription || ''
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
      if (addCollateral.generalCollateral[i].descriptionAdd || addCollateral.generalCollateral[i].descriptionDelete) {
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
            (courtOrder.courtName.length > 0 &&
            courtOrder.courtRegistry.length > 0 &&
            courtOrder.fileNumber.length > 0 &&
            courtOrder.orderDate.length > 0 &&
            courtOrder.effectOfOrder.length > 0))
  }

  private get stickyComponentErrMsg (): string {
    if (!this.validFolio && this.showErrors) {
      return '< Please complete required information'
    }
    return ''
  }

  private cancel (val: boolean): void {
    this.showCancelDialog = false
    if (val) {
      this.$router.push({ name: RouteNames.DASHBOARD })
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
    const financingStatement = await getFinancingStatement(
      true,
      this.registrationNumber
    )
    if (financingStatement.error) {
      this.emitError(financingStatement.error)
    } else {
      // load data into the store
      const registrationType = RegistrationTypes.find((reg, index) => {
        if (reg.registrationTypeAPI === financingStatement.type) {
          return true
        }
      })
      const parties = {
        valid: true,
        registeringParty: financingStatement.registeringParty,
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

  private goToReviewAmendment (): void {
    this.$router.push({
      name: RouteNames.AMEND_REGISTRATION,
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

  private async saveDraft (): Promise<void> {
    const stateModel: StateModelIF = this.getStateModel
    const draft: DraftIF = await saveAmendmentStatementDraft(stateModel)
    if (draft.error !== undefined) {
      console.log(
        'saveDraft error status: ' + draft.error.statusCode + ' message: ' + draft.error.message
      )
    }
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
    this.emitHaveData(false)
  }

  private async submitAmendment (): Promise<void> {
    if (!this.validFolio) {
      this.showErrors = true
      return
    }

    // Incomplete validation check: all changes must be valid to submit registration.
    if (this.collateralValid && this.partiesValid && this.courtOrderValid) {
      const stateModel: StateModelIF = this.getStateModel
      const apiResponse: AmendmentStatementIF = await saveAmendmentStatement(stateModel)
      if (apiResponse === undefined || apiResponse?.error !== undefined) {
        console.error(apiResponse.error)
        alert('There was an internal error attempting to save this amendment. Please try again later.')
      } else {
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

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
    if (error.statusCode === StatusCodes.NOT_FOUND) {
      alert('This registration does not exist.')
    } else if (error.statusCode === StatusCodes.BAD_REQUEST) {
      alert('You do not have access to this registration.')
    } else {
      alert('There was an internal error loading this registration. Please try again later.')
    }
    this.emitHaveData(true)
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
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
    try {
      await this.loadRegistration()
    } catch (error) {
      console.error(error)
      this.emitError({
        statusCode: 500,
        message: error
      })
    }

    // page is ready to view
    this.emitHaveData(true)
    this.dataLoaded = true
  }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.border-btm {
  border-bottom: 1px solid $gray3;
}
</style>
