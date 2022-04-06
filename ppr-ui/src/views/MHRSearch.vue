<template>
  <v-container fluid class="view-container pa-15">
    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <v-container class="container">
      <b :class="$style['search-title']">Search Results</b>
      <p v-if="!getManufacturedHomeSearchResults" :class="[$style['search-info'], 'ma-0']" style="padding-top: 26px;">
        Your search results will display below.
      </p>
      <div v-else no-gutters style="padding-top: 26px;">
        <v-row no-gutters style="padding-top: 22px;">
          <v-col :class="$style['search-info']">
            <span v-if="totalResultsLength !== 0" id="results-info">
              Select the manufactured home to download the full details of the home. Selecting the home will debit
              your search fee from your BC Online account. The downloaded report will contain the full record of
              the registration for the home and will be automatically saved to your dashboard.
            </span>
            <span v-else id="no-results-info">
              No Registrations were found. A printable PDF search result report and a general record of your search
              will be saved to your Personal Property Registry dashboard.
            </span>
          </v-col>
          <!-- to cut off in line with table submit btn -->
          <v-col cols="auto" style="width: 320px;" />
        </v-row>
      </div>
      <v-row v-if="getManufacturedHomeSearchResults" no-gutters style="padding-top: 38px;">
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
// local helpers/enums/interfaces/resources
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
export default class Search extends Vue {
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

  private get totalResultsLength (): number {
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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
#done-btn {
  font-size: 0.825rem !important;
}
.search-title {
  color: $gray9;
  font-size: 2rem;
  line-height: 2rem;
}
.search-sub-title {
  color: $gray8;
  font-size: 1.1rem;
  line-height: 1.5rem;
}
.search-info {
  color: $gray7;
  font-size: 1rem;
  line-height: 1.5rem;
}
.search-note {
  color: $gray7;
  font-size: 0.875rem;
  font-style: italic;
  line-height: 1rem;
}
.search-table-title {
  color: $gray9;
  font-size: 1rem;
  line-height: 1.5rem;
}
</style>
