<template>
  <v-container class="my-10 px-0">
    <v-overlay
      v-model="loading"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="30"
        indeterminate
      />
    </v-overlay>
    <h1 class="search-title">
      <v-icon
        size="32"
        class="pr-1 mt-n1"
      >
        mdi-home
      </v-icon>
      Selection List
    </h1>
    <p
      v-if="!getManufacturedHomeSearchResults"
      class="search-info ma-0"
    >
      Your search results will display below.
    </p>
    <div v-else>
      <v-row
        no-gutters
        class="mt-6"
      >
        <v-col class="search-info pr-6">
          <p
            v-if="totalResultsLength !== 0"
            id="results-info"
          >
            Select manufactured home registrations to download a search result report containing the full details of
            the registration(s). Lien information contained in the Personal Property Registry can be included for an
            additional fee per manufactured home registration. You will be able to review your selection prior to
            payment.
          </p>
          <span
            v-else
            id="no-results-info"
          >
            No Registrations were found.
          </span>
        </v-col>
      </v-row>
    </div>
    <v-row
      v-if="getManufacturedHomeSearchResults"
      no-gutters
      class="pt-9"
    >
      <SearchedResultMhr
        class="rounded-top pb-6"
        :is-review-mode="false"
      />
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from 'vue'
import { useStore } from '../../src/store/store'
import { SearchedResultMhr } from '../../src/components/tables'
import { RouteNames } from '../../src/enums'
import { getFeatureFlag } from '../../src/utils'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation } from '../../src/composables'

export default defineComponent({
  name: 'MHRSearch',
  components: {
    SearchedResultMhr
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    attachDialog: {
      type: String,
      default: '#app'
    },
    registryUrl: {
      type: String,
      default: 'https://bcregistry.ca'
    }
  },
  emits: ['haveData'],
  setup (props, context) {
    const { goToDash, isRouteName, navigateTo } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { getManufacturedHomeSearchResults } = storeToRefs(useStore())

    const localState = reactive({
      loading: false,
      totalResultsLength: computed((): number => {
        const searchResult = getManufacturedHomeSearchResults.value
        if (searchResult) {
          return searchResult.totalResultsSize
        }
        return 0
      })
    })

    onBeforeMount((): void => {
      window.onbeforeunload = (event) => {
        // unsaved selections if app is ready, search results exist, and on the search page
        const isSearchReportUnsaved = (
          isRouteName(RouteNames.MHRSEARCH) && props.appReady && !!getManufacturedHomeSearchResults.value
        )

        if (isSearchReportUnsaved) {
          event.preventDefault()
          // NB: custom text is no longer supported by newest versions of all browsers since 2021 for security reasons
          // the event.returnValue is now only treated as a flag (added text in case this ever changes)
          event.returnValue = 'You have not saved your search result report. Are you sure you want to leave?'
        }
      }
    })

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = (val: boolean): void => {
      // do not proceed if app is not ready
      if (!val) return

      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || !getFeatureFlag('ppr-ui-enabled')) {
        window.alert('Personal Property Registry is under construction. Please check again later.')
        navigateTo(props.registryUrl)
        return
      }

      // if navigated here without search results redirect to the dashboard
      if (!getManufacturedHomeSearchResults.value) {
        goToDash()
        emitHaveData(false)
        return
      }

      // page is ready
      emitHaveData(true)
    }

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    return {
      getManufacturedHomeSearchResults,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '../../src/assets/styles/theme';
</style>
