<template>
  <v-container class="main-results-div pa-0 white">
    <v-row no-gutters class="pt-4">
      <v-col cols="12">
        <v-data-table
          v-if="searchHistory"
          id="search-history-table"
          hide-default-footer
          fixed
          fixed-header
          :headers="headers"
          height="20rem"
          :items="searchHistory"
          item-key="searchId"
          :items-per-page="-1"
          mobile-breakpoint="0"
          sort-by="searchDateTime"
          sort-desc
          return-object
        >
          <template v-slot:body="{ items, headers }">
            <tbody v-if="items.length > 0">
              <tr v-for="item in items" :key="`${item.name}: ${items.indexOf(item) + keyValue}`">
                <td>
                  <v-row no-gutters>
                    <v-col cols="2">
                      <v-icon v-if="isPprSearch(item)" class="pr-2" color="primary">mdi-car</v-icon>
                      <v-icon v-else class="pr-2" color="success">mdi-home</v-icon>
                    </v-col>
                    <v-col>
                      {{ displaySearchValue(item.searchQuery) }}
                    </v-col>
                  </v-row>
                </td>
                <td v-if="isPprSearch(item)">
                  {{ displayType(item.searchQuery.type) }}
                </td>
                <td v-else>
                  {{ displayMhrType(item.searchQuery.type) }}
                </td>
                <td>
                  <span v-if="isPprSearch(item)">Personal Property</span>
                  <span v-else>Manufactured Homes</span>
                </td>
                <td>
                  <span v-if="!item.inProgress || isSearchOwner(item)">
                    {{ displayDate(item.searchDateTime) }}
                  </span>
                  <span v-else>Pending</span>
                </td>
                <td v-if="isStaff">
                  {{ item.username }}
                </td>
                <td v-else>
                  {{ item.searchQuery.clientReferenceId || '-' }}
                </td>
                <td>
                  <span v-if="!item.inProgress || isSearchOwner(item)">
                    {{ item.totalResultsSize }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td>
                  <span v-if="(!item.inProgress || isSearchOwner(item)) && item.exactResultsSize >= 0">
                    {{ item.exactResultsSize }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td>
                  <span v-if="!item.inProgress || isSearchOwner(item)">
                    {{ item.selectedResultsSize }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td>
                  <v-btn
                    v-if="!item.isPending &&
                    !item.inProgress && isPDFAvailable(item) && isMhrReportReady(item)"
                    :id="`pdf-btn-${item.searchId}`"
                    class="pdf-btn px-0 mt-n3"
                    depressed
                    :loading="item.loadingPDF"
                    @click="downloadPDF(item)"
                  >
                    <img src="@/assets/svgs/pdf-icon-blue.svg" />
                    <span class="pl-1">PDF</span>
                  </v-btn>
                  <v-tooltip
                    v-else
                    class="pa-2"
                    content-class="top-tooltip"
                    nudge-right="2"
                    top
                    transition="fade-transition"
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        v-if="!item.inProgress"
                        color="primary"
                        :loading="item.loadingPDF"
                        @click="refreshRow(item)"
                      >
                        <v-icon color="primary" v-bind="attrs" v-on="on">
                          mdi-information-outline
                        </v-icon>
                      </v-btn>
                      <v-btn
                        v-else-if="isSearchOwner(item)"
                        color="primary"
                        icon
                        :loading="item.loadingPDF"
                        @click="generateReport(item)"
                      >
                        <v-icon color="primary" v-bind="attrs" v-on="on">
                          mdi-information-outline
                        </v-icon>
                      </v-btn>
                      <v-icon v-else color="primary" v-bind="attrs" v-on="on">
                        mdi-information-outline
                      </v-icon>
                    </template>
                    <div class="pt-2 pb-2">
                      <span v-html="getTooltipTxtPdf(item)"></span>
                    </div>
                  </v-tooltip>
                </td>
              </tr>
            </tbody>
            <tbody v-else>
              <tr>
                <td :colspan="headers.length" style="text-align: center">
                  <div id="no-history-info" v-if="!isSearchHistory" class="pt-4 pb-3">
                    We were unable to retrieve your search history. Please try
                    again later. If this issue persists, please contact us.
                    <br /><br />
                    <v-btn
                      id="retry-search-history"
                      outlined
                      color="primary"
                      @click="retrySearch()"
                    >
                      Retry <v-icon>mdi-refresh</v-icon>
                    </v-btn>
                    <error-contact class="search-contact-container pt-6" />
                  </div>
                  <div id="no-history-info" v-else>
                    Your search history will display here
                  </div>
                </td>
              </tr>
            </tbody>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { SearchCriteriaIF, SearchResponseIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { MHRSearchTypes, searchHistoryTableHeaders, searchHistoryTableHeadersStaff, SearchTypes } from '@/resources'
import { convertDate, searchPDF, submitSelected, successfulPPRResponses, searchMhrPDF, delayActions } from '@/utils'
import { ErrorContact } from '../common'
import { useSearch } from '@/composables/useSearch'
import { cloneDeep } from 'lodash' // eslint-disable-line
import _ from 'lodash' // eslint-disable-line
import { ErrorCategories } from '@/enums'

export default defineComponent({
  components: {
    ErrorContact
  },
  setup (props, { emit }) {
    const {
      getSearchHistory,
      getUserUsername,
      isRoleStaff,
      hasPprRole,
      hasMhrRole
    } = useGetters<any>([
      'getSearchHistory',
      'getUserUsername',
      'isRoleStaff',
      'hasPprRole',
      'hasMhrRole'
    ])
    const localState = reactive({
      keyValue: 0,
      headers: computed((): Array<any> => {
        const tableHeaders = cloneDeep(searchHistoryTableHeaders)
        if (localState.isStaff) {
          return searchHistoryTableHeadersStaff
        }
        return tableHeaders
      }),
      hasBothRoles: computed((): boolean => {
        return hasPprRole.value && hasMhrRole.value
      }),
      isStaff: computed((): boolean => {
        if (isRoleStaff.value) {
          return true
        }
        return false
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
        if (getSearchHistory.value) {
          return true
        }
        return false
      })
    })
    const { mapMhrSearchType } = useSearch()
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
        if (pdf.error.statusCode === 500) {
          // emit and show modal for a server error
          emit('error', pdf.error)
        } else if (pdf.error.statusCode === 400 && pdf.error.category === ErrorCategories.REPORT_GENERATION) {
          // log to console if pdf report is still pending
          console.log('PDF Report is not ready yet')
        }
        item.loadingPDF = false
        return false
      } else if (pdf && item.isPending) {
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
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
          window.navigator.msSaveOrOpenBlob(blob, item.searchId)
        } else {
          // for other browsers, create a link pointing to the ObjectURL containing the blob
          const url = window.URL.createObjectURL(blob)
          const a = window.document.createElement('a')
          window.document.body.appendChild(a)
          a.setAttribute('style', 'display: none')
          a.href = url
          // Format: [Date (in YYYY-MM-DD format)] BCPPR Search Result - [Search Criteria] Search ID
          // Example: 2022-01-03 BCPPR BO Search Result - Telus Communications Inc. Search ID
          const today = new Date()
          const searchValue = displaySearchValue(item.searchQuery).replace(/ /g, '_').split('.').join('')
          a.download = today.toISOString().slice(0, 10) + '_BCPPR_Search_Result_' +
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
    const generateReport = _.throttle(async (item: SearchResponseIF): Promise<void> => {
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
    }, 250, { trailing: false })
    const getTooltipTxtPdf = (item: SearchResponseIF): string => {
      if (item.inProgress) {
        if (isSearchOwner(item)) {
          return '<p class="ma-0">The document PDF has not been generated. Click the ' +
            '<i class="v-icon notranslate mdi mdi-information-outline" ' +
            'style="font-size:18px; margin-bottom:4px;"></i>' +
            ' icon to generate your PDF.</p>' +
            '<p class="ma-0 mt-2">Note: Large documents may take up to 20 minutes to generate.</p>'
        }
        return 'This search is in progress by another user.'
      }
      if (!isPDFAvailable(item)) {
        return 'This document PDF is no longer available.'
      }
      return '<p class="ma-0">This document PDF is still being generated. Click the ' +
        '<i class="v-icon notranslate mdi mdi-information-outline" style="font-size:18px; margin-bottom:4px;"></i> ' +
        'icon to see if your PDF is ready to download. </p>' +
        '<p class="ma-0 mt-2">Note: Large documents may take up to 20 minutes to generate.</p>'
    }
    const isPDFAvailable = (item: SearchResponseIF): Boolean => {
      const now = new Date()
      const nowDate = new Date(now.toDateString())
      const searchDatetime = new Date(item.searchDateTime)
      const searchDate = new Date(searchDatetime.toDateString())
      const diffTime = nowDate.getTime() - searchDate.getTime()
      const diffDays = diffTime / (1000 * 3600 * 24)
      return diffDays < 15
    }
    const isSearchOwner = (item: SearchResponseIF): Boolean => {
      return getUserUsername.value === item?.userId
    }
    const retrySearch = (): void => {
      emit('retry')
    }
    const isPprSearch = (item: SearchResponseIF): boolean => {
      return item.exactResultsSize >= 0
    }
    const isMhrReportReady = (item: SearchResponseIF): boolean => {
      if (isPprSearch(item)) return true
      else {
        // Give the api 30s buffer to finish report generation
        const now = new Date()
        const searchDatetime = new Date(item.searchDateTime)
        const diffTime = now.getTime() - searchDatetime.getTime()
        return diffTime > 30000
      }
    }
    const refreshRow = async (item): Promise<void> => {
      const pdf = await downloadPDF(item)
      if (pdf) {
        // Update unique key value of table row to refresh singular component
        localState.keyValue += 1
      }
    }
    return {
      ...toRefs(localState),
      displayDate,
      displaySearchValue,
      displayType,
      displayMhrType,
      downloadPDF,
      generateReport,
      getTooltipTxtPdf,
      isMhrReportReady,
      isPDFAvailable,
      isPprSearch,
      isSearchOwner,
      refreshRow,
      retrySearch
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.main-results-div {
  width: 100%;
}
.search-contact-container {
  width: 350px;
  font-size: 0.875rem;
}
::v-deep {
  td .v-icon {
    font-size: 20px;
  }
  .v-btn--icon.v-size--default {
    height: 24px;
    width: 24px;
  }
  .v-btn.v-btn--depressed.v-btn--loading.pdf-btn {
    height: 24px;
    min-width: 24px;
    width: 24px;
  }
}
</style>
