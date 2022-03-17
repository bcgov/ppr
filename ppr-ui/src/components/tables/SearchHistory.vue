<template>
  <v-container class="main-results-div pa-0 white">
    <v-row no-gutters class="pt-4">
      <v-col cols="12">
        <v-data-table
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
              <tr v-for="item in items" :key="item.name">
                <td>
                  {{ displaySearchValue(item.searchQuery) }}
                </td>
                <td>
                  {{ displayType(item.searchQuery.type) }}
                </td>
                <td v-if="isStaff">
                  {{ item.username }}
                </td>
                <td v-else>
                  {{ item.searchQuery.clientReferenceId }}
                </td>
                <td>
                  {{ displayDate(item.searchDateTime) }}
                </td>
                <td>
                  {{ item.totalResultsSize }}
                </td>
                <td>
                  {{ item.exactResultsSize }}
                </td>
                <td>
                  {{ item.selectedResultsSize }}
                </td>
                <td>
                  <v-btn
                    v-if="item.searchId !== 'PENDING'"
                    :id="`pdf-btn-${item.searchId}`"
                    class="pdf-btn px-0 mt-n3"
                    depressed
                    :loading="item.searchId === loadingPDF"
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
                      <v-icon color="primary" v-bind="attrs" v-on="on"
                        >mdi-information-outline</v-icon
                      >
                    </template>
                    <div class="pt-2 pb-2">
                      <span v-html="tooltipTxtPdf"></span>
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
import { searchHistoryTableHeaders, searchHistoryTableHeadersStaff, SearchTypes } from '@/resources'
import { convertDate, searchPDF } from '@/utils'
import { ErrorContact } from '../common'

export default defineComponent({
  components: {
    ErrorContact
  },
  setup (props, { emit }) {
    const { getSearchHistory, isRoleStaff } = useGetters<any>(['getSearchHistory', 'isRoleStaff'])
    const tooltipTxtPdf =
      'This document PDF is still being generated. Click the ' +
        '<i class="v-icon notranslate mdi mdi-information-outline" style="font-size:18px; margin-bottom:4px;"></i>' +
        ' icon to see if your PDF is ready to download. <br>' +
        'Note: Large documents may take up to 20 minutes to generate.'
    const localState = reactive({
      loadingPDF: '',
      headers: computed((): Array<any> => {
        if (localState.isStaff) {
          return searchHistoryTableHeadersStaff
        }
        return searchHistoryTableHeaders
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
          let searchHistory = null
          searchHistory = getSearchHistory.value
          if (!searchHistory) {
            return []
          }
          return searchHistory
        }
      ),
      isSearchHistory: computed((): boolean => {
        if (getSearchHistory.value) {
          return true
        }
        return false
      })
    })
    const displayDate = (searchDate: string): string => {
      const date = new Date(searchDate)
      return convertDate(date, true, false)
    }
    const displaySearchValue = (query: SearchCriteriaIF): string => {
      const first = query?.criteria?.debtorName?.first
      const second = query?.criteria?.debtorName?.second
      const last = query?.criteria?.debtorName?.last
      const business = query?.criteria?.debtorName?.business
      if (first && last) {
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
    const downloadPDF = async (item: SearchResponseIF): Promise<any> => {
      localState.loadingPDF = item.searchId
      const pdf = await searchPDF(item.searchId)
      if (pdf.error) {
        emit('error', pdf.error)
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
          const searchValue = displaySearchValue(item.searchQuery).replace(/ /g, '_')
          a.download = today.toISOString().slice(0, 10) + '_BCPPR_Search_Result_' +
            searchValue + '_' + item.searchId
          a.click()
          window.URL.revokeObjectURL(url)
          a.remove()
        }
      }
      localState.loadingPDF = ''
    }
    const retrySearch = (): void => {
      emit('retry')
    }

    return {
      ...toRefs(localState),
      displayDate,
      displaySearchValue,
      displayType,
      downloadPDF,
      retrySearch,
      tooltipTxtPdf
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
</style>
