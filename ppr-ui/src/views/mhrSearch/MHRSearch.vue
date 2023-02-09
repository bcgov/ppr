<template>
  <v-container fluid class="view-container pa-15">
    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <v-container class="container">
      <div class="selection-list-title">
        <v-icon size="32" class="pr-1">mdi-home</v-icon>
        Selection List
      </div>
      <p v-if="!getManufacturedHomeSearchResults" class="search-info ma-0">
        Your search results will display below.
      </p>
      <div v-else no-gutters>
        <v-row no-gutters class="mt-6">
          <v-col class="search-info pr-6">
            <span v-if="totalResultsLength !== 0" id="results-info">
              Select manufactured home registrations to download a search result report containing the full details of
              the registration(s). Lien information contained in the Personal Property Registry can be included for an
              additional fee per manufactured home registration. You will be able to review your selection prior to
              payment.
            </span>
            <span v-else id="no-results-info">
              No Registrations were found.
            </span>
          </v-col>
        </v-row>
      </div>
      <v-row v-if="getManufacturedHomeSearchResults" no-gutters class="mt-6">
        <searched-result-mhr class="soft-corners" @submit="submitCheck()" />
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local components
import {
  BaseDialog,
  ConfirmationDialog,
  LargeSearchResultDialog,
  LargeSearchDelayDialog
} from '@/components/dialogs'
import { SearchedResultMhr } from '@/components/tables'
import { SearchBar } from '@/components/search'
import { RouteNames } from '@/enums'
import {
  ActionBindingIF, ErrorIF, IndividualNameIF, ManufacturedHomeSearchResponseIF, // eslint-disable-line no-unused-vars
  SearchTypeIF, UserSettingsIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { getFeatureFlag, navigate } from '@/utils'

@Component({
  components: {
    BaseDialog,
    ConfirmationDialog,
    LargeSearchResultDialog,
    LargeSearchDelayDialog,
    SearchBar,
    SearchedResultMhr
  }
})
export default class MHRSearch extends Vue {
  @Getter getSearchDebtorName: IndividualNameIF
  @Getter getManufacturedHomeSearchResults: ManufacturedHomeSearchResponseIF
  @Getter getSearchedValue: string
  @Getter getSearchedType: SearchTypeIF
  @Getter getUserSettings: UserSettingsIF

  @Action setSearchDebtorName: ActionBindingIF
  @Action setManufacturedHomeSearchResults: ActionBindingIF
  @Action setSearchedType: ActionBindingIF
  @Action setSearchedValue: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: '#app' })
  private attachDialog: string

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private loading = false

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  get totalResultsLength (): number {
    const searchResult = this.getManufacturedHomeSearchResults
    if (searchResult) {
      return searchResult.totalResultsSize
    }
    return 0
  }

  private created (): void {
    window.onbeforeunload = (event) => {
      // unsaved selections if app is ready, search results exist, and on the search page
      const isSearchReportUnsaved = (
        this.$router.currentRoute.name === RouteNames.MHRSEARCH &&
        this.appReady &&
        !!this.getManufacturedHomeSearchResults
      )
      if (isSearchReportUnsaved) {
        event.preventDefault()
        // NB: custom text is no longer supported by newest versions of all browsers since 2021 for security reasons
        // the event.returnValue is now only treated as a flag (added text in case this ever changes)
        event.returnValue = 'You have not saved your search result report. Are you sure you want to leave?'
      }
    }
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    navigate(this.registryUrl)
  }

  private submitCheck (): void {

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

    // if navigated here without search results redirect to the dashboard
    if (!this.getManufacturedHomeSearchResults) {
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      this.emitHaveData(false)
      return
    }

    // page is ready
    this.emitHaveData(true)
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

<style lang="scss" scope>
@import '@/assets/styles/theme.scss';
.selection-list-title {
  display: flex;
  color: $gray9;
  font-size: 2rem;
  line-height: 2rem;
  font-weight: bold;

  .v-icon {
    color: $gray9;
  }
}
.search-info {
  color: $gray7;
  font-size: 1rem;
  line-height: 1.5rem;
  padding-top: 26px;
}
.home {
  vertical-align: baseline !important;
  color: #212529 !important;
}

</style>
