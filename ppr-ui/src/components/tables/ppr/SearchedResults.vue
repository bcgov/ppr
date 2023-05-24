<template>
  <v-container class="main-results-div pa-0 white">
    <v-row v-if="searched" class="result-info pl-5 pt-30px" align="center" no-gutters>
      <v-col style="padding-right: 30px;" cols="auto">
        <v-row no-gutters>
          <v-col class="divider pr-3 mr-3" cols="auto">
            <b>{{ totalResultsLength }}</b> matches found
          </v-col>
          <v-col :class="totalResultsLength !== 0 ? 'divider pr-3 mr-3' : ''" cols="auto">
            <b>{{ exactMatchesLength }}</b> exact matches
          </v-col>
          <v-col v-if="totalResultsLength !== 0" cols="auto">
            <b>{{ selectedLength }}</b> total matches in
            <b>{{ selectedRegistrationsLength }}</b> registrations added to report
            <v-tooltip
              v-if="selectedRegistrationsLength !== selectedLength"
              class="pa-2"
              content-class="top-tooltip"
              nudge-right="6"
              top
              transition="fade-transition"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-icon class="pl-2" color="primary" v-bind="attrs" v-on="on">mdi-information-outline</v-icon>
              </template>
              <div class="pt-2 pb-2">
                {{ tooltipTxtSrchMtchs }}
              </div>
            </v-tooltip>
          </v-col>
        </v-row>
      </v-col>
      <v-col align-self="end" style="padding-right: 30px; width: 320px;">
        <v-btn id="btn-generate-result" class="float-right" color="primary" depressed plain @click="emit('submit')">
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
          group-by="matchType"
          :headers="headers"
          hide-default-footer
          :items="results"
          :item-class="getClass"
          item-key="id"
          :items-per-page="-1"
          mobile-breakpoint="0"
          return-object
          show-select
          @toggle-select-all="selectAll($event)"
          v-model="selected"
        >
          <template v-slot:[`header.data-table-select`]="{ props, on }">
            <v-checkbox
              class="header-checkbox ma-0 pa-0"
              color="primary"
              hide-details
              :indeterminate="props.indeterminate"
              label="Select All"
              :value="props.value"
              @click="on.input(!props.value)"
            />
          </template>
          <template v-slot:[`group.header`]="{ group }">
            <td
              class="group-header px-2"
              :colspan="headers.length"
              :style="exactMatchesLength === 0 ? 'text-align: center;' : ''"
            >
              <span v-if="group === 'EXACT'">
                Exact Matches ({{ exactMatchesLength }})
              </span>
              <span v-else-if="exactMatchesLength === 0">
                No Exact Matches
              </span>
              <span v-else>
                Similar Matches ({{ totalResultsLength - exactMatchesLength }})
              </span>
            </td>
          </template>
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
            {{ getVehicleDescription(item.vehicleCollateral.type) }}
          </template>
          <template v-slot:[`item.vehicleCollateral.make`]="{ item }">
            {{ item.vehicleCollateral.make }} {{ item.vehicleCollateral.model }}
          </template>
          <template v-slot:[`item.debtor.personName`]="{ item }">
            {{ item.debtor.personName.last }},
            {{ item.debtor.personName.first }}
            {{ item.debtor.personName.middle }}
            {{ item.debtor.personName.second }}
          </template>
          <template v-slot:[`item.debtor.birthDate`]="{ item }">
            {{ displayDate(item.debtor.birthDate) }}
          </template>
          <template v-slot:[`item.registrationNumber`]="{ item }">
            <span>{{ item.baseRegistrationNumber }}</span>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row v-else id="search-no-results-info" class="no-results-info pb-10" justify="center" no-gutters>
      <v-col cols="8">
        <p class="no-results-title ma-0 pt-10"><b>Nil Result</b></p>
        <p class="ma-0 pt-2">
          No registered liens or encumbrances have been found on file that match EXACTLY to the
          search criteria above and no similar matches to the criteria have been found.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'

import { searchTableHeaders, VehicleTypes } from '@/resources'
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
  emits: ['selected-matches', 'submit'],
  setup (props, { emit }) {
    const { getSearchResults } = useStore()
    const localState = reactive({
      searched: false,
      searchValue: '',
      selected: props.defaultSelected,
      selectedInitialized: false,
      tooltipTxtSrchMtchs: 'One or more of the selected matches appear in ' +
        'the same registration. That registration will only be shown once in the report.',
      headers: props.defaultHeaders,
      results: props.defaultResults,
      exactMatchRegistrations: 0,
      exactMatchesLength: 0,
      totalResultsLength: 0,
      selectedRegistrationsLength: 0,
      selectedLength: computed((): number => {
        return localState.selected?.length | 0
      }),
      setTableData: computed((): SearchResponseIF => {
        let resp = null
        resp = getSearchResults

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
    const getVehicleDescription = (code: string): string => {
      const vehicle = VehicleTypes.find(obj => obj.value === code)
      return vehicle.text
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
      for (const x in results) {
        if (results[x].matchType === MatchTypes.EXACT) {
          count += 1
          selectedExactMatches.push(results[x])
        }
      }
      localState.exactMatchesLength = count
      localState.selected = selectedExactMatches
    })
    watch(() => localState.selected, (selected) => {
      const baseRegs = []
      for (const x in selected) {
        if (!baseRegs.includes(selected[x].baseRegistrationNumber)) {
          baseRegs.push(selected[x].baseRegistrationNumber)
        }
      }
      localState.selectedRegistrationsLength = baseRegs.length

      if (!localState.selectedInitialized) {
        localState.selectedInitialized = true
        return
      }
      emit('selected-matches', selected)
    })

    return {
      ...toRefs(localState),
      displayDate,
      emit,
      getClass,
      getVehicleDescription,
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
.group-header, .group-header:hover {
  background-color: $gray3;
  font-weight: bold;
}
.main-results-div {
  width: 100%;
}
.no-results-info {
  color: $gray7 !important;
  font-size: 1rem;
  text-align: center;
}
.no-results-title {
  font-size: 1.125rem;
}
.result-info {
  color: $gray7 !important;
  font-size: 1rem;
}
::v-deep .header-checkbox .v-input__control .v-input__slot .v-label {
  color: $primary-blue !important;
  font-size: 0.875rem !important;
  font-weight: normal;
}
::v-deep .header-checkbox .v-input__control .v-input--selection-controls__input i,
::v-deep .header-checkbox .v-input__control .v-input--selection-controls__ripple,
::v-deep .header-checkbox .v-input__control .mdi-checkbox-blank-outline,
::v-deep .checkbox-info .row .col .v-simple-checkbox .v-input--selection-controls__ripple,
::v-deep .checkbox-info .row .col .v-simple-checkbox .mdi-checkbox-blank-outline {
  color: $primary-blue !important;
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
