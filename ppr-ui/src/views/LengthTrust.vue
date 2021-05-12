<template>
  <v-container fluid class="pa-0" style="max-width: none">
    <v-row no-gutters>
      <tombstone
        :backURL="dashboardURL"
        :header="'My Personal Property Registry'"
        :setItems="breadcrumbs"
      />
    </v-row>
    <v-row no-gutters>
      <v-container fluid class="pt-4">
        <v-row>
          <v-col cols="9" class="ps-8">
            <v-row
              no-gutters
              id="registration-header"
              class="length-trust-header pt-3 pb-3 soft-corners-top"
            >
              <v-col cols="auto">
                <b>{{ registrationTypeUI }}</b>
              </v-col>
            </v-row>
            <stepper class="mt-4" />
            <v-row no-gutters class="pt-6">
              <v-col cols="auto" class="sub-header">
                Registration Length and Trust Indenture
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pt-2 pb-6">
                Enter the length of time you want the
                {{ registrationTypeUI }} to be in effect. You can renew the
                registration in the future (for a fee).
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
              :hint="feeHint"
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
import { getFinancingFee } from '@/utils'
import {
  ActionBindingIF, BreadcrumbIF, ErrorIF, FeeSummaryIF, LengthTrustIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { tombstoneBreadcrumbRegistration } from '@/resources'
// local components
import { ButtonFooter, RegistrationFee, Stepper, Tombstone } from '@/components/common'
import { RegistrationLengthTrust } from '@/components/registration'
import { RouteNames, StatementTypes } from '@/enums'

@Component({
  components: {
    ButtonFooter,
    RegistrationFee,
    RegistrationLengthTrust,
    Stepper,
    Tombstone
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

  private get breadcrumbs (): Array<BreadcrumbIF> {
    const registrationBreadcrumb = tombstoneBreadcrumbRegistration
    registrationBreadcrumb[2].text =
      this.getRegistrationType?.registrationTypeUI || 'New Registration'
    return registrationBreadcrumb
  }

  private get dashboardURL (): string {
    return window.location.origin + '/dashboard'
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get feeHint (): string {
    return getFinancingFee(false).hint
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
