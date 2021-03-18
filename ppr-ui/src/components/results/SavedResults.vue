<template>
  <v-container :class="[$style['main-results-div'], 'pa-0', 'white']">
    <v-row v-if="searched && resultsType === 'searched'" no-gutters :class="[$style['result-info'], 'pl-5', 'pt-8']">
      <v-row v-if="totalResultsLength !== 0" no-gutters>
        <v-col>
          <v-row no-gutters>
            <span :class="[$style['divider'], 'pr-3']"><b>{{ totalResultsLength }}</b> registrations found</span>
            <span class="pl-3"><b>{{ exactMatchesLength }}</b> exact matches </span>
          </v-row>
          <v-row no-gutters class="pt-2">
            <span> Added to search results report: <b>{{ selectedLength }}</b></span>
          </v-row>
        </v-col>
      </v-row>
      <v-row v-else>
          <b>{{ totalResultsLength }}</b> registrations found
      </v-row>
    </v-row>
    <v-row v-if="totalResultsLength !== 0" no-gutters class="pt-4">
      <v-col cols="12">
        <v-data-table v-if="results"
                      id="results-table"
                      :class="$style['results-table']"
                      height="20rem"
                      hide-default-footer
                      fixed
                      fixed-header
                      :headers="headers"
                      :items="results"
                      :item-class="getClass"
                      item-key="baseRegistrationNumber"
                      multi-sort
                      return-object
                      :show-select="resultsType === 'searched'"
                      v-model="selected">
          <template v-if="resultsType === 'searched'" v-slot:[`item.makeModel`]="{ item }">
            {{ item.vehicleCollateral.make }} {{ item.vehicleCollateral.model }}
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row v-else no-gutters id="search-no-results-info" justify="center" :class="[$style['no-results-info'], 'pt-3']">
      <v-col cols="auto">
        <v-row no-gutters justify="center" :class="[$style['no-results-title'], 'pt-10']">
          <b>Nil Result</b>
        </v-row>
        <v-row no-gutters justify="center" class="pt-3 pb-10">
          <v-col>
            <b>0</b> registrations | <b>0</b> exact matches
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, useCssModule, watch } from '@vue/composition-api'
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
    resultsType: {
      type: String,
      default: 'searched'
    }
  },
  setup (props) {
    const style = useCssModule()
    const { getSearchResults, getSavedResults } = useGetters<any>(['getSearchResults', 'getSavedResults'])
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
      resultResponse: computed((): SearchResponseIF => {
        let resp = null
        if (props.resultsType === 'searched') resp = getSearchResults.value
        else resp = getSavedResults.value

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
        return style['exact-match']
      }
      return style['normal-match']
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
      getClass,
      style
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
th {
  font-size: 0.875rem !important;
  color: $gray9 !important;
}
td {
  font-size: 0.875rem !important;
  color: $gray7 !important;
}
.divider {
  border-right:1px solid $gray3;
}
.exact-match td {
  background-color: $BCgovBlue0;
  font-weight: bold;
  pointer-events: none;
}
.exact-match i {
  color: $gray7 !important;
}
.main-results-div {
  width: 100%;
}
.result-info {
  color: $gray7 !important;
  font-size: 1rem;
}
.no-results-info {
  color: $gray9 !important;
  font-size: 0.825rem;
}
.no-results-title {
  font-size: 1rem;
}
</style>
