<template>
  <v-container fluid class="pa-10">
    <v-row>
      <v-col>
        <v-row no-gutters>
          <v-col cols="12" :class="$style['search-title']">
            <b>Search</b>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="12" :class="[$style['search-info'], 'pt-2']">
            <span>
              Select a search category and then enter a value to search.
              <b>Note:</b>
              Each search incurs a fee (including searches that return no results).
            </span>
          </v-col>
        </v-row>
        <v-row>
          <!-- v-if reason: setting the props to null will cause the select to display 'null' -->
          <search-bar v-if="getSearchedType"
                      :defaultSearchValue="getSearchedValue"
                      :defaultSelectedSearchType="getSearchedType"
                      @search-error="emitError"
                      @search-data="setSearchResults"/>
          <search-bar v-else
                      @search-error="emitError"
                      @search-data="setSearchResults"/>
        </v-row>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-row no-gutters>
          <v-col cols="12" :class="$style['search-title']">
            <b>Search Results</b> <span :id="$style['search-time']"> {{ searchTime }}</span>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="12" :class="[$style['search-info'], 'pt-4']">
            <span v-if="!getSearchResults">
              Your search results will display below.
            </span>
            <span v-else-if="totalResultsLength !== 0">
              Select the registrations you want to download in a printable PDF.
              Your search results, selected registrations, and PDF are automatically saved to My Searches.
            </span>
            <span v-else>
              Your search results and PDF are automatically saved to My Searches.
            </span>
          </v-col>
        </v-row>
        <v-row v-if="getSearchResults" no-gutters justify="end" class="pt-5">
          <v-col cols="auto" class="pl-3">
            <v-btn :id="$style['done-btn']" color="outlined" class="search-done-btn" @click="submit">
              Done
            </v-btn>
          </v-col>
        </v-row>
        <v-row v-if="getSearchResults">
          <result :data="getSearchResults"/>
        </v-row>
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
// local
import { getFeatureFlag, convertDate } from '@/utils'
import { Result } from '@/components/results'
import { SearchBar } from '@/components/search'
import { ActionBindingIF, SearchResponseIF, SearchTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { RouteNames } from '@/enums'

@Component({
  components: {
    SearchBar,
    Result
  }
})
export default class Dashboard extends Vue {
  @Getter getSearchResults: SearchResponseIF
  @Getter getSearchedValue: string
  @Getter getSearchedType: SearchTypeIF

  @Action setSearchResults: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get searchTime (): string {
    // return formatted date
    const searchResult = this.getSearchResults
    if (searchResult) {
      const searchDate = new Date(searchResult.searchDateTime)
      return convertDate(searchDate)
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

  private downloadReport (): void {
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
  }

  private emitError (error) {
    // temporary until we know what errors to define
    if (error === 'payment') {
      this.emitPaymentError(error)
    } else {
      this.emitSaveSearchError(error)
    }
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  private submit (): void {
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
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

    // try to fetch data TBD
    try {
      // tell App that we're finished loading
      this.emitHaveData()
    } catch (err) {
      console.log(err) // eslint-disable-line no-console
      this.emitFetchError(err)
    }
  }

  /** Emits Fetch Error event. */
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
#download-report-btn {
  font-size: 0.825rem !important;
}
#search-time {
  font-size: 0.825rem;
  color: $gray8;
}
.search-title {
  font-size: 1rem;
  color: $gray9;
}
.search-info {
  font-size: 0.825rem;
  color: $gray8;
}
</style>
