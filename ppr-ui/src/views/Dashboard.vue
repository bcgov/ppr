<template>
  <v-container id="dashboard" class="view-container px-15 py-10 ma-0" fluid>
    <!-- Page Overlay -->
    <v-overlay :value="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>

    <base-snackbar :setMessage="snackbarMsg" :toggleSnackbar="toggleSnackbar" />
    <div v-if="appReady" class="container pa-0">
      <v-row no-gutters>
        <v-col>
          <v-row no-gutters
                  id="search-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="auto">
              <b v-if="hasPPR && hasMHR">
                Manufactured Home and Personal Property Registries Search</b>
              <b v-else-if="hasPPR">Personal Property Registry Search</b>
              <b v-else-if="hasMHR">Manufactured Home Search</b>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <search-bar
              class="soft-corners-bottom"
              :isNonBillable="isNonBillable"
              :serviceFee="getUserServiceFee"
              @debtor-name="setSearchDebtorName"
              @searched-type="setSearchedType"
              @searched-value="setSearchedValue"
              @search-data="saveResults($event)"
              @search-error="emitError($event)"
            />
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class='pt-12'>
        <v-col>
          <v-row no-gutters
                  id="search-history-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="12" sm="3">
              <b>Searches</b> ({{ searchHistoryLength }})
            </v-col>
            <v-col cols="12" sm="9">
              <span :class="[$style['header-help-text'], 'float-right', 'pr-6']">
                The Searches table will display up to 1000 searches conducted within the last 14 days.
              </span>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col v-if="!appLoadingData" cols="12">
              <search-history class="soft-corners-bottom" @retry="retrieveSearchHistory" @error="emitError"/>
            </v-col>
            <v-col v-else class="pa-10" cols="12">
              <v-progress-linear color="primary" indeterminate rounded height="6" />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class="mt-4 pt-7">
        <v-col>
          <DashboardTabs
            v-if="enableDashboardTabs"
            :appLoadingData="appLoadingData"
            :appReady="appReady"
            @snackBarMsg="snackBarEvent($event)"
          />

          <RegistrationsWrapper
            v-else-if="hasPPR"
            isPpr
            :appLoadingData="appLoadingData"
            :appReady="appReady"
            @snackBarMsg="snackBarEvent($event)"
          />
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { ProductCode, RouteNames } from '@/enums'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  ManufacturedHomeSearchResponseIF, RegTableNewItemI, // eslint-disable-line no-unused-vars
  SearchResponseIF // eslint-disable-line no-unused-vars
} from '@/interfaces'

import {
  getFeatureFlag,
  searchHistory,
  navigate
} from '@/utils'
import { BaseSnackbar, RegistrationsWrapper } from '@/components/common'
import { SearchHistory } from '@/components/tables'
import { SearchBar } from '@/components/search'
import { useSearch } from '@/composables/useSearch'
import { DashboardTabs } from '@/components/dashboard'

@Component({
  components: {
    BaseSnackbar,
    DashboardTabs,
    SearchBar,
    SearchHistory,
    RegistrationsWrapper
  }
})
export default class Dashboard extends Vue {
  @Getter getSearchHistory: Array<SearchResponseIF>
  @Getter getSearchHistoryLength: number
  @Getter getUserServiceFee!: number
  @Getter isRoleStaff!: boolean
  @Getter isRoleStaffBcol!: boolean
  @Getter isRoleStaffReg!: boolean
  @Getter hasMhrRole!: boolean
  @Getter hasPprRole!: boolean
  @Getter isNonBillable!: boolean
  @Getter isRoleQualifiedSupplier!: boolean
  @Getter getUserProductSubscriptionsCodes: Array<ProductCode>
  @Getter getRegTableNewItem: RegTableNewItemI
  @Getter hasMhrEnabled!: boolean

  @Action resetNewRegistration: ActionBindingIF
  @Action setSearchDebtorName: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF
  @Action setSearchHistory: ActionBindingIF
  @Action setSearchResults: ActionBindingIF
  @Action setManufacturedHomeSearchResults: ActionBindingIF
  @Action setSearchedType: ActionBindingIF
  @Action setSearchedValue: ActionBindingIF
  @Action setRegTableNewItem: ActionBindingIF

