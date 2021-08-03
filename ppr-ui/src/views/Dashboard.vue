<template>
  <v-container fluid class="pa-0 ma-0" style="max-width: none;">

    <v-row no-gutters>
      <v-container fluid class="py-10">
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
                          @debtor-name="setDebtorName"
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
        <v-row class="pt-3" no-gutters>
              <registration-bar class="soft-corners-bottom" :registrationTitle="''"/>
        </v-row>
        <v-row no-gutters class='pt-3'>
          <v-col>
            <v-row no-gutters
                   id="registration-header"
                   :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
              <v-col cols="auto">
                <b>My Registrations</b>
              </v-col>
            </v-row>
            <v-row no-gutters class="white" style="min-height:300px">
              <v-col cols="12"><registration-table /></v-col>
            </v-row>
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
import { StatusCodes } from 'http-status-codes'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { RouteNames } from '@/enums'
import { ActionBindingIF, BreadcrumbIF, ErrorIF, RegistrationTypeIF, // eslint-disable-line
         SearchResponseIF } from '@/interfaces' // eslint-disable-line
import { tombstoneBreadcrumbDashboard } from '@/resources'
import { getFeatureFlag, searchHistory } from '@/utils'
// local components
import { Tombstone } from '@/components/common'
import { SearchBar } from '@/components/search'
import { SearchHistory } from '@/components/tables'
import { RegistrationBar, RegistrationTable } from '@/components/registration'

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

  @Action setDebtorName: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF
  @Action setSearchHistory: ActionBindingIF
  @Action setSearchResults: ActionBindingIF
  @Action setSearchedType: ActionBindingIF
  @Action setSearchedValue: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

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

  private get breadcrumbs (): Array<BreadcrumbIF> {
    return tombstoneBreadcrumbDashboard
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
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
    this.emitHaveData()
  }

  @Watch('getRegistrationType')
  private startRegistration (val: RegistrationTypeIF): void {
    // navigate to registration page if not null/reset
    if (val) {
      // alert(val.registrationTypeAPI)
      this.$router.push({
        name: RouteNames.LENGTH_TRUST
      })
    }
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
