<template>
  <v-container class="main-results-div pa-0 white">
    <v-row v-if="searched" class="result-info pl-5 pt-30px" align="center" no-gutters>
      <v-col style="padding-right: 30px;" cols="auto">
        <v-row no-gutters>
          <v-col class="divider pr-3 mr-3" cols="auto">
            <b>{{ totalResultsLength }}</b> registrations found
          </v-col>
          <v-col class="divider pr-3 mr-3" cols="auto">
            <b>{{ exactMatchesLength }}</b> exact matches
          </v-col>
          <v-col v-if="totalResultsLength !== 0" cols="auto">
            Registrations added to search result report: <b>{{ selectedLength }}</b>
          </v-col>
        </v-row>
      </v-col>
      <v-col align-self="end" style="padding-right: 30px; width: 320px;">
        <v-btn class="float-right" color="primary" depressed plain @click="console.log('submit')">
          <img class="pr-1" src="@/assets/svgs/pdf-icon-white.svg">
          Generate Search Result Report
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-if="totalResultsLength !== 0" class="pt-3" no-gutters>
      <v-col cols="12">
        <v-data-table
          v-if="results"
          id="search-results-table"
          class="results-table"
          disable-sort
          fixed
          fixed-header
          :headers="headers"
          hide-default-footer
          :items="results"
          :item-class="getClass"
          item-key="id"
          mobile-breakpoint="0"
          return-object
          show-select
          @toggle-select-all="selectAll"
          v-model="selected"
        >
          <template v-slot:[`item.data-table-select`]="{ item, isSelected, select }">
            <td v-if="isSelected && item.matchType === 'EXACT'" class="checkbox-info">
              <v-row no-gutters>
                <v-col cols="2">
                  <v-simple-checkbox readonly :ripple="false" :value="isSelected"/>
                </v-col>
                <v-col cols="auto" class="pl-2 pt-1">
                  exact match added
                </v-col>
              </v-row>
            </td>
            <td v-else class="checkbox-info">
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
            {{ item.debtor.personName.first }}
            {{ item.debtor.personName.second }}
            {{ item.debtor.personName.middle }}
            {{ item.debtor.personName.last }}
          </template>
          <template v-slot:[`item.debtor.birthDate`]="{ item }">
            {{ displayDate(item.debtor.birthDate) }}
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row v-else id="search-no-results-info" class="no-results-info pt-3" justify="center" no-gutters>
      <v-col cols="auto">
        <v-row class="no-results-title pt-10" justify="center" no-gutters>
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
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
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
    const displayDate = (dateString:string):string => {
      if (!dateString) {
        return ''
      }
      const date = new Date(dateString)
      return convertDate(date, false, false)
    }
    const getClass = (item:SearchResultIF):string => {
      if (item.matchType === MatchTypes.EXACT) return 'exact-match'
      return 'normal-match'
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
      selectAll
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
button {
  font-weight: normal !important;
}
td {
  font-size: 0.875rem !important;
  color: $gray7 !important;
}
th {
  font-size: 0.875rem !important;
  color: $gray9 !important;
}
.checkbox-info {
  font-size: 0.725rem !important;
  font-weight: bold;
  text-align: center;
}
.divider {
  border-right: 1px solid $gray3;
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
.no-results-info {
  color: $gray9 !important;
  font-size: 0.825rem;
}
.no-results-title {
  font-size: 1rem;
}
.result-info {
  color: $gray7 !important;
  font-size: 1rem;
}
::v-deep .results-table .v-data-table__wrapper {
  max-height: 550px;
}
::v-deep .results-table .v-data-table__wrapper table tbody {
  tr {
    height: 54px;
  }

  tr:not(.v-data-table__selected)::before,
  tr:not(.v-data-table__selected)::after,
  tr:not(.v-data-table__selected):hover {
    // $gray1 at 75%
    background-color: #f1f3f5BF !important;
  }

  tr.v-data-table__selected::before,
  tr.v-data-table__selected::after,
  tr.v-data-table__selected:hover {
    background-color: #E4EDF7 !important;
  }
}
</style>
