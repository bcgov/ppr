<template>
  <v-container fluid class="pa-0" style="max-width: none;">
    <v-row no-gutters>
      <v-container fluid class="pt-4">
        <v-row>
          <v-col cols="9">
            <v-row no-gutters
                   id="registration-header"
                   class="length-trust-header pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
<h1>{{ registrationTypeUI }}</h1>

              </v-col>
            </v-row>
            <stepper class="mt-4" :showStepErrors="showStepErrors"/>
            <v-row class='pt-6'>
              <v-col cols="auto" class="sub-header ps-4">
                Review and Confirm
              </v-col>
            </v-row>
            <v-row class="pa-2">
              <v-col>
                Review the information in your registration. If you need to change anything,
                return to the step to make the necessary change.
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-container fluid class="pa-1">
                <v-row no-gutters class='pt-1'>
                  <v-col>
                    <registration-length-trust :isSummary="true"/>
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
                    <collateral :isSummary="true"/>
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
          </v-col>
          <v-col cols="3">
            <registration-fee :registrationType="registrationTypeUI"/>
          </v-col>
        </v-row>
      </v-container>
    </v-row>
    <v-row no-gutters class='pt-15'>
      <v-col cols="12">
        <button-footer :currentStatementType="statementType" :currentStepName="stepName"
                       :router="this.$router"
                       @draft-save-error="saveDraftError" @registration-incomplete="registrationIncomplete" />
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
import { RouteNames, StatementTypes } from '@/enums'
import {
  ActionBindingIF, FeeSummaryIF, ErrorIF, AddPartiesIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, AddCollateralIF, LengthTrustIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
// local components
import { ButtonFooter, RegistrationFee, Stepper } from '@/components/common'
import { RegistrationLengthTrust } from '@/components/registration'
import { Collateral } from '@/components/collateral'
import { Parties } from '@/components/parties'
import {
  getAddCollateral, // eslint-disable-line no-unused-vars
  getLengthTrust, // eslint-disable-line no-unused-vars
  getAddSecuredPartiesAndDebtors // eslint-disable-line no-unused-vars
} from '@/store/getters'
import {
  setAddCollateral, // eslint-disable-line no-unused-vars
  setLengthTrust, // eslint-disable-line no-unused-vars
  setAddSecuredPartiesAndDebtors // eslint-disable-line no-unused-vars
} from '@/store/actions'

@Component({
  components: {
    ButtonFooter,
    RegistrationFee,
    RegistrationLengthTrust,
    Stepper,
    Collateral,
    Parties
  }
})
export default class ReviewConfirm extends Vue {
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getFeeSummary: FeeSummaryIF
  @Getter getAddCollateral: AddCollateralIF
  @Getter getLengthTrust: LengthTrustIF
  @Getter getAddSecuredPartiesAndDebtors: AddPartiesIF

  @Action resetNewRegistration: ActionBindingIF
  @Action setAddCollateral: ActionBindingIF
  @Action setLengthTrust: ActionBindingIF
  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF

  @Prop({ default: '#app' })
  private attachDialog: string

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private showStepErrors: boolean = false

  private get feeSummary (): FeeSummaryIF {
    return this.getFeeSummary
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get registrationTypeUI (): string {
    return this.getRegistrationType?.registrationTypeUI || ''
  }

  private get registrationType (): string {
    return this.getRegistrationType?.registrationTypeAPI || ''
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  private get statementType (): string {
    return StatementTypes.FINANCING_STATEMENT
  }

  private get stepName (): string {
    return RouteNames.REVIEW_CONFIRM
  }

  mounted () {
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
  }

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

  @Watch('saveDraftError')
  private saveDraftError (val: ErrorIF): void {
    alert('Error saving draft. Replace when design complete.')
  }

  @Watch('registrationIncomplete')
  private registrationIncomplete (): void {
    this.showStepErrors = true
    alert('Error saving draft. Replace when design complete.')
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
