<template>
  <v-container class="pa-0 bg-white pb-0">
    <!-- Results Header -->
    <v-row
      v-if="searched"
      class="result-info px-5 pt-30px"
      align="center"
      noGutters
    >
      <v-col cols="9">
        <v-row noGutters>
          <v-col
            class="divider pr-3 mr-3"
            cols="auto"
          >
            <p><b>{{ totalResultsLength }}</b> matches found</p>
          </v-col>
          <v-col
            :class="totalResultsLength !== 0 ? 'divider pr-3 mr-3' : ''"
            cols="auto"
          >
            <p><b>{{ exactMatchResults.length }}</b> exact matches</p>
          </v-col>
          <v-col
            v-if="totalResultsLength !== 0"
            cols="auto"
          >
            <p>
              <b>{{ selectedLength }}</b> total matches in
              <b>{{ selectedRegistrationsLength }}</b> registrations added to report
              <v-tooltip
                v-if="selectedRegistrationsLength !== selectedLength"
                class="pa-2"
                contentClass="top-tooltip"
                location="top"
                transition="fade-transition"
              >
                <template #activator="{ props }">
                  <v-icon
                    class="pl-2"
                    color="primary"
                    v-bind="props"
                  >
                    mdi-information-outline
                  </v-icon>
                </template>
                <div class="pt-2 pb-2">
                  {{ tooltipTxtSrchMtchs }}
                </div>
              </v-tooltip>
            </p>
          </v-col>
        </v-row>
      </v-col>
      <v-col>
        <v-btn
          id="btn-generate-result"
          class="float-right"
          color="primary"
          variant="flat"
          @click="emit('submit')"
        >
          <img
            class="pr-1"
            src="@/assets/svgs/pdf-icon-white.svg"
          >
          Generate Search Result Report
        </v-btn>
      </v-col>
    </v-row>

    <!-- Results Table -->
    <v-row
      v-if="results && results.length"
      class="pt-3"
      noGutters
    >
      <v-col cols="12">
        <v-table
          v-if="results"
          id="search-results-table"
          class="results-table"
          :class="{'hide-scroll': results.length <= 1 }"
          fixedHeader
        >
          <template #default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th
                  v-for="(header, index) in headers"
                  :key="header.value"
                  :class="header.class"
                >
                  <!-- Search selection checkbox -->
                  <template v-if="index === 0">
                    <v-checkbox
                      v-model="selectAll"
                      class="header-checkbox"
                      color="primary"
                      hideDetails
                      label="Select All"
                      :indeterminate="(exactMatchResults.length && !selectAll) || false"
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
                  <td
                    class="group-header px-2"
                    :colspan="headers.length"
                  >
                    <span>Exact Matches ({{ exactMatchResults.length }})</span>
                  </td>
                </tr>
                <!-- Grouped Rows -->
                <tr
                  v-for="(item, index) in exactMatchResults"
                  :key="`exact - ${item}: ${index}`"
                  disabled
                  class="selected-row"
                >
                  <!-- Exact Selection Checkboxes -->
                  <td class="checkbox-info">
                    <v-row
                      noGutters
                    >
                      <v-col
                        cols="3"
                        class="checkbox-col"
                      >
                        <v-checkbox
                          class="exact-match-checkbox mt-n4"
                          :readonly="true"
                          :ripple="false"
                          :disabled="true"
                          :modelValue="isSelected(item)"
                        />
                      </v-col>
                      <span class="exact-match-checkbox-label mt-1">Exact Match</span>
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
                <td
                  class="group-header px-2 text-center"
                  :colspan="headers.length"
                >
                  <span>No Exact Matches</span>
                </td>
              </tr>

              <!-- Similar matches -->
              <template v-if="similarMatchResults.length">
                <!-- Group Header -->
                <tr v-if="exactMatchResults.length">
                  <td
                    class="group-header px-2"
                    :colspan="headers.length"
                  >
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
                    <v-row noGutters>
                      <v-col
                        cols="2"
                        class="checkbox-col"
                      >
                        <v-checkbox
                          class="mt-n4"
                          :ripple="false"
                          :modelValue="isSelected(item)"
                          @input="toggleSelected(item)"
                        />
                      </v-col>
                      <span class="ml-3 mt-1">added</span>
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
        </v-table>
      </v-col>
    </v-row>
    <v-row
      v-else
      id="search-no-results-info"
      class="text-center my-6"
      noGutters
    >
      <v-col>
        <p class="no-results-title pt-10">
          <b>Nil Result</b>
        </p>
        <p class="pt-2">
          No registered liens or encumbrances have been found on file that match EXACTLY to the
          search criteria above and no similar matches to the criteria have been found.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { searchTableHeaders, VehicleTypes } from '@/resources'
import { BaseHeaderIF, SearchResponseIF, SearchResultIF, TableHeadersIF } from '@/interfaces'
import { APISearchTypes, MatchTypes } from '@/enums'
import { convertDate } from '@/utils'
import { storeToRefs } from 'pinia'

export default defineComponent({
  props: {
    defaultHeaders: {
      type: Array as () => TableHeadersIF,
      default: () => []
    },
    defaultResults: {
      type: Array as () => Array<SearchResultIF>,
      default: () => []
    }
  },
  emits: ['selectedMatches', 'submit'],
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

    const displayDate = (dateString: string): string => {
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

    watch(() => localState.results, () => {
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
      emit('selectedMatches', selected)
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

thead tr th:first-child {
  width: 12rem;
}

th {
  vertical-align: middle !important;
  padding-bottom: 10px !important;
}

.header-checkbox {
  :deep(.v-selection-control .v-label) {
    color: $app-blue;
  }
}

.exact-match-checkbox-row {
  display: flex;
  flex-direction: row;
}

.selected-row {
  td {
    background: $blueSelected;
  }
}

.checkbox-info {
  font-size: 0.75rem !important;
  font-weight: bold;
  text-align: center;
}

.checkbox-col {
  max-height: 10px;
}

:deep(.v-selection-control__input>.v-icon) {
  color: $app-blue !important;
}

:deep(.v-table__wrapper) {
  max-height: 550px;
}
.hide-scroll {
  :deep(.v-table__wrapper) {
    overflow: hidden!important;
  }
}
</style>
