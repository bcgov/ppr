<template>
  <v-container fluid class="pa-0" style="max-width: none;">
    <v-row no-gutters>
        <tombstone :backURL="dashboardURL" :header="'My Personal Property Registry'" :setItems="breadcrumbs"/>
    </v-row>
    <v-row no-gutters>
      <v-container fluid class="pt-4">
        <v-row no-gutters>
          <v-col cols="6">
            <v-row no-gutters
                   id="registration-header"
                   :class="[$style['length-trust-header'], 'pt-3', 'pb-3', 'soft-corners-top']">
              <v-col cols="auto">
                <b>{{ registrationTypeUI }}</b>
              </v-col>
            </v-row>
            <stepper class="mt-4" />
            <template>
              <component
                v-for="step in getSteps"
                v-show="isRouteName(step.to)"
                :is="step.component"
                :key="step.step"
              />
            </template>
          </v-col>
          <v-col cols="1">
          </v-col>
           <v-col align-self="end" cols="3">
            <registration-fee :registrationType="registrationTypeUI"/>
          </v-col>
        </v-row>
        <v-row no-gutters class='pt-6'>
          <v-col cols="auto">
            <b>Add Secured Parties and Debtors</b>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="auto">
            Add the people and businesses who have an interest in this registration.
          </v-col>
        </v-row>
      </v-container>
    </v-row>
    <v-row no-gutters>
      <v-container fluid class="pa-10">
        <v-row no-gutters class='pt-12'>
          <v-col cols="auto">Content</v-col>
        </v-row>
      </v-container>
    </v-row>
    <v-row no-gutters>
      <v-container fluid class="pl-6 pt-30 pb-60">
        <v-row no-gutters>
          <v-col cols="6"  class="align=left pa-0">
            <span class="pr-3">
              <v-btn id='reg-cancel-btn' outlined color="accent" @click="submitCancel">
                <b>Cancel</b>
              </v-btn>
            </span>
            <span class="pr-3">
              <v-btn id='reg-save-resume-btn' outlined color="accent" @click="submitSaveResume">
                <b>Save and Resume Later</b>
              </v-btn>
            </span>
            <v-btn id='reg-save-btn' outlined color="accent" @click="submitSave">
              <b>Save</b>
            </v-btn>
          </v-col>
          <v-col cols="6" class="align=right">
            <span class="pr-3">
              <v-btn id='reg-back-btn' outlined color="accent" @click="submitBack">
                <b>&lt; Back</b>
              </v-btn>
            </span>
            <v-btn id='reg-next-btn' color="primary" @click="submitNext">
              <b>Add Collateral ></b>
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { RouteNames } from '@/enums'
import {
  ActionBindingIF, BreadcrumbIF, FeeSummaryIF, ErrorIF, RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { tombstoneBreadcrumbRegistration } from '@/resources'
// local components
import { RegistrationFee, Stepper, Tombstone } from '@/components/common'

@Component({
  components: {
    RegistrationFee,
    Stepper,
    Tombstone
  }
})
export default class AddParties extends Vue {
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getFeeSummary: FeeSummaryIF

  @Action resetNewRegistration: ActionBindingIF

  @Prop({ default: '#app' })
  private attachDialog: string

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private get breadcrumbs (): Array<BreadcrumbIF> {
    const registrationBreadcrumb = tombstoneBreadcrumbRegistration
    registrationBreadcrumb[2].text = this.getRegistrationType?.registrationTypeUI || 'New Registration'
    return registrationBreadcrumb
  }

  private get dashboardURL (): string {
    return window.location.origin + '/dashboard'
  }

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

  private submitNext (): void {
    // validate and if no errors navigate to add parties
    this.$router.push({
      name: RouteNames.ADD_COLLATERAL
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
    // navigate to dashboard
    this.$router.push({
      name: RouteNames.LENGTH_TRUST
    })
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

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }
}
</script>

<style lang="scss" module>
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

.parties-header {
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
