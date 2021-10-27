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
              <svg
                width="19px"
                height="19px"
                viewBox="0 0 19 19"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                xmlns:xlink="http://www.w3.org/1999/xlink"
              >
                <title>new pdf icon copy 4</title>
                <defs>
                  <filter color-interpolation-filters="auto" id="filter-1">
                    <feColorMatrix
                      in="SourceGraphic"
                      type="matrix"
                      values="0 0 0 0 1.000000 0 0 0 0 1.000000 0 0 0 0 1.000000 0 0 0 1.000000 0"
                    />
                  </filter>
                </defs>
                <g id="Symbols" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                  <g id="My-Searches" transform="translate(-1105.000000, -368.000000)">
                    <g id="new-pdf-icon-copy-5" transform="translate(1105.000000, 368.000000)">
                      <g id="file-document-outline-(1)" fill="#1669BB" fill-rule="nonzero">
                        <path
                          d="M3.63984674,1.9 L3.63984674,17.1 C3.63984674,18.149341 4.47095034,19 5.49616858,
                            19 L16.6340996,19 C17.6593179,19 18.4904215,18.149341 18.4904215,17.1 L18.4904215,
                            5.7 L12.9214559,0 L5.49616858,0 C4.47095034,0 3.63984674,0.850658975 3.63984674,
                            1.9 Z M11.993295,1.4952381 L11.993295,5.2452381 C11.993295,5.52138047 12.2171526,
                            5.7452381 12.493295,5.7452381 L17.0388615,5.7452381 C17.3150039,
                            5.7452381 17.5388615,5.96909572 17.5388615,6.2452381 L17.5388615,
                            17.5047619 C17.5388615,17.7809043 17.3150039,18.0047619 17.0388615,
                            18.0047619 L5.09140668,18.0047619 C4.8152643,18.0047619 4.59140668,
                            17.7809043 4.59140668,17.5047619 L4.59140668,1.4952381 C4.59140668,
                            1.21909572 4.8152643,0.995238095 5.09140668,0.995238095 L11.493295,
                            0.995238095 C11.7694374,0.995238095 11.993295,1.21909572 11.993295,
                            1.4952381 Z M0,9.04705882 L0,13.7529412 C4.47140469e-16,14.3052259 0.44771525,
                            14.7529412 1,14.7529412 L13.7777778,14.7529412 C14.3300625,14.7529412 14.7777778,
                            14.3052259 14.7777778,13.7529412 L14.7777778,9.04705882 C14.7777778,
                            8.49477407 14.3300625,8.04705882 13.7777778,8.04705882 L1,8.04705882 C0.44771525,
                            8.04705882 -1.78657678e-16,8.49477407 0,9.04705882 Z"
                          id="Shape"
                        />
                      </g>
                      <g id="PDF" transform="translate(1.585568, 9.144000)" filter="url(#filter-1)">
                        <g>
                          <path
                            d="M1.00455182,
                              4.75 L1.00455182,3.06022409 L1.43697479,3.06022409 C2.82072829,3.06022409 3.2797619,
                              2.32177871 3.2797619,1.48354342 C3.2797619,0.558823529 2.74089636,
                              0 1.51680672,0 L0,0 L0,4.75 L1.00455182,4.75 Z M1.33718487,2.23529412 L1.00455182,
                              2.23529412 L1.00455182,0.824929972 L1.46358543,0.824929972 C1.99579832,
                              0.824929972 2.26190476,1.05777311 2.26190476,1.51680672 C2.26190476,
                              2.02240896 1.90266106,2.23529412 1.33718487,2.23529412 Z M5.52170868,4.75 C7.15161064,
                              4.75 8.1162465,3.93172269 8.1162465,2.32843137 C8.1162465,0.81162465 7.15161064,
                              0 5.66806723,0 L4.17787115,0 L4.17787115,4.75 L5.52170868,4.75 Z M5.61484594,
                              3.91841737 L5.18242297,3.91841737 L5.18242297,0.824929972 L5.72128852,
                              0.824929972 C6.59943978,0.824929972 7.07177871,1.31057423 7.07177871,
                              2.35504202 C7.07177871,3.3995098 6.58613445,3.91841737 5.61484594,
                              3.91841737 Z M10.0920868,4.75 L10.0920868,2.87394958 L11.7020308,2.87394958 L11.7020308,
                              2.04901961 L10.0920868,2.04901961 L10.0920868,0.824929972 L11.8217787,
                              0.824929972 L11.8217787,0 L9.10084034,0 L9.10084034,4.75 L10.0920868,4.75 Z"
                            fill="#1669BB"
                            fill-rule="nonzero"
                          />
                        </g>
                      </g>
                    </g>
                  </g>
                </g>
              </svg>
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
