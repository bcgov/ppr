<template>
  <v-container v-if="dataLoaded" class="view-container pa-15" fluid style="min-width: 960px;">
    <div class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Total Discharge</h1>
          <div style="padding-top: 30px; max-width: 875px;">
            <p class="ma-0">
              Confirm and complete any additional information before submitting this Total Discharge.
            </p>
          </div>
          <caution-box class="mt-10" :setMsg="cautionTxt"/>
          <h2 class="pt-15">
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
          <registering-party-summary class="pt-4" :setEnableNoDataAction="false" />
        </v-col>
        <v-col class="pl-6" cols="3">
          <registration-fee :registrationType="'Total Discharge'" />
          <buttons-stacked
            class="pt-4"
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
import { ButtonsStacked, CautionBox, RegistrationFee } from '@/components/common'
import { RegisteringPartySummary } from '@/components/parties/summaries'
// local helpers/enums/interfaces/resources
import { APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import {
  ActionBindingIF, FeeSummaryIF, ErrorIF, AddPartiesIF, RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationTypes } from '@/resources'
import { convertDate, getFeatureFlag, getFinancingStatement } from '@/utils'
import { StatusCodes } from 'http-status-codes'

@Component({
  components: {
    ButtonsStacked,
    CautionBox,
    RegistrationFee,
    RegisteringPartySummary
  }
})
export default class ConfirmDischarge extends Vue {
  @Getter getRegistrationType: RegistrationTypeIF

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

  private cautionTxt = 'Secured Parties in this registration ' +
    'will receive a copy of the Total Discharge Verification Statement.'
  private dataLoaded = false // eslint-disable-line lines-between-class-members
  private financingStatementDate: Date = null
  private tooltipTxt = 'The Registering Party is based on your ' +
    'account information and cannot be changed here. This information ' +
    'can be changed by updating your BC Registries account information.'

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
    return this.$route.query['reg-num'] as string || ''
  }

  private get registrationTypeUI (): UIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeUI || null
  }

  private get registrationType (): APIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeAPI || null
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
    const financingStatement = await getFinancingStatement(true, this.registrationNumber)
    if (financingStatement.error) {
      this.emitError(financingStatement.error)
    } else {
      // load data into the store
      const registrationType = RegistrationTypes.find(
        (reg, index) => {
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
      const feeSummary = {
        feeAmount: 0,
        serviceFee: 1.50,
        quantity: 1,
        feeCode: ''
      } as FeeSummaryIF
      this.setRegistrationCreationDate(financingStatement.createDateTime)
      this.setRegistrationExpiryDate(financingStatement.expiryDate)
      this.setRegistrationNumber(financingStatement.baseRegistrationNumber)
      this.setRegistrationType(registrationType)
      this.setAddSecuredPartiesAndDebtors(parties)
      this.setFeeSummary(feeSummary)
    }
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  private goToReviewRegistration (): void {
    this.$router.push({
      name: RouteNames.REVIEW_DISCHARGE,
      query: { 'reg-num': this.registrationNumber }
    })
    this.emitHaveData(false)
  }

  private showDialog (): void {
    // TBD
    console.log('show dialog')
  }

  private submitDischarge (): void {
    // TBD
    console.log('submit')
  }

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void { }

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
    if (error.statusCode === StatusCodes.NOT_FOUND) alert('This registration does not exist.')
    else if (error.statusCode === StatusCodes.BAD_REQUEST) alert('You do not have access to this registration.')
    else alert('There was an internal error loading this registration. Please try again later.')
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
