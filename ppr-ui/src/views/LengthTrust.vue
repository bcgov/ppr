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
          <v-col cols="3" class="pt-10">
            <registration-fee
              :registrationType="registrationTypeUI"
              :updatedFeeSummary="updatedFeeSummary"
              :hint="feeHint"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-row>
    <v-row no-gutters>
      <v-container fluid class="pl-6 pt-30 pb-60">
        <v-row no-gutters>
          <v-col cols="6" class="align=left pa-0">
            <span class="pr-3">
              <v-btn
                id="reg-cancel-btn"
                outlined
                color="accent"
                @click="submitCancel"
              >
                <b>Cancel</b>
              </v-btn>
            </span>
            <span class="pr-3">
              <v-btn
                id="reg-save-resume-btn"
                outlined
                color="accent"
                @click="submitSaveResume"
              >
                <b>Save and Resume Later</b>
              </v-btn>
            </span>
            <v-btn
              id="reg-save-btn"
              outlined
              color="accent"
              @click="submitSave"
            >
              <b>Save</b>
            </v-btn>
          </v-col>
          <!--
          <v-col cols="2">
          </v-col>
          <v-col cols="1">
          </v-col>
          <v-col cols="5" class="align=right">
            <v-btn id='reg-back-btn' outlined color="accent" @click="submitBack">
              <b>< Back</b>
            </v-btn>
          </v-col>
-->
          <v-col cols="6" class="align=right">
            <v-btn id="reg-next-btn" color="primary" @click="submitNext">
              <b>Add Secured Parties and Debtors ></b>
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
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
import { getFinancingFee } from '@/utils'
import { RouteNames } from '@/enums'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  BreadcrumbIF, // eslint-disable-line no-unused-vars
  FeeIF, // eslint-disable-line no-unused-vars
  FeeSummaryIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { tombstoneBreadcrumbRegistration } from '@/resources'
// local components
import { RegistrationFee, Stepper, Tombstone } from '@/components/common'
import { RegistrationLengthTrust } from '@/components/registration'

@Component({
  components: {
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
  @Action resetNewRegistration: ActionBindingIF

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

  private get trustIndenture (): boolean {
    return this.getLengthTrust?.trustIndenture || false
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  private submitNext (): void {
    // validate and if no errors navigate to add parties
    this.$router.push({
      name: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS
    })
  }

  private submitCancel (): void {
    // clear all state set data
    this.resetNewRegistration(null)
    // navigate to dashboard
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
  }

  private submitBack (): void {
    this.submitCancel()
  }

  private submitSave (): void {
    // Save and return to dashboard
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
  }

  private submitSaveResume (): void {
    // Save draft
    // alert('Soon')
  }

  @Watch('updatedFeeSummary')
  private updateFeeSummary (val: FeeSummaryIF): void {
    if (val) {
      this.updatedFeeSummary = val
    }
  }

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }
}
</script>

<style lang="scss" scoped>
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
