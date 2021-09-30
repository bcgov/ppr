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
          <h1>Registration Amendment</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review the current information for this registration as of
              <b>{{ asOfDateTime }}.</b><br />
            </p>
          </div>
          <caution-box class="mt-9" :setMsg="cautionTxt" />
          <registration-length-trust
            class="mt-15"
            :isSummary="true"
            @setRegistrationLengthTrustValid="
              registrationLengthTrustValid = $event
            "
          />
          <div class="summary-header mt-15 pa-4 rounded-top">
            <v-icon color="darkBlue">mdi-account-multiple-plus</v-icon>
            <label class="pl-3">
              <strong>Registering Party, Secured Parties, and Debtors</strong>
            </label>
          </div>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              The Registering Party has been added based on your account
              information and cannot be changed here.
            </p>
          </div>
          <h3 class="pt-6 px-1">Original Registering Party</h3>
          <registering-party-summary
            class="pt-4"
            :setEnableNoDataAction="false"
          />
          <h3 class="pt-6 px-1">Secured Parties</h3>
          <secured-parties
            @setSecuredPartiesValid="securedPartiesValid = $event"
            :setShowInvalid="showInvalid" class="pt-4"
          />
          <h3 class="pt-6 px-1">Debtors</h3>
          <debtors
            @setDebtorValid="debtorValid = $event"
            :setShowInvalid="showInvalid"
          />
          <collateral
            :setRegistrationType="registrationType"
            @setCollateralValid="collateralValid = $event"
            class="mt-15"
          />
        </v-col>
        <v-col class="pl-6" cols="3">
          <sticky-container
            :setRightOffset="true"
            :setShowButtons="true"
            :setShowFeeSummary="true"
            :setFeeType="feeType"
            :setRegistrationType="registrationTypeUI"
            :setCancelBtn="'Cancel'"
            :setBackBtn="'Save and Resume Later'"
            :setSubmitBtn="'Review and Complete'"
            @cancel="goToDashboard()"
            @submit="confirmAmendment()"
            @back="saveDraft()"
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
import { CautionBox, StickyContainer } from '@/components/common'
import { Debtors, SecuredParties } from '@/components/parties'
import { RegistrationLengthTrust } from '@/components/registration'
import { Collateral } from '@/components/collateral'
import { RegisteringPartySummary } from '@/components/parties/summaries'
// local helpers/enums/interfaces/resources
import {
  APIRegistrationTypes, // eslint-disable-line no-unused-vars
  RouteNames, // eslint-disable-line no-unused-vars
  UIRegistrationTypes, // eslint-disable-line no-unused-vars
  RegistrationFlowType // eslint-disable-line no-unused-vars
} from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  AddCollateralIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  DraftIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationTypes } from '@/resources'
import {
  convertDate,
  getFeatureFlag,
  getFinancingStatement,
  saveAmendmentStatementDraft
} from '@/utils'
import { cloneDeep } from 'lodash'
import { StatusCodes } from 'http-status-codes'

@Component({
  components: {
    CautionBox,
    RegistrationLengthTrust,
    Collateral,
    Debtors,
    RegisteringPartySummary,
    SecuredParties,
    StickyContainer
  }
})
export default class AmendRegistration extends Vue {
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getAddSecuredPartiesAndDebtors: AddPartiesIF
  @Getter getStateModel: StateModelIF

  @Action setAddCollateral: ActionBindingIF
  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF
  @Action setLengthTrust: ActionBindingIF
  @Action setOriginalAddCollateral: ActionBindingIF
  @Action setOriginalAddSecuredPartiesAndDebtors: ActionBindingIF
  @Action setOriginalLengthTrust: ActionBindingIF
  @Action setRegistrationCreationDate: ActionBindingIF
  @Action setRegistrationExpiryDate: ActionBindingIF
  @Action setRegistrationNumber: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF
  @Action setRegistrationFlowType: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private cautionTxt =
    'Secured Parties in this registration ' +
    'will receive a copy of the Amendment Verification Statement.'
  private dataLoaded = false // eslint-disable-line lines-between-class-members
  private feeType = FeeSummaryTypes.AMEND
  private financingStatementDate: Date = null
  private debtorValid = true
  private showInvalid = false
  private securedPartiesValid = true
  private registrationLengthTrustValid = true
  private collateralValid = true

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

  // the number of the registration being amended
  private get registrationNumber (): string {
    return (this.$route.query['reg-num'] as string) || ''
  }

  private get registrationTypeUI (): UIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeUI || null
  }

  private get registrationType (): APIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeAPI || null
  }

  private async loadRegistration (): Promise<void> {
    if (!this.registrationNumber) {
      console.error('No registration number given to amend. Redirecting to dashboard...')
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
      const registrationType = RegistrationTypes.find((reg, index) => {
        if (reg.registrationTypeAPI === financingStatement.type) {
          return true
        }
      })
      const collateral = {
        valid: true,
        vehicleCollateral: financingStatement.vehicleCollateral,
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
        registeringParty: financingStatement.registeringParty,
        securedParties: financingStatement.securedParties,
        debtors: financingStatement.debtors
      } as AddPartiesIF
      this.setRegistrationCreationDate(financingStatement.createDateTime)
      this.setRegistrationExpiryDate(financingStatement.expiryDate)
      this.setRegistrationNumber(financingStatement.baseRegistrationNumber)
      this.setRegistrationType(registrationType)
      this.setAddCollateral(collateral)
      this.setLengthTrust(lengthTrust)
      this.setAddSecuredPartiesAndDebtors(parties)
      this.setOriginalAddCollateral(cloneDeep(collateral))
      this.setOriginalLengthTrust(cloneDeep(lengthTrust))
      this.setOriginalAddSecuredPartiesAndDebtors(cloneDeep(parties))
      this.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    }
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  private confirmAmendment (): void {
    if (
      this.debtorValid &&
      this.securedPartiesValid &&
      this.registrationLengthTrustValid &&
      this.collateralValid
    ) {
      this.$router.push({
        name: RouteNames.CONFIRM_AMENDMENT,
        query: { 'reg-num': this.registrationNumber }
      })
      this.emitHaveData(false)
    } else {
      this.showInvalid = true
    }
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
