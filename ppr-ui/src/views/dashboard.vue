<template>
  <v-container fluid class="pa-10">
    <v-row no-gutters>
      <v-col>
        <v-row no-gutters :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
          <v-col cols="auto">
            <b>Personal Property Search</b>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <search-bar class="soft-corners-bottom"
                      @searched-type="setSearchedType"
                      @searched-value="setSearchedValue"
                      @search-data="setSearchResults"
                      @search-error="emitError"/>
        </v-row>
      </v-col>
    </v-row>
    <v-row no-gutters class='pt-12'>
      <v-col>
        <v-row no-gutters :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
          <v-col cols="auto">
            <b>My Searches</b> (110)
          </v-col>
        </v-row>
        <v-row no-gutters>
          <saved-result class="soft-corners-bottom"/>
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
import { getFeatureFlag } from '@/utils'
import { SavedResult } from '@/components/results'
import { SearchBar } from '@/components/search'
import { ActionBindingIF, SearchResponseIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { RouteNames } from '@/enums'

@Component({
  components: {
    SavedResult,
    SearchBar
  }
})
export default class Dashboard extends Vue {
  @Getter getSavedResults: SearchResponseIF
  @Getter getSearchResults: SearchResponseIF

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
    this.setSearchedType(null)
    this.setSearchedValue('')
    this.setSearchResults(null)
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
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

  @Watch('getSearchResults')
  private onSearch (val: SearchResponseIF): void {
    // navigate to search page if not null/reset
    if (val) {
      this.$router.push({
        name: RouteNames.SEARCH
      })
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
.dashboard-title {
  font-size: 1rem;
  color: $gray9;
  background-color: $BCgovBlue0;
}
</style>
