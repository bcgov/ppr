<template>
  <v-container class="main-results-div pa-0 white">{{selected}}
    <!-- Results Header -->
    <v-row v-if="searched" class="result-info pl-5 pt-30px" align="center" no-gutters>
      <v-col style="padding-right: 30px;" cols="auto">
        <v-row no-gutters>
          <v-col class="divider pr-3 mr-3" cols="auto">
            <b>{{ totalResultsLength }}</b> matches found
          </v-col>
          <v-col :class="totalResultsLength !== 0 ? 'divider pr-3 mr-3' : ''" cols="auto">
            <b>{{ exactMatchResults.length }}</b> exact matches
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
        <v-btn id="btn-generate-result" class="float-right" color="primary" depressed @click="emit('submit')">
          <img class="pr-1" src="@/assets/svgs/pdf-icon-white.svg">
          Generate Search Result Report
        </v-btn>
      </v-col>
    </v-row>

    <!-- Results Table -->
    <v-row v-if="results && results.length" class="pt-3" no-gutters>
      <v-col cols="12">
        <v-simple-table
          v-if="results"
          id="search-results-table"
          class="results-table"
          fixed-header
        >
          <template v-slot:default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th v-for="(header, index) in headers" :key="header.value" :class="header.class">
                  <!-- Search selection checkbox -->
                  <template v-if="index === 0">
                    <v-checkbox
                      class="header-checkbox ma-0 pa-0"
                      color="primary"
                      hide-details
                      label="Select All"
                      :indeterminate="(exactMatchResults.length && !selectAll) || false"
                      v-model="selectAll"
                    />
                  </template>
                  <template v-else>
                    {{ header.text }}
                  </template>
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody v-if="results.length > 0">

              <!-- Exact Matches -->
              <template v-if="exactMatchResults.length">
                <!-- Group Header -->
                <tr>
                  <td class="group-header px-2" :colspan="headers.length">
                    <span>Exact Matches ({{ exactMatchResults.length }})</span>
                  </td>
                </tr>
                <!-- Grouped Rows -->
                <tr
                  v-for="(item, index) in exactMatchResults"
                  disabled
                  class="selected-row"
                  :key="`exact - ${item}: ${index}`"
                >
                  <!-- Exact Selection Checkboxes -->
                  <td class="checkbox-info exact-match">
                    <v-row no-gutters>
                      <v-col cols="2">
                        <v-simple-checkbox readonly :ripple="false" :value="isSelected(item)"/>
                      </v-col>
                      <v-col cols="auto" class="pl-2 pt-1">
                        exact match added
                      </v-col>
                    </v-row>
                  </td>

                  <!-- Vehicle -->
                  <template v-if="item.vehicleCollateral">
                    <td v-if="searchType === APISearchTypes.MHR_NUMBER">
                      {{ item.vehicleCollateral.manufacturedHomeRegistrationNumber }}
                    </td>
                    <td>{{ item.vehicleCollateral.serialNumber }}</td>
                    <td v-if="![APISearchTypes.MHR_NUMBER, APISearchTypes.AIRCRAFT].includes(searchType)">
                      {{ getVehicleDescription(item.vehicleCollateral.type) }}
                    </td>
                    <td>{{ item.vehicleCollateral.year }}</td>
                    <td>
                      {{ item.vehicleCollateral.make }} {{ item.vehicleCollateral.model }}
                    </td>
                  </template>

                  <!-- Debtor -->
                  <template v-if="item.debtor">
                    <!-- Person -->
                    <template v-if="item.debtor.personName">
                      <td>
                        {{ item.debtor.personName.last }},
                        {{ item.debtor.personName.first }}
                        {{ item.debtor.personName.middle }}
                        {{ item.debtor.personName.second }}
                      </td>
                      <td>{{ displayDate(item.debtor.birthDate) }}</td>
                      <td>{{ item.baseRegistrationNumber }}</td>
                    </template>

                    <!-- Business -->
                    <template v-if="item.debtor.businessName">
                      <td>{{ item.debtor.businessName }}</td>
                    </template>
                  </template>

                  <!-- Base Registration -->
                  <template v-if="searchType === APISearchTypes.REGISTRATION_NUMBER">
                    <td>{{ item.baseRegistrationNumber }}</td>
                  </template>

                </tr>
              </template>
              <tr v-else>
                <td class="group-header px-2 text-center" :colspan="headers.length"><span>No Exact Matches</span></td>
              </tr>

              <!-- Similar matches -->
              <template v-if="similarMatchResults.length">
                <!-- Group Header -->
                <tr v-if="exactMatchResults.length">
                  <td class="group-header px-2" :colspan="headers.length">
                    <span>Similar Matches ({{ similarMatchResults.length }})</span>
                  </td>
                </tr>
                <!-- Grouped Rows -->
                <tr
                  v-for="(item, index) in similarMatchResults"
                  :key="`similar - ${item}: ${index}`"
                  :class="{'selected-row' : isSelected(item)}"
                >
                  <!-- Exact Selection Checkboxes -->
                  <td class="checkbox-info">
                    <v-row no-gutters>
                      <v-col cols="2">
                        <v-simple-checkbox
                          :ripple="false"
                          :value="isSelected(item)"
                          @input="toggleSelected(item)"
                        />
                      </v-col>
                      <v-col v-if="isSelected(item)" cols="auto" class="pl-2 pt-1">
                        added
                      </v-col>
                    </v-row>
                  </td>

                  <!-- Vehicle -->
                  <template v-if="item.vehicleCollateral">
                    <td v-if="searchType === APISearchTypes.MHR_NUMBER">
                      {{ item.vehicleCollateral.manufacturedHomeRegistrationNumber }}
                    </td>
                    <td>{{ item.vehicleCollateral.serialNumber }}</td>
                    <td v-if="![APISearchTypes.MHR_NUMBER, APISearchTypes.AIRCRAFT].includes(searchType)">
                      {{ getVehicleDescription(item.vehicleCollateral.type) }}
                    </td>
                    <td>{{ item.vehicleCollateral.year }}</td>
                    <td>
                      {{ item.vehicleCollateral.make }} {{ item.vehicleCollateral.model }}
                    </td>
                  </template>

                  <!-- Debtor -->
                  <template v-if="item.debtor">
                    <!-- Person -->
                    <template v-if="item.debtor.personName">
                      <td>
                        {{ item.debtor.personName.last }},
                        {{ item.debtor.personName.first }}
                        {{ item.debtor.personName.middle }}
                        {{ item.debtor.personName.second }}
                      </td>
                      <td>{{ displayDate(item.debtor.birthDate) }}</td>
                      <td>{{ item.baseRegistrationNumber }}</td>
                    </template>
                    <!-- Business -->
                    <template v-if="item.debtor.businessName">
                      <td>{{ item.debtor.businessName }}</td>
                    </template>
                  </template>

                  <!-- Base Registration -->
                  <template v-if="searchType === APISearchTypes.REGISTRATION_NUMBER">
                    <td>{{ item.baseRegistrationNumber }}</td>
                  </template>

                </tr>
              </template>
            </tbody>
          </template>
        </v-simple-table>
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
// eslint-disable-line no-unused-vars
import { BaseHeaderIF, SearchResponseIF, SearchResultIF, TableHeadersIF } from '@/interfaces'
import { APISearchTypes, MatchTypes } from '@/enums'
import { convertDate } from '@/utils'
import { storeToRefs } from 'pinia'

