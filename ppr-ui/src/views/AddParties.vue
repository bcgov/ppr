<template>
  <v-container fluid class="pa-0" style="max-width: none;">
    <v-row no-gutters>
        <tombstone :backURL="dashboardURL" :header="'My Personal Property Registry'" :setItems="breadcrumbs"/>
    </v-row>
    <v-row no-gutters>
      <v-container fluid class="pt-4">
        <v-row>
          <v-col cols="9" class="ps-8">
            <v-row no-gutters
                   id="registration-header"
                   class="length-trust-header pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <b>{{ registrationTypeUI }}</b>
              </v-col>
            </v-row>
            <stepper class="mt-4" />
            <v-row class='pt-6'>
              <v-col cols="auto" class="sub-header ps-4">
                Add Secured Parties and Debtors
              </v-col>
            </v-row>
            <v-row class="pa-2">
              <v-col cols="auto">
                Add the people and businesses who have an interest in this registration.
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-container fluid class="pa-10">
                <v-row no-gutters class='pt-12'>
                  <v-col cols="auto">Content</v-col>
                </v-row>
              </v-container>
            </v-row>
        </v-col>
        <v-col cols="3">
            <registration-fee
              :registrationType="registrationTypeUI"
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
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { RouteNames, StatementTypes } from '@/enums'
import {
  ActionBindingIF, BreadcrumbIF, FeeSummaryIF, ErrorIF, RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { tombstoneBreadcrumbRegistration } from '@/resources'
// local components
import { ButtonFooter, RegistrationFee, Stepper, Tombstone } from '@/components/common'

@Component({
  components: {
    ButtonFooter,
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

  private get statementType (): string {
    return StatementTypes.FINANCING_STATEMENT
  }

  private get stepName (): string {
    return RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS
  }

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

  @Watch('draftSaveError')
  private saveDraftError (val: ErrorIF): void {
    alert('Error saving draft. Replace when design complete.')
  }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
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
</style>
