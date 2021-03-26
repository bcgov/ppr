<template>
  <v-container :class="[$style['main-results-div'], 'pa-0', 'white']">
    <v-row v-if="searched" no-gutters :class="[$style['result-info'], 'pl-5', 'pt-8']">
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
                      id="search-results-table"
                      :class="$style['results-table']"
                      fixed
                      fixed-header
                      :headers="headers"
                      height="20rem"
                      hide-default-footer
                      :items="results"
                      :item-class="getClass"
                      item-key="baseRegistrationNumber"
                      multi-sort
                      return-object
                      show-select
                      @toggle-select-all="selectAll"
                      v-model="selected">
          <template v-slot:[`item.data-table-select`]="{ item, isSelected, select }">
            <td v-if="isSelected && item.matchType === 'EXACT'" :class="$style['checkbox-info']">
              <v-row no-gutters>
                <v-col cols="2">
                  <v-simple-checkbox readonly :ripple="false" :value="isSelected"/>
                </v-col>
                <v-col cols="auto" class="pl-2 pt-1">
                  exact match added
                </v-col>
              </v-row>
            </td>
            <td v-else :class="$style['checkbox-info']">
              <v-row no-gutters>
                <v-col cols="2">
                  <v-simple-checkbox :ripple="false" :value="isSelected" @click="select(!isSelected)"/>
                </v-col>
                <v-col v-if="isSelected" cols="auto" class="pl-2 pt-1">
                  added
                </v-col>
              </v-row>
            </td>
          </template>
          <template v-slot:[`item.vehicleCollateral.type`]="{ item }">
            <span v-if="item.vehicleCollateral.type === 'MV'">
              Motor Vehicle
            </span>
            <span v-else-if="item.vehicleCollateral.type === 'MH'">
              Manufactured Home
            </span>
            <span v-else-if="item.vehicleCollateral.type === 'AC'">
              Aircraft
            </span>
            ({{ item.vehicleCollateral.type }})
          </template>
          <template v-slot:[`item.vehicleCollateral.make`]="{ item }">
            {{ item.vehicleCollateral.make }} {{ item.vehicleCollateral.model }}
          </template>
          <template v-slot:[`item.debtor.personName`]="{ item }">
            {{ item.debtor.personName.first }} {{ item.debtor.personName.second }} {{ item.debtor.personName.last }}
          </template>
          <template v-slot:[`item.debtor.birthDate`]="{ item }">
            {{ displayDate(item.debtor.birthDate) }}
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

import { searchTableHeaders } from '@/resources'
import { SearchResponseIF, SearchResultIF, TableHeadersIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { MatchTypes } from '@/enums'
import { convertDate } from '@/utils'

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
    }
  },
  setup (props, { emit }) {
    const style = useCssModule()
    const { getSearchResults } = useGetters<any>(['getSearchResults'])
    const localState = reactive({
      searched: false,
      searchValue: '',
      selected: props.defaultSelected,
      selectedInitialized: false,
      headers: props.defaultHeaders,
      results: props.defaultResults,
      exactMatchesLength: 0,
      totalResultsLength: 0,
      selectedLength: computed((): number => {
        return localState.selected?.length | 0
      }),
      setTableData: computed((): SearchResponseIF => {
        let resp = null
        resp = getSearchResults.value

        if (resp) {
          localState.searchValue = resp.searchQuery.criteria.value
          localState.searched = true
          localState.headers = searchTableHeaders[resp.searchQuery.type]
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
    const displayDate = (dateString:string) => {
      const date = new Date(dateString)
      return convertDate(date, false)
    }
    const getClass = (item:SearchResultIF):string => {
      if (item.matchType === MatchTypes.EXACT) {
        return style['exact-match']
      }
      return style['normal-match']
    }
    const selectAll = (props: { items:Array<SearchResultIF>, value:boolean }):void => {
      // ensures exact matches are never deselected
      if (!props.value) {
        const selected = []
        props.items.forEach(item => {
          if (item.matchType === MatchTypes.EXACT) {
            selected.push(item)
          }
        })
        localState.selected = selected
      }
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
    watch(() => localState.selected, (val) => {
      if (!localState.selectedInitialized) {
        localState.selectedInitialized = true
        return
      }
      emit('selected-matches', val)
    })

    return {
      ...toRefs(localState),
      displayDate,
      getClass,
      selectAll,
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
  min-width: 9rem;
}
.checkbox-info {
  font-size: 0.725rem !important;
  font-weight: bold;
  text-align: center;
}
.divider {
  border-right:1px solid $gray3;
}
.exact-match td {
  background-color: $blueSelected;
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