export default defineComponent({
  props: {
    defaultHeaders: {
      type: Array as () => TableHeadersIF
    },
    defaultResults: {
      type: Array as () => Array<SearchResultIF>
    }
  },
  emits: ['selected-matches', 'submit'],
  setup (props, { emit }) {
    const { getSearchResults } = storeToRefs(useStore())

    const localState = reactive({
      searched: false,
      searchValue: '',
      selected: [],
      selectAll: false,
      selectedInitialized: false,
      tooltipTxtSrchMtchs: 'One or more of the selected matches appear in ' +
          'the same registration. That registration will only be shown once in the report.',
      headers: props.defaultHeaders as Array<BaseHeaderIF>,
      results: props.defaultResults,
      exactMatchRegistrations: 0,
      totalResultsLength: 0,
      selectedRegistrationsLength: 0,
      searchType: computed((): APISearchTypes => {
        return getSearchResults.value?.searchQuery.type
      }),
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
      }),
      exactMatchResults: computed((): Array<SearchResultIF> => {
        return localState.results?.filter(result => result.matchType === MatchTypes.EXACT) || []
      }),
      similarMatchResults: computed((): Array<SearchResultIF> => {
        return localState.results?.filter(result => result.matchType === MatchTypes.SIMILAR) || []
      })
    })

    const isSelected = (item: SearchResultIF): boolean => {
      return localState.selected.some(result => result.id === item.id)
    }

    const toggleSelected = (item: SearchResultIF): void => {
      isSelected(item)
        ? localState.selected = [...localState.selected.filter(result => result.id !== item.id)]
        : localState.selected = [...localState.selected, { ...item }]
    }

    const toggleSelectAll = (selectAll: boolean): void => {
      selectAll
        ? localState.selected = [...localState.selected, ...localState.similarMatchResults]
        : localState.selected = [...localState.exactMatchResults]
    }

    const displayDate = (dateString:string):string => {
      if (!dateString) {
        return ''
      }
      const date = new Date(dateString)
      return convertDate(date, false, false)
    }

    const getVehicleDescription = (code: string): string => {
      const vehicle = VehicleTypes.find(obj => obj.value === code)
      return vehicle.text
    }

    watch(() => localState.results, (results) => {
      localState.selected = [...localState.exactMatchResults]
    })
    watch(() => localState.selectAll, (selectAll: boolean) => {
      toggleSelectAll(selectAll)
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
    }, { immediate: true })

    return {
      emit,
      displayDate,
      isSelected,
      toggleSelected,
      getVehicleDescription,
      APISearchTypes,
      ...toRefs(localState)
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
thead tr th:first-child {
  width: 11rem;
  min-width: 11rem;
}
.selected-row {
  td {
    background: $blueSelected;
  }
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
  cursor: default;
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
