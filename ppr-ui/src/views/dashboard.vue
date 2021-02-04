<template>
  <v-container fluid class="copy-normal pa-10">
    <v-row no-gutters>
      hello world
    </v-row>
    <search class ="mt-10">
    </search>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Search } from '@/components/search'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

@Component({
  components: {
    Search
  }
})
export default class Dashboard extends Vue {
  // Local Properties
  searchOptions = [
    'Serial Number',
    'something'
  ]

  selected = null

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  /** Called when App is ready and this component can load its data. */
  @Watch('appReady')
  private async onAppReady (val: boolean): Promise<void> {
    // do not proceed if app is not ready
    if (!val) return

    // do not proceed if we are not authenticated (safety check - should never happen)
    if (!this.isAuthenticated) return

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

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void { }
}
</script>

<style lang="scss" scoped>

</style>
