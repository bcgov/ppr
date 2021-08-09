<template>
  <v-container fluid class="pa-0" style="max-width: none">
    <v-row no-gutters>
      <v-container fluid class="pt-4">
        <v-row>
          <v-col cols="9">
            <v-row
              no-gutters
              id="registration-header"
              class="length-trust-header pt-3 pb-3 soft-corners-top"
            >
              <v-col cols="auto">
<h1>{{ registrationTypeUI }}</h1>

              </v-col>
            </v-row>
            <stepper class="mt-4" />
            <v-row no-gutters class="pt-10">
              <v-col cols="auto" class="sub-header" v-if="registrationType !== registrationTypes['REPAIRERS_LIEN']">
                Registration Length and Trust Indenture
              </v-col>
              <v-col cols="auto" class="sub-header" v-else>
                Terms of Repairers Lien
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pt-2 pb-6">
                {{registrationLengthMessage}}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <registration-length-trust
                  :defaultRegistrationType="registrationType"
                  @updated-fee-summary="updateFeeSummary"
                />
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="3">
            <registration-fee
              :registrationType="registrationTypeUI"
              :updatedFeeSummary="updatedFeeSummary"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-row>
    <v-row no-gutters class='pt-10'>
      <v-col cols="12">
        <button-footer :currentStatementType="statementType" :currentStepName="stepName"
                       :router="this.$router" @draft-save-error="saveDraftError"/>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import {
  ActionBindingIF, ErrorIF, FeeSummaryIF, LengthTrustIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
// local components
import { ButtonFooter, RegistrationFee, Stepper } from '@/components/common'
import { RegistrationLengthTrust } from '@/components/registration'
import { APIRegistrationTypes, RouteNames, StatementTypes } from '@/enums' // eslint-disable-line no-unused-vars

@Component({
  components: {
    ButtonFooter,
    RegistrationFee,
    RegistrationLengthTrust,
    Stepper
  }
})
export default class LengthTrust extends Vue {
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getLengthTrust: LengthTrustIF
  @Getter getFeeSummary: FeeSummaryIF

  @Action setLengthTrust: ActionBindingIF

  @Prop({ default: '#app' })
  private attachDialog: string

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private updatedFeeSummary: FeeSummaryIF = null

  private regTypes: APIRegistrationTypes[] = Object.keys(APIRegistrationTypes).map(k => APIRegistrationTypes[k])

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get feeSummary (): FeeSummaryIF {
    return this.getFeeSummary
  }

  private get registrationTypeUI (): string {
    return this.getRegistrationType?.registrationTypeUI || ''
  }

  private get registrationType (): string {
    return this.getRegistrationType?.registrationTypeAPI || ''
  }

  private get registrationTypes (): Array<string> {
    return this.regTypes
  }

  private get registrationLengthMessage (): string {
    switch (this.getRegistrationType) {
      case APIRegistrationTypes.REPAIRERS_LIEN:
        return 'Enter the amount of the Lien and the date the vehicle was surrendered.' +
                'Please note that this must be within the last 21 days. The length of the Lien is automatically set ' +
                'to 180 days.'
      case APIRegistrationTypes.MARRIAGE_MH:
      case APIRegistrationTypes.LAND_TAX_LIEN:
      case APIRegistrationTypes.MANUFACTURED_HOME_LIEN:
        return 'The registration length for this registration is automatically set to infinite. ' +
        'There is a $10.00 fee for this registration.'
      case APIRegistrationTypes.MISCELLANEOUS_OTHER:
        return 'The registration length for this registration is automatically set to infinite. ' +
        'There is no fee for this registration.'
      default:
        return 'Enter the length of time you want the ' + this.getRegistrationType?.registrationTypeUI +
                ' to be in effect. You can renew the registration in the future (for a fee).'
    }
  }

  private get statementType (): string {
    return StatementTypes.FINANCING_STATEMENT
  }

  private get stepName (): string {
    return RouteNames.LENGTH_TRUST
  }

  private get trustIndenture (): boolean {
    return this.getLengthTrust?.trustIndenture || false
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  @Watch('updatedFeeSummary')
  private updateFeeSummary (val: FeeSummaryIF): void {
    if (val) {
      this.updatedFeeSummary = val
    }
  }

  @Watch('draftSaveError')
  private saveDraftError (val: ErrorIF): void {
    alert('Error saving draft. Replace when design complete.')
  }
}
</script>

<style lang="scss" module>
@import "@/assets/styles/theme.scss";
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

.reg-default-btn {
  background-color: $gray3 !important;
}

.reg-default-btn::before {
  background-color: transparent !important;
}
</style>
