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
              This is the current registration information as of
              <b>{{ asOfDateTime }}.</b> Review this information to ensure it is
              correct
              <span v-if="registrationType !== registrationTypeRL">
                and select the length of time you would like to renew this
                registration for</span
              >.<br />
            </p>
            <p class="ma-0 pt-5">
              To view the full history of this registration including
              descriptions of any previous amendments or court orders, you will
              need to conduct a separate search.
            </p>
          </div>
          <registration-length-trust
            :setShowInvalid="showInvalid"
            @lengthTrustValid="registrationValid = $event"
            v-if="registrationType !== registrationTypeRL"
            class="mt-15"
            :isRenewal="true"
          />
          <registration-repairers-lien v-else class="mt-15" :isRenewal="true" />
          <div class="summary-header mt-15 pa-4 rounded-top">
            <v-icon color="darkBlue">mdi-account-multiple-plus</v-icon>
            <label class="pl-3">
              <strong>Registering Party, Secured Parties, and Debtors</strong>
            </label>
          </div>
          <h3 class="pt-6 px-1">Original Registering Party</h3>
          <registering-party-summary
            class="pt-4"
            :setEnableNoDataAction="false"
          />
          <h3 class="pt-6 px-1">Secured Parties</h3>
          <secured-party-summary class="pt-4" :setEnableNoDataAction="false" />
          <h3 class="pt-6 px-1">Debtors</h3>
          <debtor-summary class="pt-4" :setEnableNoDataAction="false" />
          <collateral class="mt-15" :isSummary="true" />
          <court-order
            :setShowErrors="showInvalid"
            :setRequireCourtOrder="true"
            @setCourtOrderValid="registrationValid = $event"
            v-if="registrationType === registrationTypeRL"
            class="mt-15" />
        </v-col>
        <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
                :setRightOffset="true"
                :setShowButtons="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setRegistrationLength="registrationLength"
                :setRegistrationType="registrationTypeUI"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Confirm and Complete'"
                @cancel="goToDashboard()"
                @submit="confirmRenewal()"
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
import { CautionBox, StickyContainer, CourtOrder } from '@/components/common'
import { RegistrationLengthTrust, RegistrationRepairersLien } from '@/components/registration'
import { Collateral } from '@/components/collateral'
import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '@/components/parties/summaries'
// local helpers/enums/interfaces/resources
import {
  APIRegistrationTypes, // eslint-disable-line no-unused-vars
  RouteNames, // eslint-disable-line no-unused-vars
  RegistrationFlowType, // eslint-disable-line no-unused-vars
  UIRegistrationTypes // eslint-disable-line no-unused-vars
} from '@/enums'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  AddPartiesIF, // eslint-disable-line no-unused-vars
  CertifyIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  AddCollateralIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  DebtorNameIF, // eslint-disable-line no-unused-vars
  CourtOrderIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
import { AllRegistrationTypes } from '@/resources'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { convertDate, getFeatureFlag, getFinancingStatement } from '@/utils'
import { StatusCodes } from 'http-status-codes'

@Component({
  components: {
    CautionBox,
    RegistrationLengthTrust,
    RegistrationRepairersLien,
    Collateral,
    DebtorSummary,
    RegisteringPartySummary,
    SecuredPartySummary,
    CourtOrder,
    StickyContainer
  }
})
export default class ReviewRegistration extends Vue {
  @Getter getConfirmDebtorName: DebtorNameIF
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getLengthTrust: LengthTrustIF
  @Getter getRegistrationFlowType: RegistrationFlowType
  @Getter getRegistrationNumber: String

  @Action setAddCollateral: ActionBindingIF
  @Action setStaffPayment: ActionBindingIF
  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF
  @Action setFeeSummary: ActionBindingIF
  @Action setLengthTrust: ActionBindingIF
  @Action setRegistrationCreationDate: ActionBindingIF
  @Action setRegistrationExpiryDate: ActionBindingIF
  @Action setRegistrationNumber: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF
  @Action setRegistrationFlowType: ActionBindingIF
  @Action setCourtOrderInformation: ActionBindingIF
  @Action setCertifyInformation: ActionBindingIF
  @Action setFolioOrReferenceNumber: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private dataLoaded = false // eslint-disable-line lines-between-class-members
  private financingStatementDate: Date = null
  private feeType = FeeSummaryTypes.RENEW
  private showInvalid = false
  private registrationValid = false

  private get asOfDateTime (): string {
    // return formatted date
    if (this.financingStatementDate) {
      return `${convertDate(this.financingStatementDate, true, true)}`
    }
    return `${convertDate(new Date(), true, true)}`
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  // the number of the registration being renewed
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

  private get registrationTypeRL (): string {
    return APIRegistrationTypes.REPAIRERS_LIEN
  }

  private async loadRegistration (): Promise<void> {
    if (
      !this.getRegistrationNumber ||
      this.getRegistrationFlowType !== RegistrationFlowType.RENEWAL
    ) {
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
      const financingStatement = await getFinancingStatement(true, this.registrationNumber)
      if (financingStatement.error) {
        this.emitError(financingStatement.error)
      } else {
        // load data into the store
        const registrationType = AllRegistrationTypes.find((reg, index) => {
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
          valid: false,
          showInvalid: false,
          trustIndenture: financingStatement.trustIndenture || false,
          lifeInfinite: false,
          lifeYears: null,
          surrenderDate: financingStatement.surrenderDate || null,
          lienAmount: financingStatement.lienAmount || null
        } as LengthTrustIF
        if (
          registrationType.registrationTypeAPI ===
          APIRegistrationTypes.REPAIRERS_LIEN
        ) {
          lengthTrust.lifeYears = 1
          lengthTrust.valid = true
        }
        const parties = {
          valid: true,
          registeringParty: financingStatement.registeringParty,
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
        this.setStaffPayment({
          option: -1,
          routingSlipNumber: '',
          bcolAccountNumber: '',
          datNumber: '',
          folioNumber: '',
          isPriority: false
        })
        this.setCourtOrderInformation(courtOrder)
        this.setRegistrationCreationDate(financingStatement.createDateTime)
        this.setRegistrationExpiryDate(financingStatement.expiryDate)
        this.setRegistrationNumber(financingStatement.baseRegistrationNumber)
        this.setRegistrationType(registrationType)
        this.setAddCollateral(collateral)
        this.setLengthTrust(lengthTrust)
        this.setAddSecuredPartiesAndDebtors(parties)
        this.setRegistrationFlowType(RegistrationFlowType.RENEWAL)
        this.setFolioOrReferenceNumber('')
        this.setCertifyInformation(certifyInfo)
      }
    }
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  private confirmRenewal (): void {
    if (this.registrationValid) {
      this.$router.push({
        name: RouteNames.CONFIRM_RENEWAL,
        query: { 'reg-num': this.registrationNumber }
      })
      this.emitHaveData(false)
    } else {
      this.showInvalid = true
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
      const errorMsg = error as string
      console.error(errorMsg)
      this.emitError({
        statusCode: 500,
        message: errorMsg
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
