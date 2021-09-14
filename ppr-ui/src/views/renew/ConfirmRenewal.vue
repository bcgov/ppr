<template>
  <v-container
    v-if="dataLoaded"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <div class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Renewal</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Confirm and complete any additional information before submitting
              this registration Renewal.
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
          <registering-party-summary
            class="pt-4"
            :setEnableNoDataAction="false"
          />
          <registration-length-trust class="mt-15" :isRenewal="true"
          :isSummary="true" :defaultRegistrationType="registrationType" />
          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-10"
          />
        </v-col>
        <v-col class="pl-6" cols="3">
          <fee-summary
              :setFeeType="feeType"
              :setRegistrationLength="registrationLength"
              :setRegistrationType="registrationTypeUI"
            />
          <buttons-stacked
            class="pt-4"
            :setBackBtn="'Back'"
            :setCancelBtn="'Cancel'"
            :setSubmitBtn="'Submit Renewal'"
            @back="goToReviewRenewal()"
            @cancel="showDialog()"
            @submit="submitRenewal()"
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
  ButtonsStacked,
  FolioNumberSummary
} from '@/components/common'
import { RegisteringPartySummary } from '@/components/parties/summaries'
import { RegistrationLengthTrust } from '@/components/registration'

// local helpers/enums/interfaces/resources
import { APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  RenewRegistrationIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  LengthTrustIF // eslint-disable-line no-unused-vars
} from '@/interfaces'

import { RegistrationTypes } from '@/resources'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { convertDate, getFeatureFlag, getFinancingStatement, saveRenewal } from '@/utils'
import { StatusCodes } from 'http-status-codes'
import { FeeSummary } from '@/composables/fees'
import { FeeSummaryI, RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars

@Component({
  components: {
    ButtonsStacked,
    RegistrationLengthTrust,
    FeeSummary,
    FolioNumberSummary,
    RegisteringPartySummary
  }
})
export default class ConfirmDischarge extends Vue {
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getStateModel: StateModelIF
  @Getter getLengthTrust: LengthTrustIF

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
  private showErrors = false
  private tooltipTxt = 'The Registering Party is based on your ' +
    'account information and cannot be changed here. This information ' +
    'can be changed by updating your BC Registries account information.'

  private validFolio = true
  private feeType = FeeSummaryTypes.RENEW

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

  private showDialog (): void {
    // TBD
    console.log('show dialog')
  }

  private async submitRenewal (): Promise<void> {
    if (!this.validFolio) {
      this.showErrors = true
      return
    }

    const stateModel: StateModelIF = this.getStateModel
    const apiResponse: RenewRegistrationIF = await saveRenewal(stateModel)
    if (apiResponse === undefined || apiResponse?.error !== undefined) {
      console.error(apiResponse.error)
      alert('There was an internal error attempting to save this renewal. Please try again later.')
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
