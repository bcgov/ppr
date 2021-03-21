<template>
  <v-container fluid class="pa-10">
    <v-row no-gutters>
      <v-col>
        <!-- v-if reason: setting the props to null will cause the select to display 'null' -->
        <search-bar v-if="getSearchedType"
                    class="soft-corners"
                    :defaultSearchValue="getSearchedValue"
                    :defaultSelectedSearchType="getSearchedType"
                    @searched-type="setSearchedType"
                    @searched-value="setSearchedValue"
                    @search-error="emitError"
                    @search-data="setSearchResults"/>
        <search-bar v-else
                    class="soft-corners"
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
            <v-row no-gutters>
              <p>
                <span :class="$style['search-sub-title']"><b>for {{ searchType }} "{{ searchValue }}"</b></span>
                <span :class="$style['search-time']">{{ searchTime }}</span>
              </p>
            </v-row>
            <v-row no-gutters>
              <v-col cols="8" :class="$style['search-info']">
                <span v-if="totalResultsLength !== 0">
                  Select the registrations you want to include in a printable search report.
                  This report will contain the full record of each selected registration and will be
                  automatically saved to your PPR Dashboard.
                  A general record of your search results will also be saved.
                </span>
                <span v-else>
                  No Registrations were found. Your search results and a printable PDF have been automatically
                  saved to My Searches on your PPR Dashboard.
                </span>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-row v-if="getSearchResults" no-gutters justify="end" class="pt-5">
          <v-col v-if="folioNumber" align-self="start">
            <p class="pt-3 mb-0">
              <b :class="$style['search-table-title']">Folio Number: </b>
              <span :class="$style['search-info']">{{ folioNumber }}</span>
            </p>
          </v-col>
          <v-col cols="auto" class="pl-3">
            <v-btn :id="$style['done-btn']" class="search-done-btn pl-7 pr-7" @click="submit">
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
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
import { StatusCodes } from 'http-status-codes'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { convertDate, getFeatureFlag, submitSelected, updateSelected } from '@/utils'
import { SearchedResult } from '@/components/tables'
import { SearchBar } from '@/components/search'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  SearchResponseIF, // eslint-disable-line no-unused-vars
  SearchResultIF, // eslint-disable-line no-unused-vars
  SearchTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RouteNames } from '@/enums'

@Component({
  components: {
    SearchBar,
    SearchedResult
  }
})
export default class Search extends Vue {
  @Getter getSearchResults: SearchResponseIF
  @Getter getSearchedValue: string
  @Getter getSearchedType: SearchTypeIF

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

  private selectedMatches: Array<SearchResultIF> = []

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
      return ` as of ${convertDate(searchDate, true)}`
    }
    return ''
  }

  private get searchType (): string {
    return this.getSearchedType.searchTypeUI || ''
  }

  private get searchValue (): string {
    const searchResult = this.getSearchResults
    if (searchResult) {
      // will put in more logic when doing individual debtor
      return searchResult.searchQuery?.criteria?.value || ''
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

  private emitError (statusCode: number): void {
    const saveErrorCodes = [StatusCodes.INTERNAL_SERVER_ERROR, StatusCodes.BAD_REQUEST]
    if (statusCode === StatusCodes.PAYMENT_REQUIRED) {
      this.emitPaymentError()
    } else if (saveErrorCodes.includes(statusCode)) {
      this.emitSaveSearchError()
    } else if (statusCode === StatusCodes.UNAUTHORIZED) {
      this.emitAuthenticationError()
    } else {
      // temporary catch all (should be a more generic dialogue)
      this.emitSaveSearchError()
    }
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  private async submit (): Promise<void> {
    const statusCode = await submitSelected(this.getSearchResults.searchId, this.selectedMatches)
    if (statusCode !== StatusCodes.CREATED) {
      this.emitError(statusCode)
    } else {
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
  }

  private async updateSelectedMatches (matches:Array<SearchResultIF>): Promise<void> {
    this.selectedMatches = matches
    const statusCode = await updateSelected(this.getSearchResults.searchId, matches)
    if (statusCode !== StatusCodes.ACCEPTED) {
      this.emitError(statusCode)
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

  @Emit('authenticationError')
  private emitAuthenticationError (message: string = ''): void { }

  @Emit('fetchError')
  private emitFetchError (message: string = ''): void { }

  @Emit('paymentError')
  private emitPaymentError (message: string = ''): void { }

  @Emit('saveSearchError')
  private emitSaveSearchError (message: string = ''): void { }

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
