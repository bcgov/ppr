<script lang="ts">
import {
  computed,
  defineComponent,
  nextTick,
  reactive,
  toRefs,
  watch,
  onMounted
} from 'vue'
import { useStore } from '@/store/store'
import type { SearchCriteriaIF, SearchResponseIF, SearchTypeIF } from '@/interfaces'
import { MHRSearchTypes, searchHistoryTableHeaders, searchHistoryTableHeadersStaff, SearchTypes } from '@/resources'
import { convertDate } from '@/utils'
import { searchPDF, submitSelected, successfulPPRResponses } from '@/utils/ppr-api-helper'
import { searchMhrPDF, delayActions } from '@/utils/mhr-api-helper'
import { useSearch } from '@/composables/useSearch'
import { cloneDeep } from 'lodash' // eslint-disable-line
import _ from 'lodash' // eslint-disable-line
import { ErrorCategories, FilterTypes } from '@/enums'
import { useTableFeatures } from '@/composables'
import { storeToRefs } from 'pinia'
import AriaLabel from './AriaLabel.vue'
import SearchBarList from '@/components/search/SearchBarList.vue'

export default defineComponent({
  components: {
    AriaLabel,
    SearchBarList
  },
  props: {
    searchAdded: { type: Boolean, default: false },
    searchAddedId: { type: String, default: '' }
  },
  emits: ['error', 'retry'],
  setup (props, { emit }) {
    const { goToPay } = useNavigation()
    const {
      getSearchHistory,
      getUserUsername,
      isRoleStaff,
      hasPprRole,
      hasMhrRole
    } = storeToRefs(useStore())

    const localState = reactive({
      keyValue: 0,
      sortAsc: false,
      headers: computed((): Array<any> => {
        const tableHeaders = cloneDeep(searchHistoryTableHeaders)
        if (localState.isStaff) {
          return searchHistoryTableHeadersStaff
        }
        return tableHeaders
      }),
      selectedSearchType: null,
      showDatePicker: false,
      dateTxt: '',
      filters: {},
      hasBothRoles: computed((): boolean => {
        return hasPprRole.value && hasMhrRole.value
      }),
      isStaff: computed((): boolean => {
        return !!isRoleStaff.value
      }),
      historyLength: computed((): number => {
        return localState.searchHistory?.length || 0
      }),
      searchHistory: computed(
        (): Array<SearchResponseIF> => {
          return getSearchHistory.value || []
        }
      ),
      isSearchHistory: computed((): boolean => {
        return !!getSearchHistory.value
      })
    })

    onMounted(() => {
      resetFilters()
    })

    const { mapMhrSearchType } = useSearch()
    const { sortDates } = useTableFeatures()
    const displayDate = (searchDate: string): string => {
      const date = new Date(searchDate)
      return convertDate(date, true, false)
    }
    const displaySearchValue = (query: SearchCriteriaIF): string => {
      const individualKey = Object.keys(query?.criteria)[0]
      const first = query?.criteria?.[individualKey]?.first
      const second = query?.criteria?.[individualKey]?.second || query?.criteria?.[individualKey]?.middle
      const last = query?.criteria?.[individualKey]?.last
      const business = query?.criteria?.debtorName?.business
      if (first || last) {
        if (second) {
          return `${first} ${second} ${last}`
        }
        return `${first} ${last}`
      }
      return business || query?.criteria?.value || ''
    }
    const displayType = (APISearchType: string): string => {
      let UISearchType = ''
      for (let i = 0; i < SearchTypes.length; i++) {
        if (APISearchType === SearchTypes[i].searchTypeAPI) {
          UISearchType = SearchTypes[i].searchTypeUI
          break
        }
      }
      return UISearchType
    }
    const displayMhrType = (APISearchType: string): string => {
      let UISearchType = ''
      for (let i = 0; i < MHRSearchTypes.length; i++) {
        if (mapMhrSearchType(APISearchType, true) === MHRSearchTypes[i].searchTypeAPI) {
          UISearchType = MHRSearchTypes[i].searchTypeUI
          break
        }
      }
      return UISearchType
    }
    const downloadPDF = async (item: SearchResponseIF): Promise<boolean> => {
      item.loadingPDF = true
      let pdf:any = null
      if (item.isPending) {
        item.loadingPDF = true
        await delayActions(5000)
      }
      if (isPprSearch(item)) {
        pdf = await searchPDF(item.searchId)
      } else {
        pdf = await searchMhrPDF(item.searchId)
      }
      if (pdf.error) {
        if (pdf.error.statusCode === 400 && pdf.error.category === ErrorCategories.REPORT_GENERATION) {
          // log to console if pdf report is still pending
          console.info('PDF Report is not ready yet.')
        } else {
          // emit and show modal for a server error
          emit('error', pdf.error)
        }
        item.loadingPDF = false
        return false
      } else if (pdf && item.isPending) {
        // prevent automatic downloads of pending PDFs
        item.loadingPDF = false
        item.isPending = false
        return true
      } else {
        /* solution from https://github.com/axios/axios/issues/1392 */

        // it is necessary to create a new blob object with mime-type explicitly set
        // otherwise only Chrome works like it should
        const blob = new Blob([pdf], { type: 'application/pdf' })

        // IE doesn't allow using a blob object directly as link href
        // instead it is necessary to use msSaveOrOpenBlob
        if (window.navigator && (window.navigator as any).msSaveOrOpenBlob) {
          (window.navigator as any).msSaveOrOpenBlob(blob, item.searchId)
        } else {
          // for other browsers, create a link pointing to the ObjectURL containing the blob
          const url = window.URL.createObjectURL(blob)
          const a = window.document.createElement('a')
          window.document.body.appendChild(a)
          a.setAttribute('style', 'display: none')
          a.href = url
          // Format (PPR): [Date (in YYYY-MM-DD format)] BCPPR Search Result - [Search Criteria] Search ID
          // Example: 2022-01-03 BCPPR BO Search Result - Telus Communications Inc. Search ID

          // Format (MHR): [Date (in YYYY-MM-DD format)] BCMHR Search Result - [Search Criteria] Search ID
          // Example: 2022-03-13 BCMHR Search Result - 001919 - 13492

          const today = new Date()
          const searchValue = displaySearchValue(item.searchQuery).replace(/ /g, '_').split('.').join('')
          a.download = today.toISOString().slice(0, 10) + `_BC${isPprSearch(item) ? 'PPR' : 'MHR'}_Search_Result_` +
            searchValue + '_' + item.searchId
          a.click()
          window.URL.revokeObjectURL(url)
          a.remove()
        }
      }
      item.loadingPDF = false
      item.isPending = false
      return true
    }
    const generateReport = async (item: SearchResponseIF): Promise<void> => {
      let callBack = false
      if (item.selectedResultsSize >= 75) callBack = true
      // item searchId may be flipped to pending so keep track of real id with constant
      const searchId = item.searchId
      item.loadingPDF = true
      // wait at least 1 second
      setTimeout(async () => {
        // stop waiting after 5 seconds
        setTimeout(() => {
          // set to pending if submit was not finished
          if (item.inProgress) {
            item.loadingPDF = false
            item.isPending = true
          }
        }, 5000)
        const statusCode = await submitSelected(searchId, [], callBack, true)
        // FUTURE: add error handling, for now just ignore so they can try again
        if (successfulPPRResponses.includes(statusCode)) {
          if (item.selectedResultsSize >= 75) {
            item.isPending = true
          } else item.searchId = searchId
          item.inProgress = false
        }
        item.loadingPDF = false
        item.isPending = false
      }, 1000)
    }
    const getTooltipTxtPdf = (item: SearchResponseIF): string => {
      if (item.inProgress) {
        if (isSearchOwner(item)) {
          return 'The document PDF has not been generated. Click the ' +
            '<i class="v-icon notranslate mdi mdi-information-outline" ' +
            'style="font-size:20px;"></i>' +
            ' icon to generate your PDF.</p>' +
            'Note: Large documents may take up to 20 minutes to generate.'
        }
        return 'This search is in progress by another user.'
      }
      if (!isPDFAvailable(item)) {
        return 'This document PDF is no longer available.'
      }
      return 'This document PDF is still being generated. Click the ' +
        '<i class="v-icon notranslate mdi mdi-information-outline" style="font-size:20px;"></i> ' +
        'icon to see if your PDF is ready to download. </p>' +
        'Note: Large documents may take up to 20 minutes to generate.'
    }
    const isPDFAvailable = (item: SearchResponseIF): boolean => {
      const now = new Date()
      const nowDate = new Date(now.toDateString())
      const searchDatetime = new Date(item.searchDateTime)
      const searchDate = new Date(searchDatetime.toDateString())
      const diffTime = nowDate.getTime() - searchDate.getTime()
      const diffDays = diffTime / (1000 * 3600 * 24)
      return diffDays < 15
    }
    const isSearchOwner = (item: SearchResponseIF): boolean => {
      return getUserUsername.value === item?.userId
    }
    const retrySearch = (): void => {
      emit('retry')
    }
    const isPprSearch = (item: SearchResponseIF): boolean => {
      return item.exactResultsSize >= 0
    }
    const refreshRow = async (item): Promise<void> => {
      const pdf = await downloadPDF(item)
      if (pdf) {
        // Update unique key value of table row to refresh singular component
        localState.keyValue += 1
      }
    }
    /** Date sort handler to sort and change sort icon state **/
    const dateSortHandler = (searchHistory: Array<SearchResponseIF>, dateType: string, reverse: boolean) => {
      localState.sortAsc = !localState.sortAsc
      sortDates(searchHistory, dateType, reverse)
    }

    /** Scroll to Search Table **/
    async function scrollToAddedSearch(): Promise<void> {
      setTimeout(() => {
        document?.querySelector('.added-search-effect')?.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        })
      }, 300)
    }

    const returnSearchSelection = (selection: SearchTypeIF) => {
      localState.selectedSearchType = selection
    }

    const updateDateRange = (dates: { endDate: Date, startDate: Date }) => {
      if (!(dates.endDate && dates.startDate)) localState.dateTxt = ''
      else localState.dateTxt = 'Custom'
      localState.showDatePicker = false
    }
    const resetFilters = () => {
      localState.headers.forEach(header => {
        if(header.filter) {
          localState.filters[header.value] = ''
        }
      })
    }
    const clearFilters = () => {
      resetFilters()
    }

    /** Scroll to event on added search **/
    watch(() => [props.searchAdded, props.searchAddedId], async () => {
      if (props.searchAdded) {
        await nextTick()
        await scrollToAddedSearch()
      }
      if (props.searchAddedId) {
        const index = localState.searchHistory.findIndex(
          (item: SearchResponseIF) => item.searchId === props.searchAddedId
        )
        await nextTick()
        await scrollToAddedSearch(index)
      }
    }, { immediate: true })

    watch(() => localState.filters, (val) => {
      console.log(localState.filters, "from watch", val)
    }, {deep: true})

    return {
      ...toRefs(localState),
      displayDate,
      displaySearchValue,
      displayType,
      displayMhrType,
      downloadPDF,
      generateReport,
      getTooltipTxtPdf,
      isPDFAvailable,
      isPprSearch,
      isSearchOwner,
      refreshRow,
      retrySearch,
      dateSortHandler,
      goToPay,
      returnSearchSelection,
      updateDateRange,
      FilterTypes,
      clearFilters
    }
  }
})
</script>

