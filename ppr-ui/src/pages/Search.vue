<template>
  <v-container class="px-0 py-12">
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
    <BaseDialog
      :set-display="errorDialog"
      :set-options="errorOptions"
      @proceed="handleReportError($event)"
    />
    <LargeSearchResultDialog
      :set-display="largeSearchResultDialog"
      :set-options="largeSearchResultOptions"
      :set-number-registrations="selectedResultsLength"
      @proceed="handleLargeReport($event)"
    />
    <LargeSearchDelayDialog
      :set-display="largeSearchDelayDialog"
      :set-options="largeSearchDelayOptions"
      :set-number-registrations="exactResultsLength"
      @proceed="handleDelayReport($event)"
    />
    <ConfirmationDialog
      :set-display="confirmationDialog"
      :set-options="confirmOptions"
      :set-setting-option="settingOption"
      @proceed="submit($event)"
    />
    <section>
      <h1 class="search-title">
        Search Results
      </h1>
      <p
        v-if="!getSearchResults"
        class="search-info ma-0 pt-6"
      >
        Your search results will display below.
      </p>
      <div
        v-else
        class="pt-6"
      >
        <p
          id="search-meta-info"
          class="ma-0"
        >
          <span class="search-sub-title font-weight-bold">for {{ searchType }} "{{ searchValue }}"</span>
          <span class="search-info">{{ searchTime }}</span>
        </p>
        <p
          v-if="folioNumber"
          id="results-folio-header"
          class="ma-0 pt-6"
        >
          <b class="search-table-title">Folio Number: </b>
          <span class="search-info">{{ folioNumber }}</span>
        </p>
        <v-row
          no-gutters
          class="pt-6"
        >
          <v-col
            cols="9"
            class="'search-info pr-4"
          >
            <p
              v-if="totalResultsLength !== 0"
              id="results-info"
            >
              Select the registrations you want to include in a printable PDF search report. Exact matches
              are automatically selected. This report will contain the full record of the registration for
              each selected match and will be automatically saved to your PPR Dashboard.
            </p>
            <p
              v-else
              id="no-results-info"
            >
              No Registrations were found. A printable PDF search result report and a general record of your search
              will be saved to your Personal Property Registry dashboard.
            </p>
          </v-col>
        </v-row>
      </div>
      <v-row
        v-if="getSearchResults"
        no-gutters
        class="pt-9"
      >
        <SearchedResultsPpr
          class="rounded-top py-10"
          @selected-matches="updateSelectedMatches"
          @submit="submitCheck()"
        />
      </v-row>
    </section>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { MatchTypes, RouteNames, SettingOptions } from '@/enums'
import {
  largeSearchReportError,
  searchReportError,
  selectionConfirmaionDialog,
  largeSearchReportDelay,
  saveResultsError,
  saveSelectionsError
} from '@/resources/dialogOptions'
import { getFeatureFlag, pacificDate } from '@/utils'
import { submitSelected, successfulPPRResponses, updateSelected } from '@/utils/ppr-api-helper'
import type { SearchResultIF } from '@/interfaces'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation } from '@/composables'
import SearchedResultsPpr from '@/components/tables/ppr/SearchedResultsPpr.vue'

