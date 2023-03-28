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
              Select the registrations you want to include in a printable PDF search report. Exact matches
              are automatically selected. This report will contain the full record of the registration for
              each selected match and will be automatically saved to your PPR Dashboard.
            </span>
            <span v-else id="no-results-info">
              No Registrations were found. A printable PDF search result report and a general record of your search
              will be saved to your Personal Property Registry dashboard.
            </span>
          </v-col>
          <!-- to cut off in line with table submit btn -->
          <v-col cols="auto" style="width: 320px;" />
        </v-row>
      </div>
      <v-row v-if="getSearchResults" no-gutters style="padding-top: 38px;">
        <searched-result-ppr class="soft-corners" @selected-matches="updateSelectedMatches" @submit="submitCheck()" />
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import {
  BaseDialog,
  ConfirmationDialog,
  LargeSearchResultDialog,
  LargeSearchDelayDialog
} from '@/components/dialogs'
import { SearchedResultPpr } from '@/components/tables'
import { SearchBar } from '@/components/search'
import { MatchTypes, RouteNames, SettingOptions } from '@/enums'
import {
  largeSearchReportError,
  searchReportError,
  selectionConfirmaionDialog,
  largeSearchReportDelay,
  saveResultsError,
  saveSelectionsError
} from '@/resources/dialogOptions'
import { getFeatureFlag, submitSelected, successfulPPRResponses, updateSelected, navigate, pacificDate } from '@/utils'
import { ErrorIF, SearchResultIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'Search',
  components: {
    BaseDialog,
    ConfirmationDialog,
    LargeSearchResultDialog,
    LargeSearchDelayDialog,
    SearchBar,
    SearchedResultPpr
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
    const {
      getSearchedType,
      getUserSettings,
      getSearchResults
    } = useGetters([
      'getSearchedType',
      'getUserSettings',
      'getSearchResults'
    ])

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
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
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
        let x:any
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
        if (searchResult) {
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
          context.root.$router.currentRoute.name === RouteNames.SEARCH &&
          props.appReady &&
          !!getSearchResults.value
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
        context.root.$router.push({ name: RouteNames.DASHBOARD })
      }
    }

    const handleLargeReport = (generateReport: boolean): void => {
      if (generateReport) {
        submit(true)
      }
      localState.largeSearchResultDialog = false
    }

    const handleDelayReport = (acknowledge: boolean): void => {
      submit(true)
      localState.largeSearchDelayDialog = false
    }

    const redirectRegistryHome = (): void => {
      navigate(props.registryUrl)
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
          console.error({ statusCode: statusCode })
        } else {
          context.root.$router.push({ name: RouteNames.DASHBOARD })
        }
      }
    }

    const updateSelectedMatches = async (matches:Array<SearchResultIF>): Promise<void> => {
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
      if (!localState.isAuthenticated || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        window.alert('Personal Property Registry is under contruction. Please check again later.')
        redirectRegistryHome()
        return
      }

      // if navigated here without search results redirect to the dashboard
      if (!getSearchResults.value) {
        context.root.$router.push({
          name: RouteNames.DASHBOARD
        })
        emitHaveData(false)
        return
      }

      // page is ready
      emitHaveData(true)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: Boolean = true): void => {
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