<template>
  <v-container
    class="main-results-div pa-0 bg-white"
    role="region"
  >
    <v-row
      no-gutters
    >
      <v-col cols="12">
        <RangeDatePicker
          v-if="showDatePicker"
          id="ranged-date-picker"
          ref="datePicker"
          @submit="updateDateRange($event)"
        />

        <v-table
          v-if="searchHistory"
          id="search-history-table"
          height="25rem"
          fixed-header
        >
          <template #default>
            <thead>
            <tr>
              <th
                v-for="header in headers"
                :key="header.value"
                class="px-1 py-1 table-header"
                :class="header.class"
              >
              <template v-if="header.value==='matches'">
                <v-row>
                  <v-col>{{header.text}}</v-col>
                </v-row>
                <v-row>
                  <v-col
                    v-for="subHeader in header.subHeaders"
                    :key="subHeader"
                    class="font-light"
                  >
                    {{ subHeader }}
                  </v-col>
                </v-row>
              </template>
              <template v-else>
                    {{ header.text }}
              </template>
                <!-- Date Sort Icon/Button -->
                <SortingIcon
                  v-if="header.sortable"
                  :sort-asc="sortAsc"
                  @sort-event="dateSortHandler(searchHistory, 'searchDateTime', $event)"
                />
              </th>
            </tr>
            <tr>
              <th
                v-for="header in headers"
                :key="header.value"
                class="px-1 py-1 table-header"
                :class="header.class"
              >
                <v-row no-gutters class="py-2">
                  <v-col>
                    <v-tooltip
                      text="tooltip text hahaha"
                      location="bottom"
                    >
                      <template v-slot:activator="{props}">
                        <v-text-field
                          v-if="header.filter && header.filter.type === FilterTypes.TEXT_FIELD"
                          v-bind="props"
                          v-model="filters[header.value]"
                          variant="filled"
                          color="primary"
                          single-line
                          :hide-details="true"
                          type="text"
                          :label="header.filter.text"
                          density="compact"
                          clearable
                          persistent-clear
                        />
                        <SearchBarList
                          v-if="header.filter && header.filter.type === FilterTypes.SELECT"
                          v-bind="props"
                          :is-table-filter="true"
                          :default-selected-search-type="selectedSearchType"
                          :filter-label="header.filter.text"
                          @selected="returnSearchSelection($event)"
                        />
                        <v-text-field
                          v-if="header.filter && header.filter.type === FilterTypes.DATE_PICKER"
                          v-bind="props"
                          v-model="dateTxt"
                          append-inner-icon="mdi-calendar"
                          density="compact"
                          clearable
                          variant="filled"
                          color="primary"
                          hide-details
                          :label="header.filter.text"
                          single-line
                          persistent-clear
                          @click="showDatePicker = true"
                        />  
                      </template>
                    </v-tooltip>
                    <v-btn
                      v-if="header.value==='pdf'"
                      class="registration-action ma-0"
                      color="primary"
                      :ripple="false"
                      variant="outlined"
                      @click="clearFilters()"
                    >
                      Clear Filters
                      <v-icon size="18" class="pl-3 pt-1">
                        mdi-close
                      </v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </th>
            </tr>
            </thead>

            <tbody v-if="searchHistory.length > 0">
            <tr
              v-for="(item, index) in searchHistory"
              :key="item.searchId"
              :class="{ 'added-search-effect': ((searchAdded && index === 0) || (item.searchId === searchAddedId)) }"
            >
            <template
              v-for="header in headers"
              :key="header"
            >
              <!-- Search Value -->
              <td v-if="header.value==='searchQuery.criteria.value'">
                <v-icon
                  class="pl-4 pr-2 mt-n1"
                  color="#212529"
                  aria-hidden="false"
                  :aria-label="
                      headers[0].text + ',' + (isPprSearch(item) ? 'PPR' : 'MHR') + displaySearchValue(item.searchQuery)
                    "
                >
                  {{ isPprSearch(item) ? 'mdi-account-details' : 'mdi-home' }}
                </v-icon>
                <span class="pl-2" aria-hidden="true">{{ displaySearchValue(item.searchQuery) }}</span>
              </td>
              <!-- Search Type or Category -->
              <td v-if="header.value==='typeAndRegistry'">
                <v-row>
                  <AriaLabel :aria-text="header.text" />
                <strong>
                  <span v-if="isPprSearch(item)">Personal Property</span>
                  <span v-else>Manufactured Homes</span>
                </strong>
                </v-row>
                <v-row>
                  <AriaLabel :aria-text="header.text" />
                  {{ isPprSearch(item) ? displayType(item.searchQuery.type) : displayMhrType(item.searchQuery.type) }}
                </v-row>
              </td>
              <td v-if="header.value==='searchQuery.clientReferenceId'">
                <AriaLabel :aria-text="header.text" />
                {{ item.searchQuery.clientReferenceId || '-' }}
              </td>
              <!-- Date/Time (Pacific time) -->
              <td v-if="header.value==='searchDateTime'">
                <AriaLabel :aria-text="header.text" />
                <span v-if="!item.inProgress || isSearchOwner(item)">
                    {{ displayDate(item.searchDateTime) }}
                </span>
                <span v-else>Pending</span>
              </td>
              <td v-if="header.value==='username'">
                <AriaLabel :aria-text="header.text" />
                {{ item.username }}
              </td>
              <td
                v-if="header.value==='matches'"
                class="matches"
              >
              <v-row>
                <v-col
                  class="text-center"
                >
                  <AriaLabel :aria-text="header.text" />
                  <span v-if="!item.inProgress || isSearchOwner(item)">
                    {{ item.totalResultsSize }}
                  </span>
                  <span
                    v-else
                    role="img"
                    aria-label="None"
                  >-</span>
                </v-col>
                <v-col class="text-center">
                  <AriaLabel :aria-text="header.text" />
                  <span v-if="(!item.inProgress || isSearchOwner(item)) && item.exactResultsSize >= 0">
                    {{ item.exactResultsSize }}
                  </span>
                  <span
                    v-else
                    role="img"
                    aria-label="None"
                  >-</span>
                </v-col>
                <v-col class="text-center">
                  <AriaLabel :aria-text="header.text" />
                  <span v-if="!item.inProgress || isSearchOwner(item)">
                    {{ item.selectedResultsSize }}
                  </span>
                  <span
                    v-else
                    role="img"
                    aria-label="None"
                  >-</span>
                </v-col>
            </v-row>
            </td>
              <td
              v-if="header.value==='pdf'"
              class="text-center"
              >
                <v-btn
                  v-if="item.paymentPending"
                  class="resume-pay-btn px-6"
                  color="primary"
                  aria-label="Resume Pay Button"
                  variant="outlined"
                  @click="goToPay(
                    item.invoiceId,
                    isPprSearch(item) ? item.searchId : null,
                    !isPprSearch(item) ? `search-${item.searchId}` : null
                  )"
                >
                  <span class="fs-14 leading-none">Resume<br>Payment</span>
                </v-btn>
                <v-btn
                  v-else-if="!item.isPending &&
                      !item.inProgress && isPDFAvailable(item)"
                  :id="`pdf-btn-${item.searchId}`"
                  class="pdf-btn px-0 mt-n3"
                  variant="plain"
                  :ripple="false"
                  :loading="item.loadingPDF"
                  aria-label="Download PDF"
                  @click="downloadPDF(item)"
                >
                  <img src="@/assets/svgs/pdf-icon-blue.svg">
                  <span class="pl-1 text-blue-500">PDF</span>
                </v-btn>
                <v-tooltip
                  v-else
                  class="pa-2"
                  content-class="top-tooltip"
                  location="top"
                  transition="fade-transition"
                >
                  <template #activator="{ props }">
                    <v-btn
                      v-if="!item.inProgress"
                      variant="plain"
                      color="primary"
                      :ripple="false"
                      :loading="item.loadingPDF"
                      aria-label="Refresh Download Button"
                      @click="refreshRow(item)"
                    >
                      <v-icon
                        color="primary"
                        size="20"
                        v-bind="props"
                      >
                        mdi-information-outline
                      </v-icon>
                    </v-btn>
                    <v-btn
                      v-else-if="isSearchOwner(item)"
                      color="primary"
                      variant="plain"
                      :ripple="false"
                      :loading="item.loadingPDF"
                      aria-label="Generate Report Button"
                      @click="generateReport(item)"
                    >
                      <v-icon
                        color="primary"
                        size="20"
                        v-bind="props"
                      >
                        mdi-information-outline
                      </v-icon>
                    </v-btn>
                    <v-icon
                      v-else
                      color="primary"
                      size="20"
                      v-bind="props"
                      tabindex="0"
                      role="img"
                      aria-hidden="false"
                      :aria-label="getTooltipTxtPdf(item)"
                    >
                      mdi-information-outline
                    </v-icon>
                  </template>
                  <div class="pt-2 pb-2">
                    <span v-html="getTooltipTxtPdf(item)" />
                  </div>
                </v-tooltip>
              </td>
            </template>
            </tr>
            </tbody>
            <tbody v-else>
            <tr>
              <td
                :colspan="headers.length"
                style="text-align: center"
              >
                <div
                  v-if="!isSearchHistory"
                  id="no-history-info"
                  class="pt-4 pb-3"
                >
                  We were unable to retrieve your search history. Please try
                  again later. If this issue persists, please contact us.
                  <br><br>
                  <v-btn
                    id="retry-search-history"
                    variant="plain"
                    color="primary"
                    :ripple="false"
                    aria-label="Retry Button"
                    @click="retrySearch()"
                  >
                    Retry <v-icon>mdi-refresh</v-icon>
                  </v-btn>
                  <error-contact class="search-contact-container pt-6" />
                </div>
                <div
                  v-else
                  id="no-history-info"
                >
                  Your search history will display here
                </div>
              </td>
            </tr>
            </tbody>
          </template>
        </v-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.table-header:first-child {
  padding-left: 24px!important;
}

.added-search-effect {
  background-color: $greenSelected;
  font-weight: bold;
}
.main-results-div {
  width: 100%;
}
.search-contact-container {
  width: 350px;
  font-size: 0.875rem;
}
:deep(#search-history-table) {
  // th {
  //   height: 5rem;
  // }
  :deep(.v-input__control)   {
    height: 45px;
  }
  td {
    text-overflow: initial;
    white-space: initial;
    vertical-align: top;
    padding-top: 20px !important;
    padding-bottom: 20px !important;
    word-wrap: break-word;
  }
}
.dontRead {
  speak: none!important;
}
.aria-label-only {
  display: none
}
.v-col {
  padding: 0;
}
.matches {
  background-color: $ghostWhite !important;
  padding: 0;
}
</style>
