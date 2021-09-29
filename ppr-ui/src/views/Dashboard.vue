<template>
  <v-container fluid class="view-container px-15 py-10 ma-0">
    <div class="container pa-0">
      <v-row no-gutters>
        <v-col>
          <v-row no-gutters
                  id="search-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="auto">
              <b>Personal Property Search</b>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <search-bar class="soft-corners-bottom"
                        :searchTitle="''"
                        @debtor-name="setSearchDebtorName"
                        @searched-type="setSearchedType"
                        @searched-value="setSearchedValue"
                        @search-data="setSearchResults"
                        @search-error="emitError"/>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class='pt-12'>
        <v-col>
          <v-row no-gutters
                  id="search-history-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="auto">
              <b>My Searches</b> ({{ searchHistoryLength }})
            </v-col>
          </v-row>
          <v-row no-gutters>
            <search-history class="soft-corners-bottom" @error="emitError"/>
          </v-row>
        </v-col>
      </v-row>
      <v-row class="pt-15" no-gutters>
        <registration-bar class="soft-corners-bottom" @selected-registration-type="startRegistration($event)"/>
      </v-row>
      <v-row no-gutters class="pt-7" style="margin-top: 2px; margin-bottom: 80px;">
        <v-col>
          <v-row no-gutters
                  id="registration-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="auto">
              <b>My Registrations</b> ({{ registrationsLength }})
            </v-col>
          </v-row>
          <v-row no-gutters class="white" style="min-height:300px">
            <v-col cols="12">
              <registration-table
                @registrationTotal="showRegistrationTotal($event)"
                @discharge="startDischarge($event)"
                @renew="startRenewal($event)"
                @amend="startAmendment($event)"
                @editFinancingDraft="startFinancingDraft($event)"
                @editAmendmentDraft="startAmendmentDraft"
              />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
import { StatusCodes } from 'http-status-codes'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { RouteNames } from '@/enums'
import { ActionBindingIF, BreadcrumbIF, ErrorIF, RegistrationTypeIF, // eslint-disable-line
         SearchResponseIF, StateModelIF } from '@/interfaces' // eslint-disable-line
import { tombstoneBreadcrumbDashboard } from '@/resources'
import { getFeatureFlag, searchHistory, setupFinancingStatementDraft } from '@/utils'
// local components
import { Tombstone } from '@/components/tombstone'
import { SearchBar } from '@/components/search'
import { SearchHistory, RegistrationTable } from '@/components/tables'
import { RegistrationBar } from '@/components/registration'

@Component({
  components: {
    RegistrationBar,
    SearchHistory,
    SearchBar,
    Tombstone,
    RegistrationTable
  }
})
export default class Dashboard extends Vue {
  @Getter getSearchHistory: Array<SearchResponseIF>
  @Getter getSearchResults: SearchResponseIF
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getStateModel: StateModelIF

  @Action resetNewRegistration: ActionBindingIF
  @Action setSearchDebtorName: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF
  @Action setSearchHistory: ActionBindingIF
  @Action setSearchResults: ActionBindingIF
  @Action setSearchedType: ActionBindingIF
  @Action setSearchedValue: ActionBindingIF
  @Action setStateModel: ActionBindingIF
  @Action setLengthTrust: ActionBindingIF
  @Action setAddCollateral: ActionBindingIF
  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private regLength: number = 0

  mounted () {
    // clear search data in the store
    this.setRegistrationType(null)
    this.setSearchedType(null)
    this.setSearchedValue('')
    this.setSearchResults(null)
    this.onAppReady(this.appReady)
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get searchHistoryLength (): number {
    return this.getSearchHistory?.length || 0
  }

  private get registrationsLength (): number {
    return this.regLength
  }

  private get breadcrumbs (): Array<BreadcrumbIF> {
    return tombstoneBreadcrumbDashboard
  }

  private startDischarge (regNum: string): void {
    this.$router.push({
      name: RouteNames.REVIEW_DISCHARGE,
      query: { 'reg-num': regNum }
    })
    this.emitHaveData(false)
  }

  private startRenewal (regNum: string): void {
    this.$router.push({
      name: RouteNames.RENEW_REGISTRATION,
      query: { 'reg-num': regNum }
    })
    this.emitHaveData(false)
  }

  private startAmendment (regNum: string): void {
    this.$router.push({
      name: RouteNames.AMEND_REGISTRATION,
      query: { 'reg-num': regNum }
    })
    this.emitHaveData(false)
  }

  private async startFinancingDraft (documentId: string): Promise<void> {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    // Get draft details and setup store for editing the draft financing statement.
    const stateModel:StateModelIF = await setupFinancingStatementDraft(this.getStateModel, documentId)
    if (stateModel.registration.draft === undefined || stateModel.registration.draft.error !== undefined) {
      alert('Attempt to get draft for editing failed.')
    } else {
      this.setLengthTrust(stateModel.registration.lengthTrust)
      this.setAddCollateral(stateModel.registration.collateral)
      this.setAddSecuredPartiesAndDebtors(stateModel.registration.parties)
      // Go to the first step.
      this.$router.push({ name: RouteNames.LENGTH_TRUST })
    }
  }

  private async startAmendmentDraft ({ regNum, docId }): Promise<void> {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    // Go to the Amendment first step which loads the base registration and draft data.
    this.$router.push({
      name: RouteNames.AMEND_REGISTRATION,
      query: { 'reg-num': regNum, 'document-id': docId }
    })
    this.emitHaveData(false)
  }

  private showRegistrationTotal (total: number): void {
    this.regLength = total
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  /** Set registration type in the store and route to the first registration step */
  private startRegistration (selectedRegistration: RegistrationTypeIF): void {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    this.setRegistrationType(selectedRegistration)
    this.$router.push({ name: RouteNames.LENGTH_TRUST })
  }

  /** Called when App is ready and this component can load its data. */
  @Watch('appReady')
  private async onAppReady (val: boolean): Promise<void> {
    // do not proceed if app is not ready
    if (!val) return

    // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
    if (!this.isAuthenticated || (!this.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
      window.alert('Personal Property Registry is under contruction. Please check again later.')
      this.redirectRegistryHome()
      return
    }

    // get/set search history
    const resp = await searchHistory()
    if (!resp || resp?.error) {
      this.emitError({ statusCode: StatusCodes.NOT_FOUND })
    } else {
      this.setSearchHistory(resp?.searches)
    }
    // tell App that we're finished loading
    this.emitHaveData(true)
  }

  @Watch('getSearchResults')
  private onSearch (val: SearchResponseIF): void {
    // navigate to search page if not null/reset
    if (val) {
      this.$router.push({
        name: RouteNames.SEARCH
      })
    }
  }

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void { }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.dashboard-title {
  font-size: 1rem;
  color: $gray9;
  background-color: $BCgovBlue0;
}
</style>
