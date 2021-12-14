<template>
  <v-container fluid class="view-container pa-15">
    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog :setDisplay="errorDialog" :setOptions="errorOptions" @proceed="handleReportError($event)" />
    <large-search-result-dialog
      :setDisplay="largeSearchResultDialog"
      :setOptions="largeSearchResultOptions"
      :setNumberRegistrations="selectedResultsLength"
      @proceed="handleLargeReport($event)"
    />
    <large-search-delay-dialog
      :setDisplay="largeSearchDelayDialog"
      :setOptions="largeSearchDelayOptions"
      :setNumberRegistrations="exactResultsLength"
      @proceed="handleDelayReport($event)"
    />
    <confirmation-dialog
      :setDisplay="confirmationDialog"
      :setOptions="confirmOptions"
      :setSettingOption="settingOption"
      @proceed="submit($event)"
    />
    <v-container class="container">
      <b :class="$style['search-title']">Search Results</b>
      <p v-if="!getSearchResults" :class="[$style['search-info'], 'ma-0']" style="padding-top: 26px;">
        Your search results will display below.
      </p>
      <div v-else no-gutters style="padding-top: 26px;">
        <p id="search-meta-info" class="ma-0">
          <span :class="$style['search-sub-title']"><b>for {{ searchType }} "{{ searchValue }}"</b></span>
          <span :class="$style['search-info']">{{ searchTime }}</span>
        </p>
        <p v-if="folioNumber" id="results-folio-header" class="ma-0" style="padding-top: 22px;">
          <b :class="$style['search-table-title']">Folio Number: </b>
          <span :class="$style['search-info']">{{ folioNumber }}</span>
        </p>
        <v-row no-gutters style="padding-top: 22px;">
          <v-col :class="$style['search-info']">
            <span v-if="totalResultsLength !== 0" id="results-info">
              Select the registrations you want to include in a printable search report. Exact matches
              are automatically selected. This report will contain the full record of each selected registration
              and will be saved to My Searches on your My Personal Property Registry dashboard. A general record
              of your search results will also be saved.
            </span>
            <span v-else id="no-results-info">
              No Registrations were found. Your search results and a printable PDF have been automatically
              saved to My Searches on your PPR Dashboard.
            </span>
          </v-col>
          <!-- to cut off in line with table submit btn -->
          <v-col cols="auto" style="width: 320px;" />
        </v-row>
        <v-row no-gutters style="padding-top: 24px;">
          <v-col :class="$style['search-note']">
            Note: If some of the selected matches are part of the same base registration, that base registration
            will only be shown in the report once.
          </v-col>
          <!-- to cut off in line with table submit btn -->
          <v-col cols="auto" style="width: 320px;" />
        </v-row>
      </div>
      <v-row v-if="getSearchResults" no-gutters style="padding-top: 38px;">
        <searched-result class="soft-corners" @selected-matches="updateSelectedMatches" @submit="submitCheck()" />
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
import { SearchedResult } from '@/components/tables'
import { SearchBar } from '@/components/search'
// local helpers/enums/interfaces/resources
import { RouteNames, SettingOptions } from '@/enums'
import {
  ActionBindingIF, ErrorIF, IndividualNameIF, // eslint-disable-line no-unused-vars
  SearchResponseIF, SearchResultIF, SearchTypeIF, UserSettingsIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import {
  largeSearchReportError,
  searchReportError,
  selectionConfirmaionDialog,
  largeSearchReportDelay
} from '@/resources/dialogOptions'
import { convertDate, getFeatureFlag, submitSelected, successfulPPRResponses, updateSelected } from '@/utils'

@Component({
  components: {
    BaseDialog,
    ConfirmationDialog,
    LargeSearchResultDialog,
    LargeSearchDelayDialog,
    SearchBar,
    SearchedResult
  }
})
export default class Search extends Vue {
  @Getter getSearchDebtorName: IndividualNameIF
  @Getter getSearchResults: SearchResponseIF
  @Getter getSearchedValue: string
  @Getter getSearchedType: SearchTypeIF
  @Getter getUserSettings: UserSettingsIF

  @Action setSearchDebtorName: ActionBindingIF
  @Action setSearchResults: ActionBindingIF
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

  private confirmationDialog = false
  private confirmOptions = selectionConfirmaionDialog
  private errorDialog = false
  private largeSearchResultDialog = false
  private largeSearchDelayDialog = false
  private errorOptions = searchReportError
  private largeSearchResultOptions = largeSearchReportError
  private largeSearchDelayOptions = largeSearchReportDelay
  private loading = false
  private selectedMatches: Array<SearchResultIF> = []
  private settingOption = SettingOptions.SELECT_CONFIRMATION_DIALOG

  private get folioNumber (): string {
    return this.getSearchResults?.searchQuery?.clientReferenceId || ''
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get searchTime (): string {
    // return formatted date
    const searchResult = this.getSearchResults
    if (searchResult) {
      const searchDate = new Date(searchResult.searchDateTime)
      return ` as of ${convertDate(searchDate, true, true)}`
    }
    return ''
  }

  private get searchType (): string {
    return this.getSearchedType?.searchTypeUI || ''
  }

  private get searchValue (): string {
    const searchResult = this.getSearchResults
    if (searchResult) {
      // will put in more logic when doing individual debtor
      const first = searchResult.searchQuery?.criteria?.debtorName?.first
      const second = searchResult.searchQuery?.criteria?.debtorName?.second
      const last = searchResult.searchQuery?.criteria?.debtorName?.last
      const business = searchResult.searchQuery?.criteria?.debtorName?.business
      if (first && last) {
        if (second) {
          return `${first} ${second} ${last}`
        }
        return `${first} ${last}`
      }
      return business || searchResult.searchQuery?.criteria?.value || ''
    }
    return ''
  }

  private get totalResultsLength (): number {
    const searchResult = this.getSearchResults
    if (searchResult) {
      return searchResult.totalResultsSize
    }
    return 0
  }

  private get exactResultsLength (): number {
    const searchResult = this.getSearchResults
    if (searchResult) {
      return searchResult.exactResultsSize
    }
    return 0
  }

  private get selectedResultsLength (): number {
    if (this.selectedMatches) {
      return this.selectedMatches.length
    }
    return 0
  }

  /** Use to conditionally display selection confirmation dialog. */
  private get similarResultsLength (): number {
    const searchResult = this.getSearchResults
    var similarCount = 0
    if (searchResult) {
      for (var result of searchResult.results) {
        if (result.matchType !== 'EXACT') {
          similarCount += 1
        }
      }
    }
    return similarCount
  }

  private handleReportError (stayOnSearchResults: boolean): void {
    this.errorDialog = false
    if (!stayOnSearchResults) {
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
  }

  private handleLargeReport (generateReport: boolean): void {
    if (generateReport) {
      this.submit(true)
    }
    this.largeSearchResultDialog = false
  }

  private handleDelayReport (acknowledge: boolean): void {
    this.submit(true)
    this.largeSearchDelayDialog = false
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  private submitCheck (): void {
    // if exact match is more than 75, inform about the delay
    if (this.exactResultsLength >= 75) {
      this.largeSearchDelayDialog = true
    // if they have selected more than 75 including inexact, give them the option
    } else if (this.selectedMatches?.length >= 75) {
      this.largeSearchResultDialog = true
    } else if (
      this.getUserSettings?.selectConfirmationDialog &&
      this.totalResultsLength > 0 && this.totalResultsLength < 75 &&
      this.similarResultsLength > 0 && this.similarResultsLength < 75
    ) {
      this.confirmOptions = { ...selectionConfirmaionDialog }
      this.confirmOptions.text = `<b>${this.selectedMatches?.length}</b> ${selectionConfirmaionDialog.text}`
      this.confirmationDialog = true
    } else {
      this.submit(true)
    }
  }

  private async submit (proceed: boolean): Promise<void> {
    this.confirmationDialog = false
    if (proceed) {
      this.loading = true
      let shouldCallback = false
      if (this.selectedMatches?.length >= 75) {
        shouldCallback = true
      }
      const statusCode = await submitSelected(this.getSearchResults.searchId, this.selectedMatches, shouldCallback)
      this.loading = false
      if (!successfulPPRResponses.includes(statusCode)) {
        this.emitError({ statusCode: statusCode })
      } else {
        this.$router.push({ name: RouteNames.DASHBOARD })
      }
    }
  }

  private async updateSelectedMatches (matches:Array<SearchResultIF>): Promise<void> {
    this.selectedMatches = matches
    const statusCode = await updateSelected(this.getSearchResults.searchId, matches)
    if (!successfulPPRResponses.includes(statusCode)) {
      this.emitError({ statusCode: statusCode })
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
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
    if (!this.getSearchResults) {
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
