<template>
  <v-container :class="[$style['main-results-div'], 'pa-0', 'white']">
    <v-row v-if="historyLength !== 0" no-gutters class="pt-4">
      <v-col cols="12">
        <v-data-table v-if="searchHistory"
                      id="search-history-table"
                      hide-default-footer
                      fixed
                      fixed-header
                      :headers="headers"
                      height="20rem"
                      :items="searchHistory"
                      item-key="searchId"
                      :items-per-page="-1"
                      sort-by="searchDateTime"
                      sort-desc
                      return-object>
          <template v-slot:[`item.searchQuery.criteria.value`]="{ item }">
            {{ displaySearchValue(item.searchQuery) }}
          </template>
          <template v-slot:[`item.UISearchType`]="{ item }">
            {{ displayType(item.searchQuery.type) }}
          </template>
          <template v-slot:[`item.searchDateTime`]="{ item }">
            {{ displayDate(item.searchDateTime) }}
          </template>
          <template v-slot:[`item.pdf`]="{ item }">
            <v-btn
              :id="`pdf-btn-${item.searchId}`"
              class="pdf-btn px-0 mt-n3"
              depressed
              :loading="item.searchId === loadingPDF"
              @click="downloadPDF(item.searchId)"
            >
              <img src="@/assets/svgs/custom-pdf-icon.svg">
              <span class="pl-1">PDF</span>
            </v-btn>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row v-else no-gutters justify="center" id="no-history-info" :class="[$style['no-results-info'], 'pa-5']">
      <v-col cols="auto">
        Your search history will display here
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs, useCssModule } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { SearchCriteriaIF, SearchResponseIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { searchHistroyTableHeaders, SearchTypes } from '@/resources'
import { convertDate, searchPDF } from '@/utils'
import { StatusCodes } from 'http-status-codes'

export default defineComponent({
  setup (props, { emit }) {
    const style = useCssModule()
    const { getSearchHistory } = useGetters<any>(['getSearchHistory'])
    const localState = reactive({
      loadingPDF: '',
      headers: searchHistroyTableHeaders,
      historyLength: computed((): number => {
        return localState.searchHistory?.length || 0
      }),
      searchHistory: computed((): Array<SearchResponseIF> => {
        let searchHistory = null
        searchHistory = getSearchHistory.value
        return searchHistory
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
    const downloadPDF = async (searchId: string): Promise<any> => {
      localState.loadingPDF = searchId
      const pdf = await searchPDF(searchId)
      if (!pdf || pdf?.error) {
        emit('error', { statusCode: StatusCodes.NOT_FOUND })
      } else {
        /* solution from https://github.com/axios/axios/issues/1392 */

        // it is necessary to create a new blob object with mime-type explicitly set
        // otherwise only Chrome works like it should
        const blob = new Blob([pdf], { type: 'application/pdf' })

        // IE doesn't allow using a blob object directly as link href
        // instead it is necessary to use msSaveOrOpenBlob
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
          window.navigator.msSaveOrOpenBlob(blob, searchId)
        } else {
          // for other browsers, create a link pointing to the ObjectURL containing the blob
          const url = window.URL.createObjectURL(blob)
          const a = window.document.createElement('a')
          window.document.body.appendChild(a)
          a.setAttribute('style', 'display: none')
          a.href = url
          a.download = searchId
          a.click()
          window.URL.revokeObjectURL(url)
          a.remove()
        }
      }
      localState.loadingPDF = ''
    }
    return {
      ...toRefs(localState),
      displayDate,
      displaySearchValue,
      displayType,
      downloadPDF,
      style
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.main-results-div {
  width: 100%;
}
.no-history-info {
  color: $gray9 !important;
  font-size: 0.825rem;
}
.pdf-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  justify-content: start;
}
.pdf-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.pdf-btn-text {
  text-decoration: underline;
}
</style>
