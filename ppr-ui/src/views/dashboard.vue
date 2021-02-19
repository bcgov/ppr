<template>
  <v-container fluid class="pa-10">
    <v-row no-gutters>
      <v-col cols="12" class="search-title">
        <b>Search</b>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12" class="search-info pt-2">
        <span>
          Select a search category and then enter a value to search.
          <b>Note:</b>
          Each search incurs a fee (including searches that return no results).
        </span>
      </v-col>
    </v-row>
    <v-row>
      <search @search-error="emitError" @search-data="setResults">
      </search>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { getFeatureFlag } from '@/utils'
import { Search } from '@/components/search'
import { SearchResponseIF } from '@/interfaces' // eslint-disable-line no-unused-vars

@Component({
  components: {
    Search
  }
})
export default class Dashboard extends Vue {
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

  private setResults (val:SearchResponseIF): void {
    // temp
    console.log(val)
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

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.search-title {
  font-size: 1rem;
  color: $gray9;
}
.search-info {
  font-size: 0.725rem;
  color: $gray8;
}
</style>