export default defineComponent({
  name: 'Search',
  components: {
    SearchedResultsPpr
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
    const router = useRouter()
    const { goToDash, navigateToUrl } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      getSearchedType,
      getUserSettings,
      getSearchResults
    } = storeToRefs(useStore())

    const localState = reactive({
      loading: false,
      confirmationDialog: false,
      confirmOptions: selectionConfirmaionDialog,
      errorDialog: false,
      largeSearchResultDialog: false,
      largeSearchDelayDialog: false,
      errorOptions: searchReportError,
      largeSearchResultOptions: largeSearchReportError,
      largeSearchDelayOptions: largeSearchReportDelay,
      selectedMatches: [] as Array<SearchResultIF>,
      settingOption: SettingOptions.SELECT_CONFIRMATION_DIALOG,
      folioNumber: computed((): string => {
        return getSearchResults.value?.searchQuery?.clientReferenceId || ''
      }),
      searchTime: computed((): string => {
        // return formatted date
        const searchResult = getSearchResults.value
        if (searchResult) {
          const searchDate = new Date(searchResult.searchDateTime)
          return ` as of ${pacificDate(searchDate)}`
        }
        return ''
      }),
      searchType: computed((): string => {
        return getSearchedType.value?.searchTypeUI || ''
      }),
      searchValue: computed((): string => {
        const searchResult = getSearchResults.value
        if (searchResult) {
          // will put in more logic when doing individual debtor
          const first = searchResult.searchQuery?.criteria?.debtorName?.first
          const second = searchResult.searchQuery?.criteria?.debtorName?.second
          const last = searchResult.searchQuery?.criteria?.debtorName?.last
          const business = searchResult.searchQuery?.criteria?.debtorName?.business
          if (first && last) {
            if (second) {
              return `${last}, ${first} ${second}`
            }
            return `${last}, ${first}`
          }
          return business || searchResult.searchQuery?.criteria?.value || ''
        }
        return ''
      }),
      totalResultsLength: computed((): number => {
        const searchResult = getSearchResults.value
        if (searchResult) {
          return searchResult.totalResultsSize
        }
        return 0
      }),
      exactResultsLength: computed((): number => {
        const selectedExactMatches = []
        const results = getSearchResults.value?.results
        let count = 0
        let x: any
        for (x in results) {
          if (results[x].matchType === MatchTypes.EXACT) {
            count += 1
            selectedExactMatches.push(results[x])
          }
        }
        return count
      }),
      selectedResultsLength: computed((): number => {
        if (localState.selectedMatches) {
          return localState.selectedMatches.length
        }
        return 0
      }),
      similarResultsLength: computed((): number => {
        const searchResult = getSearchResults.value
        let similarCount = 0
        if (searchResult && searchResult.results) {
          for (const result of searchResult.results) {
            if (result.matchType !== 'EXACT') {
              similarCount += 1
            }
          }
        }
        return similarCount
      })
    })

    onBeforeMount((): void => {
      window.onbeforeunload = (event) => {
        // unsaved selections if app is ready, search results exist, and on the search page
        const isSearchReportUnsaved = (
          router.currentRoute.name === RouteNames.SEARCH &&
          props.appReady &&
          !!getSearchResults
        )
        if (isSearchReportUnsaved) {
          event.preventDefault()
          // NB: custom text is no longer supported by newest versions of all browsers since 2021 for security reasons
          // the event.returnValue is now only treated as a flag (added text in case this ever changes)
          event.returnValue = 'You have not saved your search result report. Are you sure you want to leave?'
        }
      }
    })

    const handleReportError = (stayOnSearchResults: boolean): void => {
      localState.errorDialog = false
      if (!stayOnSearchResults || (localState.errorOptions !== searchReportError &&
        localState.errorOptions !== saveSelectionsError)) {
        goToDash()
      }
    }

    const handleLargeReport = (generateReport: boolean): void => {
      if (generateReport) {
        submit(true)
      }
      localState.largeSearchResultDialog = false
    }

    const handleDelayReport = (): void => {
      submit(true)
      localState.largeSearchDelayDialog = false
    }

    const redirectRegistryHome = (): void => {
      navigateToUrl(props.registryUrl)
    }

    const submitCheck = (): void => {
      // if exact match is more than 75, inform about the delay
      if (localState.exactResultsLength >= 75) {
        localState.largeSearchDelayDialog = true
        // if they have selected more than 75 including inexact, give them the option
      } else if (localState.selectedMatches?.length >= 75) {
        localState.largeSearchResultDialog = true
      } else if (
        getUserSettings.value?.selectConfirmationDialog &&
        localState.totalResultsLength > 0 && localState.totalResultsLength < 75 &&
        localState.similarResultsLength > 0 && localState.similarResultsLength < 75
      ) {
        localState.confirmOptions = { ...selectionConfirmaionDialog }
        localState.confirmOptions.text =
          `<b>${localState.selectedMatches?.length}</b> ${selectionConfirmaionDialog.text}`
        localState.confirmationDialog = true
      } else {
        submit(true)
      }
    }

    const submit = async (proceed: boolean): Promise<void> => {
      localState.confirmationDialog = false
      if (proceed) {
        localState.loading = true
        let shouldCallback = false
        if (localState.selectedMatches?.length >= 75) {
          shouldCallback = true
        }
        const statusCode =
          await submitSelected(getSearchResults.value.searchId, localState.selectedMatches, shouldCallback)
        localState.loading = false
        if (!successfulPPRResponses.includes(statusCode)) {
          localState.errorOptions = { ...saveResultsError }
          localState.errorDialog = true
          console.error({ statusCode })
        } else {
          goToDash()
        }
      }
    }

    const updateSelectedMatches = async (matches: Array<SearchResultIF>): Promise<void> => {
      localState.selectedMatches = matches
      const statusCode = await updateSelected(getSearchResults.value.searchId, matches)
      if (!successfulPPRResponses.includes(statusCode)) {
        localState.errorOptions = { ...saveSelectionsError }
        localState.errorDialog = true
      }
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return

      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || !getFeatureFlag('ppr-ui-enabled')) {
        window.alert('Personal Property Registry is under contruction. Please check again later.')
        redirectRegistryHome()
        return
      }

      // if navigated here without search results redirect to the dashboard
      if (!getSearchResults) {
        goToDash()
        emitHaveData(false)
        return
      }

      // page is ready
      emitHaveData(true)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    return {
      submit,
      submitCheck,
      getSearchResults,
      handleReportError,
      handleLargeReport,
      handleDelayReport,
      redirectRegistryHome,
      updateSelectedMatches,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
//@import '@/assets/styles/theme.scss';
</style>
