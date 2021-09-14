<template>
  <v-container
    v-if="dataLoaded"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <base-dialog
      attach="#app"
      :options="options"
      :display="showCancelDialog"
      @proceed="cancel($event)"
    />
    <div class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Total Discharge</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Confirm and complete any additional information before submitting
              this Total Discharge.
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
          <registering-party-summary
            class="pt-4"
            :setEnableNoDataAction="false"
          />
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
        </v-col>
        <v-col class="pl-6" cols="3">
          <sticky-container
            :setErrMsg="stickyComponentErrMsg"
            :setRightOffset="true"
            :setShowButtons="true"
            :setShowFeeSummary="true"
            :setFeeType="feeType"
            :setRegistrationType="registrationTypeUI"
            :setBackBtn="'Back'"
            :setCancelBtn="'Cancel'"
            :setSubmitBtn="'Submit Total Discharge'"
            @back="goToReviewRegistration()"
            @cancel="showDialog()"
            @submit="submitDischarge()"
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
  DischargeConfirmSummary,
  FolioNumberSummary,
  StickyContainer
} from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { RegisteringPartySummary } from '@/components/parties/summaries'
// local helpers/enums/interfaces/resources
import { APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  DischargeRegistrationIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationTypes, dischargeCancelDialog } from '@/resources'
import { convertDate, getFeatureFlag, getFinancingStatement, saveDischarge } from '@/utils'
import { StatusCodes } from 'http-status-codes'

@Component({
  components: {
    BaseDialog,
    CautionBox,
    DischargeConfirmSummary,
    FolioNumberSummary,
    RegisteringPartySummary,
    StickyContainer
  }
})
export default class ConfirmDischarge extends Vue {
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getStateModel: StateModelIF

  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF
  @Action setRegistrationCreationDate: ActionBindingIF
  @Action setRegistrationExpiryDate: ActionBindingIF
  @Action setRegistrationNumber: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private cautionTxt = 'Secured Parties in this registration ' +
    'will receive a copy of the Total Discharge Verification Statement.'
  private collateralSummary = '' // eslint-disable-line lines-between-class-members
  private dataLoaded = false
  private feeType = FeeSummaryTypes.DISCHARGE
  private financingStatementDate: Date = null
  private options: DialogOptionsIF = dischargeCancelDialog
  private showCancelDialog = false
  private showErrors = false
  private tooltipTxt = 'The Registering Party is based on your ' +
    'account information and cannot be changed here. This information ' +
    'can be changed by updating your BC Registries account information.'
  private validConfirm = false // eslint-disable-line lines-between-class-members
  private validFolio = true

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

  private get stickyComponentErrMsg (): string {
    if ((!this.validConfirm || !this.validFolio) && this.showErrors) {
      return '< Please complete required information'
    }
    return ''
  }

  private async loadRegistration (): Promise<void> {
    if (!this.registrationNumber) {
      console.error('No registration number given to discharge. Redirecting to dashboard...')
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

  private cancel (val: boolean): void {
    this.showCancelDialog = false
    if (val) {
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

  private async submitDischarge (): Promise<void> {
    if (!this.validConfirm || !this.validFolio) {
      this.showErrors = true
      return
    }

    const stateModel: StateModelIF = this.getStateModel
    const apiResponse: DischargeRegistrationIF = await saveDischarge(stateModel)
    if (apiResponse === undefined || apiResponse?.error !== undefined) {
      console.error(apiResponse.error)
      alert('There was an internal error attempting to save this Discharge registration. Please try again later.')
    } else {
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
</style>
