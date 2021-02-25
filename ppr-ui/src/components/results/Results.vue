<template>
  <div class="main-results-div">
    <v-row v-if="searched" no-gutters class="pa-3 result-info">
      <v-col v-if="totalResultsLength !== 0">
        {{ totalResultsLength }} registrations found |
        <b>{{ exactMatchesLength }} exact matches</b> |
        <b>selected: {{ selectedLength }}</b>
      </v-col>
      <v-col v-else>
        {{ totalResultsLength }} registrations found
      </v-col>
    </v-row>
    <v-row v-if="totalResultsLength !== 0" no-gutters>
      <v-container fluid no-gutters>
        <v-row no-gutters>
          <v-col class="auto">
            <v-data-table v-if="results"
                          class="results-table"
                          height="20rem"
                          hide-default-footer
                          fixed
                          fixed-header
                          :headers="headers"
                          :items="results"
                          :item-class="getClass"
                          item-key="vehicleCollateral.serialNumber"
                          multi-sort
                          show-select
                          return-object
                          v-model="selected">
            </v-data-table>
          </v-col>
        </v-row>
      </v-container>
    </v-row>
    <v-row v-else no-gutters justify="center" class="pa-3">
      <div class="no-results-info white">
        <v-row no-gutters justify="center" class="pt-10">
          No registrations were found for the Serial Number:
        </v-row>
        <v-row no-gutters justify="center">
          <b>{{ searchValue }}</b>
        </v-row>
      </div>
    </v-row>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'

import { tableHeaders } from '@/resources'
import { SearchResponseIF, SearchResultIF, TableHeadersIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { MatchTypes } from '@/enums'

export default defineComponent({
  props: {
    defaultHeaders: {
      type: Array as () => TableHeadersIF
    },
    defaultResults: {
      type: Array as () => Array<SearchResultIF>
    },
    defaultSelected: {
      type: Array as () => Array<SearchResultIF>
    },
    resultsGetter: {
      type: String,
      default: 'getSearchResults'
    }
  },
  setup (props) {
    const { getSearchResults } = useGetters<any>([props.resultsGetter])
    const localState = reactive({
      searched: false,
      searchValue: '',
      selected: props.defaultSelected,
      headers: props.defaultHeaders,
      results: props.defaultResults,
      exactMatchesLength: 0,
      totalResultsLength: 0,
      selectedLength: computed((): number => {
        return localState.selected?.length | 0
      }),
      searchResponse: computed((): SearchResponseIF => {
        const resp = getSearchResults.value
        if (resp) {
          localState.searchValue = resp.searchQuery.criteria.value
          localState.searched = true
          localState.headers = tableHeaders[resp.searchQuery.type]
          localState.results = resp.results
          localState.totalResultsLength = resp.totalResultsSize
          return resp
        }
        return {
          searchId: '',
          maxResultsSize: NaN,
          totalResultsSize: NaN,
          returnedResultsSize: NaN,
          searchQuery: {
            type: '',
            criteria: {}
          },
          results: []
        }
      })
    })
    const getClass = (item:SearchResultIF):string => {
      if (item.matchType === MatchTypes.EXACT) {
        return 'exact-match'
      }
      return 'normal-match'
    }
    watch(() => localState.results, (results) => {
      const selectedExactMatches = []
      let count = 0
      let x:any
      for (x in results) {
        if (results[x].matchType === MatchTypes.EXACT) {
          count += 1
          selectedExactMatches.push(results[x])
        }
      }
      localState.exactMatchesLength = count
      localState.selected = selectedExactMatches
    })

    return {
      ...toRefs(localState),
      getClass
    }
  }
})
</script>

<style lang="scss">
@import '@/assets/styles/theme.scss';
#search-btn {
  width: 8rem;
}
#search-btn-info {
  color: $gray8;
  font-size: 0.725rem;
}
.close-popup-btn {
  background-color: transparent !important;
}
.exact-match td {
  color: $gray9 !important;
  font-weight: bold;
}
.normal-match td {
  color: $gray9 !important;
}
.main-results-div {
  width: 100%;
}
.result-info {
  color: $gray9 !important;
  font-size: 0.825rem;
}
.no-results-info {
  color: $gray9 !important;
  font-size: 0.825rem;
  width: 100%;
  height: 8rem;
}
// .result-header {
//   font-size: 0.825rem !important;
//   color: $gray7 !important;
// }
// .results-table {
//   height: 500px;
// }
.v-select-list {
  padding-left: 1rem;
  padding-right: 1rem;
}
</style>
