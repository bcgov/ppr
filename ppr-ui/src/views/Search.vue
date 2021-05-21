<template>
  <v-container fluid class="pa-0" style="max-width: none;">
    <confirmation-dialog
      :attach="attachDialog"
      :options="options"
      :display="confirmationDialog"
      :settingOption="settingOption"
      @proceed="submit"
    />
    <v-row no-gutters>
      <v-container fluid class="pa-10">
        <v-row no-gutters>
          <v-col>
            <!-- v-if reason: setting the props to null will cause the select to display 'null' -->
            <search-bar v-if="getSearchedType"
                        class="soft-corners"
                        :defaultDebtor="getDebtorName"
                        :defaultFolioNumber="folioNumber"
                        :defaultSearchValue="getSearchedValue"
                        :defaultSelectedSearchType="getSearchedType"
                        @debtor-name="setDebtorName"
                        @searched-type="setSearchedType"
                        @searched-value="setSearchedValue"
                        @search-error="emitError"
                        @search-data="setSearchResults"/>
            <search-bar v-else
                        class="soft-corners"
                        @debtor-name="setDebtorName"
                        @searched-type="setSearchedType"
                        @searched-value="setSearchedValue"
                        @search-error="emitError"
                        @search-data="setSearchResults"/>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col>
            <v-row no-gutters class="pt-8">
              <v-col :class="$style['search-title']">
                <b>Search Results</b>
              </v-col>
            </v-row>
            <v-row v-if="!getSearchResults" no-gutters>
              <v-col :class="$style['search-info']">
                  Your search results will display below.
              </v-col>
            </v-row>
            <v-row v-else no-gutters class="pt-2">
              <v-col>
                <v-row no-gutters id="search-meta-info">
                  <p>
                    <span :class="$style['search-sub-title']"><b>for {{ searchType }} "{{ searchValue }}"</b></span>
                    <span :class="$style['search-time']">{{ searchTime }}</span>
                  </p>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="8" :class="$style['search-info']">
                    <span v-if="totalResultsLength !== 0" id="results-info">
                      Select the registrations you want to include in a printable search report.
                      This report will contain the full record of each selected registration and will be
                      automatically saved to your PPR Dashboard.
                      A general record of your search results will also be saved.
                    </span>
                    <span v-else id="no-results-info">
                      No Registrations were found. Your search results and a printable PDF have been automatically
                      saved to My Searches on your PPR Dashboard.
                    </span>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
            <v-row v-if="getSearchResults" no-gutters justify="end" class="pt-5">
              <v-col v-if="folioNumber" id="results-folio-header" align-self="start">
                <p class="pt-3 mb-0">
                  <b :class="$style['search-table-title']">Folio Number: </b>
                  <span :class="$style['search-info']">{{ folioNumber }}</span>
                </p>
              </v-col>
              <v-col cols="auto" class="pl-3">
                <v-btn :id="$style['done-btn']" class="search-done-btn pl-7 pr-7 primary" @click="submitCheck">
                  Done
                </v-btn>
              </v-col>
            </v-row>
            <v-row v-if="getSearchResults" no-gutters class='pt-5'>
              <searched-result class="soft-corners" @selected-matches="updateSelectedMatches"/>
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
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { RouteNames, SettingOptions } from '@/enums'
import {
  ActionBindingIF, DialogOptionsIF, ErrorIF, IndividualNameIF, // eslint-disable-line no-unused-vars
  SearchResponseIF, SearchResultIF, SearchTypeIF, UserSettingsIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { selectionConfirmaionDialog } from '@/resources'
import { convertDate, getFeatureFlag, submitSelected, successfulPPRResponses, updateSelected } from '@/utils'
// local components
import { ConfirmationDialog } from '@/components/dialogs'
import { SearchedResult } from '@/components/tables'
import { SearchBar } from '@/components/search'

@Component({
  components: {
    ConfirmationDialog,
    SearchBar,
    SearchedResult
  }
})
export default class Search extends Vue {
  @Getter getDebtorName: IndividualNameIF
  @Getter getSearchResults: SearchResponseIF
  @Getter getSearchedValue: string
  @Getter getSearchedType: SearchTypeIF
  @Getter getUserSettings: UserSettingsIF

  @Action setDebtorName: ActionBindingIF
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

  private confirmationDialog: boolean = false

  private options: DialogOptionsIF = selectionConfirmaionDialog

  private selectedMatches: Array<SearchResultIF> = []

  private settingOption: string = SettingOptions.SELECT_CONFIRMATION_DIALOG

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

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  private submitCheck (): void {
    if (this.getUserSettings?.selectConfirmationDialog && this.totalResultsLength > 0 &&
                             this.similarResultsLength > 0) {
      this.options = { ...selectionConfirmaionDialog }
      this.options.text = `<b>${this.selectedMatches?.length}</b> ${selectionConfirmaionDialog.text}`
      this.confirmationDialog = true
    } else {
      this.submit(true)
    }
  }

  private async submit (proceed: boolean): Promise<void> {
    this.confirmationDialog = false
    if (proceed) {
      const statusCode = await submitSelected(this.getSearchResults.searchId, this.selectedMatches)
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
    this.emitHaveData()
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
  font-size: 2rem;
  color: $gray9;
}
.search-sub-title {
  font-size: 1.1rem;
  color: $gray8;
}
.search-time {
  font-size: 1rem;
  color: $gray7;
}
.search-info {
  font-size: 1rem;
  line-height: 1.5rem;
  color: $gray7;
}
.search-table-title {
  font-size: 1rem;
  color: $gray9;
}
</style>
