<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>
    <base-dialog
      id="reviewDialog"
      :setDisplay="errorDialog"
      :setOptions="errorOptions"
      @proceed="handleError($event)"
    />
    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters
                   id="registration-header"
                   class="length-trust-header pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>{{ registrationTypeUI }}</h1>
              </v-col>
            </v-row>
            <stepper class="mt-4" :showStepErrorsFlag="showStepErrors"/>
            <v-row class='pt-10' no-gutters>
              <v-col cols="auto" class="sub-header">
                Review and Confirm
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pt-2 pb-6 sub-header-info">
                Review the information in your registration. If you need to change anything,
                return to the step to make the necessary change.
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-container fluid class="pa-1">
                <v-row no-gutters class='pt-1'>
                  <v-col>
                    <registration-length-trust-summary />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row no-gutters>
              <v-container fluid class="ps-1 pt-8">
                <v-row no-gutters class='pt-1'>
                  <v-col>
                    <parties :isSummary="true"/>
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row no-gutters>
              <v-container fluid class="ps-1 pt-8">
                <v-row no-gutters class='pt-1'>
                  <v-col>
                    <collateral :isSummary="true" />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row no-gutters>
              <v-container fluid class="ps-1 pt-8">
                <v-row no-gutters class='pt-1'>
                  <v-col>
                    <folio-number-summary />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row no-gutters>
              <v-container fluid class="ps-1 pt-8">
                <v-row no-gutters class='pt-1'>
                  <v-col>
                    <certify-information
                      @certifyValid="validCertify = $event"
                      :setShowErrors="showStepErrors"
                      class="pt-10"
                    />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
          </v-col>
          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <sticky-container
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  :setRegistrationLength="registrationLength"
                  :setRegistrationType="registrationTypeUI"
                />
              </affix>
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
    <v-row no-gutters class='pt-15'>
      <v-col cols="12">
        <button-footer
          :currentStatementType="statementType"
          :currentStepName="stepName"
          :router="this.$router"
          :certifyValid="validCertify"
          :forceSave="saveDraftExit"
          @draft-save-error="saveDraftError"
          @registration-incomplete="registrationIncomplete"
          @error="handleSubmitError($event)"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { APIRegistrationTypes, RegistrationFlowType, RouteNames, StatementTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ActionBindingIF, ErrorIF, AddPartiesIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, AddCollateralIF, LengthTrustIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
import { getFeatureFlag } from '@/utils'
// local components
import { Stepper, StickyContainer, CertifyInformation } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { Collateral } from '@/components/collateral'
import { Parties } from '@/components/parties'
import FolioNumberSummary from '@/components/common/FolioNumberSummary.vue'
import { BaseDialog } from '@/components/dialogs'
import {
  registrationSaveDraftErrorDialog,
  registrationCompleteErrorDialog
} from '@/resources/dialogOptions'
import { StatusCodes } from 'http-status-codes'
@Component({
  components: {
    ButtonFooter,
    Collateral,
    FolioNumberSummary,
    Parties,
    RegistrationLengthTrustSummary,
    Stepper,
    CertifyInformation,
    BaseDialog,
    StickyContainer
  }
})
export default class ReviewConfirm extends Vue {
  @Getter getAddCollateral: AddCollateralIF
  @Getter getAddSecuredPartiesAndDebtors: AddPartiesIF
  @Getter getLengthTrust: LengthTrustIF
  @Getter getRegistrationFlowType: RegistrationFlowType
  @Getter getRegistrationOther: string
  @Getter getRegistrationType: RegistrationTypeIF
  @Action setAddCollateral: ActionBindingIF
  @Action setLengthTrust: ActionBindingIF
  @Action setShowStepErrors: ActionBindingIF
  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF
  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: false })
  private saveDraftExit: boolean

  private dataLoaded = false
  private feeType = FeeSummaryTypes.NEW
  private showStepErrors: boolean = false
  private statementType = StatementTypes.FINANCING_STATEMENT
  private stepName = RouteNames.REVIEW_CONFIRM
  private validCertify = false
  private errorDialog = false
  private errorOptions = registrationSaveDraftErrorDialog
  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get registrationLength (): RegistrationLengthI {
    return {
      lifeInfinite: this.getLengthTrust?.lifeInfinite || false,
      lifeYears: this.getLengthTrust?.lifeYears || 0
    }
  }

  private get registrationTypeUI (): string {
    if (this.getRegistrationType?.registrationTypeAPI === APIRegistrationTypes.OTHER) {
      return this.getRegistrationOther || ''
    }
    return this.getRegistrationType?.registrationTypeUI || ''
  }

  private get registrationType (): string {
    return this.getRegistrationType?.registrationTypeAPI || ''
  }

  private handleError (stay: boolean): void {
    this.errorDialog = false
    if (!stay) {
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
  }

  private handleSubmitError (error: ErrorIF): void {
    if (error.statusCode === StatusCodes.PAYMENT_REQUIRED) {
      this.emitError(error)
    } else {
      this.errorOptions = { ...registrationCompleteErrorDialog }
      this.errorDialog = true
    }
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void { }

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
    // redirect if store doesn't contain all needed data (happens on page reload, etc.)
    if (!this.getRegistrationType || this.getRegistrationFlowType !== RegistrationFlowType.NEW) {
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      return
    }
    const collateral = this.getAddCollateral
    if (!collateral.valid) {
      collateral.showInvalid = true
      this.setAddCollateral(collateral)
    }
    const lengthTrust = this.getLengthTrust
    if (!lengthTrust.valid) {
      lengthTrust.showInvalid = true
      this.setLengthTrust(lengthTrust)
    }
    const parties = this.getAddSecuredPartiesAndDebtors
    if (!parties.valid) {
      parties.showInvalid = true
      this.setAddSecuredPartiesAndDebtors(parties)
    }
    // page is ready to view
    this.emitHaveData(true)
    this.dataLoaded = true
  }

  @Watch('saveDraftError')
  private saveDraftError (val: ErrorIF): void {
    this.errorOptions = { ...registrationSaveDraftErrorDialog }
    this.errorDialog = true
  }

  @Watch('registrationIncomplete')
  private registrationIncomplete (): void {
    this.showStepErrors = true
    this.setShowStepErrors(true)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.step-container {
  margin-top: 1rem;
  padding: 1.25rem;
}
.meta-container {
  display: flex;
  flex-flow: column nowrap;
  position: relative;
  > label:first-child {
    font-weight: 700;
  }
}
@media (min-width: 768px) {
  .meta-container {
    flex-flow: row nowrap;
    > label:first-child {
      flex: 0 0 auto;
      padding-right: 2rem;
      width: 12rem;
    }
  }
}
.review-header {
  color: $gray9;
  font-size: 1.5rem;
  font-weight: bold;
}
.reg-default-btn {
  background-color: $gray3 !important;
}
.reg-default-btn::before {
  background-color: transparent !important;
}
</style>