  @Prop({ default: false })
  private appLoadingData: boolean

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private loading = false
  // my reg table action stuff
  private isMHRSearchType = useSearch().isMHRSearchType

  private snackbarMsg = ''
  private toggleSnackbar = false

  mounted () {
    // clear search data in the store
    this.setRegistrationType(null)
    this.setSearchedType(null)
    this.setSearchedValue('')
    this.setSearchResults(null)
    this.onAppReady(this.appReady)
  }

  private get enableDashboardTabs (): boolean {
    return getFeatureFlag('mhr-registration-enabled') &&
      this.hasPprRole && this.hasMhrRole && (this.isRoleStaff || this.isRoleQualifiedSupplier)
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get searchHistoryLength (): number {
    return this.getSearchHistory?.length || 0
  }

  private get hasPPR (): boolean {
    // For Staff we check roles, for Client we check Products
    if (this.isRoleStaff || this.isRoleStaffBcol || this.isRoleStaffReg) {
      return this.hasPprRole
    } else {
      return this.getUserProductSubscriptionsCodes.includes(ProductCode.PPR)
    }
  }

  private get hasMHR (): boolean {
    // For Staff we check roles, for Client we check Products
    if (this.isRoleStaff || this.isRoleStaffBcol || this.isRoleStaffReg) {
      return this.hasMhrRole && getFeatureFlag('mhr-ui-enabled')
    } else {
      if (this.getRegTableNewItem.addedReg) {
        this.snackBarEvent('Registration was successfully added to your table.')
        setTimeout(() => {
          const emptyItem: RegTableNewItemI = {
            addedReg: '', addedRegParent: '', addedRegSummary: null, prevDraft: ''
          }
          this.setRegTableNewItem(emptyItem)
        }, 4000)
      }
      return this.hasMhrEnabled
    }
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    navigate(this.registryUrl)
  }

  private async retrieveSearchHistory (): Promise<void> {
    // get/set search history
    const resp = await searchHistory()
    if (!resp || resp?.error) {
      this.setSearchHistory(null)
    } else {
      this.setSearchHistory(resp?.searches)
    }
  }

  private saveResults (results: SearchResponseIF|ManufacturedHomeSearchResponseIF) {
    if (results) {
      if (this.isMHRSearchType(results.searchQuery.type)) {
        this.setManufacturedHomeSearchResults(results)
        this.$router.replace({
          name: RouteNames.MHRSEARCH
        })
      } else {
        this.setSearchResults(results)
        this.$router.replace({
          name: RouteNames.SEARCH
        })
      }
    }
  }

  private snackBarEvent (msg: string): void {
    this.snackbarMsg = msg
    this.toggleSnackbar = !this.toggleSnackbar
  }

  /** Called when App is ready and this component can load its data. */
  @Watch('appReady')
  private async onAppReady (val: boolean): Promise<void> {
    this.loading = true
    // do not proceed if app is not ready
    if (!val) return

    // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
    if (!this.isAuthenticated || (!this.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
      window.alert('Personal Property Registry is under construction. Please check again later.')
      this.redirectRegistryHome()
      return
    }
    this.emitHaveData(false)
    this.resetNewRegistration(null) // Clear store data from any previous registration.
    await this.retrieveSearchHistory()

    // tell App that we're finished loading
    this.loading = false
    this.emitHaveData(true)
  }

  @Watch('getSearchHistoryLength')
  private handleSearchHistoryUpdate (newVal: number, oldVal: number): void {
    // show snackbar if oldVal was not null
    if (oldVal !== null) {
      this.snackbarMsg = 'Your search was successfully added to your table.'
      this.toggleSnackbar = !this.toggleSnackbar
    }
  }

  /** Emits error to app.vue for handling */
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
  background-color: $BCgovBlue0;
  color: $gray9;
  font-size: 1rem;
}

.header-help-text {
  color: $gray7;
  font-size: .875rem;
}
</style>
