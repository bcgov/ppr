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
      <div v-else>
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
        <searched-result-mhr class="soft-corners" />
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from 'vue-demi'
import { useRouter } from 'vue2-helpers/vue-router'
import { useStore } from '@/store/store'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { SearchedResultMhr } from '@/components/tables'
import { RouteNames } from '@/enums'
import { getFeatureFlag, navigate } from '@/utils'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'MHRSearch',
  components: {
    SearchedResultMhr
  },
  emits: ['haveData'],
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    isJestRunning: {
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
  setup (props, context) {
    const router = useRouter()
    const {
      getManufacturedHomeSearchResults
    } = storeToRefs(useStore())

    const localState = reactive({
      loading: false,
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
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
          router.currentRoute.name === RouteNames.MHRSEARCH &&
           props.appReady &&
           !!getManufacturedHomeSearchResults.value
        )

        if (isSearchReportUnsaved) {
          event.preventDefault()
          // NB: custom text is no longer supported by newest versions of all browsers since 2021 for security reasons
          // the event.returnValue is now only treated as a flag (added text in case this ever changes)
          event.returnValue = 'You have not saved your search result report. Are you sure you want to leave?'
        }
      }
    })

    /** Redirects browser to Business Registry home page. */
    const redirectRegistryHome = (): void => {
      navigate(props.registryUrl)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: Boolean = true): void => {
      context.emit('haveData', haveData)
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = (val: boolean): void => {
      // do not proceed if app is not ready
      if (!val) return

      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!localState.isAuthenticated || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        window.alert('Personal Property Registry is under construction. Please check again later.')
        redirectRegistryHome()
        return
      }

      // if navigated here without search results redirect to the dashboard
      if (!getManufacturedHomeSearchResults) {
        router.push({
          name: RouteNames.DASHBOARD
        })
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
