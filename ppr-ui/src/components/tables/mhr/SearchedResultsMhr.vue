<template>
  <v-container class="bg-white pa-0 ma-0">
    <!-- Table Header -->
    <section
      id="search-meta-info"
    >
      <v-row 
        no-gutters 
        class="px-6 py-4"
        :class="{'bg-lt-blue': !isReviewMode}"
      >
        <p class="search-sub-title">
          <strong>Search Results:</strong> {{ searchType }} - <b>"{{ searchValue }}"</b>
        </p>
      </v-row>
      <v-row
        v-if="searched && !isReviewMode"
        id="search-summary-info"
        class="result-info pt-6 px-6"
      >
        <v-col
          id="home-results-count"
          cols="auto"
        >
          <p class="divider pr-3">
            Matches Found: <b>{{ totalResultsLength }}</b>
          </p>
        </v-col>
        <v-col
          id="selected-results-count"
          cols="auto"
          class="pl-6"
        >
          <p class="divider pr-3">
            Matches Selected: <b>{{ selectedMatchesLength }}</b>
          </p>
        </v-col>
        <v-col
          cols="auto"
          class="pl-0"
        >
          <p id="selected-lien-count">
            PPR Lien Searches Selected: <b>{{ selectedLiensLength }}</b>
          </p>
        </v-col>
        <v-col class="mr-6">
          <v-row class="float-right">
            <FolioNumber
              class="mr-3 ml-0 mt-n2"
              :default-folio-number="folioNumber"
              @folio-number="updateFolioOrReference($event)"
              @folio-error="folioError = $event"
            />
            <v-btn
              id="review-confirm-btn"
              color="primary"
              filled
              class="important-btn"
              :disabled="totalResultsLength === 0"
              @click="reviewAndConfirm()"
            >
              Review and Confirm
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
      <v-row
        v-else
        class="result-info px-6 my-0"
      >
        <v-col
          id="review-results-count"
          cols="auto"
        >
          <span class="divider pr-3">Matches Selected: <b>{{ selectedMatchesLength }}</b></span>
          <span class="divider px-3">Registrations: <b>{{ uniqueResultsSelected.length }}</b></span>
          <span class="pl-3">PPR Lien Searches Selected: <b>{{ uniqueResultsLienSelected.length }}</b></span>
        </v-col>
      </v-row>
    </section>

    <!-- Search Results Table -->
    <v-row
      v-if="totalResultsLength !== 0"
      class="pt-3"
    >
      <v-col cols="12">
        <v-table
          :id="`mh-search-results-table`"
          class="results-table"
          :class="{ 'review-mode' : isReviewMode }"
          fixed-header
        >
          <template #default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th
                  v-if="!isReviewMode"
                  class="column-xxs"
                >
                  <!-- First Header -->
                  <!-- Search selection checkbox -->
                    <v-tooltip
                      location="top"
                      content-class="top-tooltip"
                      transition="fade-transition"
                    >
                      <template #activator="{ props }">
                        <span v-bind="props">
                          <v-checkbox
                            id="select-all-checkbox"
                            v-model="selectAll"
                            class="header-checkbox ma-0 pa-0 align-start"
                            hide-details
                          />
                        </span>
                      </template>
                      <div class="pt-2 pb-2">
                        Select this to include all manufactured homes.
                      </div>
                    </v-tooltip>
                </th>
                <th
                  v-for="(header, index) in headers"
                  :key="header.value"
                  :class="header.class"
                >
                  <!-- Last Header -->
                  <!-- Lien selection checkbox -->
                  <span v-if="index === 9 && !isReviewMode">
                    <v-checkbox
                      id="select-all-lien-checkbox"
                      v-model="selectAllLien"
                      class="header-checkbox ma-0 pa-0 align-start "
                      label="Include lien information for all selections"
                      :disabled="selectedMatchesLength === 0"
                      hide-details
                    />
                  </span>

                  <!-- Standard Headers -->
                  <span
                    v-else
                    class="flex"
                    @click="sortTable(header.value, header.sortable)"
                  >
                    <span
                      v-if="header.value === 'ownerName.first'"
                      class="pr-2"
                    >
                      {{ ownerOrOrgHeader }} Name
                    </span>
                    <span
                      v-else-if="header.value === 'ownerStatus'"
                      :class="index === 0 && 'pl-8'"
                      class="pr-2"
                    >
                      {{ ownerOrOrgHeader }} Status
                    </span>
                    <span 
                      v-else
                      class="pr-2"
                    >
                      {{ header.text }}
                    </span>
                    <SortingIcon
                      v-if="header.sortable && sortOptions.sortBy === header.value"
                      :sort-asc="sortOptions.isAsc"
                      color="primary"
                    />
                  </span>
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody v-if="results.length > 0">
              <tr
                v-for="item in results"
                :key="item.id"
                :class="{
                  'selected-row': item.selected && !isReviewMode,
                  'no-border-bottom': hasMultipleSelections(item.mhrNumber) &&
                    isFirstSelectionOfMultiples(item.mhrNumber, item.id)
                }"
              >
                <!-- Name search -->
                <template v-if="isOwnerOrOrgSearch">
                  <template v-if="!isReviewMode">
                    <SearchedResultsMhrTableRow
                      :headers="headers"
                      :item="item"
                      @on-selection-checkbox-click="onSelectionCheckboxClick($event)"
                      @set-include-lien-info="setIncludeLienInfo($event)"
                    />
                  </template>
                  <template v-else>
                    <td>
                      <v-checkbox
                        v-model="item.selected"
                        :label="getOwnerName(item) + ' ' + getOwnerCount(item)"
                        :ripple="false"
                        hide-details
                        class="align-start"
                        @click="onSelectionCheckboxClick(item)"
                      />
                    </td>
                    <template v-if="hasMultipleSelections(item.mhrNumber)">
                      <template v-if="isFirstSelectionOfMultiples(item.mhrNumber, item.id)">
                        <td>
                          <v-tooltip
                            location="top"
                            content-class="top-tooltip"
                            transition="fade-transition"
                          >
                            <template #activator="{ props }">
                              <span
                                v-bind="props"
                                class="mhr-number"
                              >
                                <u>{{ item.mhrNumber }}</u>
                              </span>
                            </template>
                            <div class="pt-2 pb-2">
                              Multiple selections in the same registration are displayed together.
                            </div>
                          </v-tooltip>
                        </td>
                        <td>
                          {{ item.baseInformation.year || '-' }} / {{ item.baseInformation.make || '-' }} /
                          {{ item.baseInformation.model || '-' }}
                        </td>
                        <td>{{ item.homeLocation }}</td>
                        <td>{{ item.serialNumber }}</td>
                        <td class="lien-col">
                          <v-tooltip
                            location="top"
                            content-class="top-tooltip"
                            transition="fade-transition"
                          >
                            <template #activator="{ props }">
                              <span v-bind="props">
                                <v-checkbox
                                  v-model="item.includeLienInfo"
                                  class="align-start"
                                  :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                                  :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                                  :ripple="false"
                                  hide-details
                                />
                              </span>
                            </template>
                            <div class="pt-2 pb-2">
                              Select this to include a Personal Property Registry (PPR) lien search for the manufactured
                              home for an additional fee.
                              You must have the manufactured home selected before you can include the home's lien
                              search.
                            </div>
                          </v-tooltip>
                        </td>
                      </template>
                      <template v-else>
                        <td />
                        <td />
                        <td />
                        <td />
                        <td />
                        <td />
                      </template>
                    </template>

                    <template v-else-if="!hasMultipleSelections(item.mhrNumber)">
                      <td class="font-weight-bold">
                        {{ item.mhrNumber }}
                      </td>
                      <td>
                        {{ item.baseInformation.year || '-' }} / {{ item.baseInformation.make || '-' }} /
                        {{ item.baseInformation.model || '-' }}
                      </td>
                      <td>{{ item.homeLocation }}</td>
                      <td>{{ item.serialNumber }}</td>
                      <td class="lien-col">
                        <v-tooltip
                          location="top"
                          content-class="top-tooltip"
                          transition="fade-transition"
                        >
                          <template #activator="{ props }">
                            <span v-bind="props">
                              <v-checkbox
                                v-model="item.includeLienInfo"
                                class="align-start"
                                :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                                :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                                :ripple="false"
                                hide-details
                              />
                            </span>
                          </template>
                          <div class="pt-2 pb-2">
                            Select this to include a Personal Property Registry (PPR) lien search for the manufactured
                            home for an additional fee.
                            You must have the manufactured home selected before you can include the home's lien search.
                          </div>
                        </v-tooltip>
                      </td>
                    </template>
                  </template>
                </template>

                <!-- Mhr number search -->
                <template v-if="searchType === UIMHRSearchTypes.MHRMHR_NUMBER">
                  
                  <template v-if="!isReviewMode">
                    <SearchedResultsMhrTableRow
                      :headers="headers"
                      :item="item"
                      @on-selection-checkbox-click="onSelectionCheckboxClick($event)"
                      @set-include-lien-info="setIncludeLienInfo($event)"
                    />
                  </template>
                  <template v-else>
                    <td v-if="hasMultipleSelections(item.mhrNumber)">
                      <v-tooltip
                        location="top"
                        content-class="top-tooltip"
                        transition="fade-transition"
                      >
                        <template #activator="{ props }">
                          <span
                            v-bind="props"
                            class="mhr-number"
                          >
                            <u>{{ item.mhrNumber }}</u>
                          </span>
                        </template>
                        <div class="pt-2 pb-2">
                          Multiple selections in the same registration are displayed together.
                        </div>
                      </v-tooltip>
                    </td>
                    <td v-else>
                      <v-checkbox
                        v-model="item.selected"
                        class="align-start"
                        :label="item.mhrNumber"
                        :ripple="false"
                        hide-details
                        @click="onSelectionCheckboxClick(item)"
                      />
                    </td>
                    <td>{{ getOwnerName(item) }}</td>
                    <td>
                      {{ item.baseInformation.year || '-' }} / {{ item.baseInformation.make || '-' }} /
                      {{ item.baseInformation.model || '-' }}
                    </td>
                    <td>{{ item.homeLocation }}</td>
                    <td>{{ item.serialNumber }}</td>
                    <td class="lien-col">
                      <v-tooltip
                        location="top"
                        content-class="top-tooltip"
                        transition="fade-transition"
                      >
                        <template #activator="{ props }">
                          <span v-bind="props">
                            <v-checkbox
                              v-model="item.includeLienInfo"
                              class="align-start"
                              :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                              :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                              :ripple="false"
                              hide-details
                            />
                          </span>
                        </template>
                        <div class="pt-2 pb-2">
                          Select this to include a Personal Property Registry (PPR) lien search for the manufactured
                          home for an additional fee.
                          You must have the manufactured home selected before you can include the home's lien search.
                        </div>
                      </v-tooltip>
                    </td>
                  </template>
                </template>

                <!-- Serial number search -->
                <template v-if="searchType === UIMHRSearchTypes.MHRSERIAL_NUMBER">
                  
                  <template v-if="!isReviewMode">
                    <SearchedResultsMhrTableRow
                      :headers="headers"
                      :item="item"
                      @on-selection-checkbox-click="onSelectionCheckboxClick($event)"
                      @set-include-lien-info="setIncludeLienInfo($event)"
                    />
                  </template>
                  <template v-else>
                    <td>
                      <v-checkbox
                        v-model="item.selected"
                        class="align-start"
                        :label="item.activeCount > 1
                          ? `${item.serialNumber} (${item.activeCount})`
                          : `${item.serialNumber}`"
                        :ripple="false"
                        hide-details
                        @click="onSelectionCheckboxClick(item)"
                      />
                    </td>
                    <td class="font-weight-bold">
                      {{ item.mhrNumber }}
                    </td>
                    <td>{{ getOwnerName(item) }}</td>
                    <td>
                      {{ item.baseInformation.year || '-' }} / {{ item.baseInformation.make || '-' }} /
                      {{ item.baseInformation.model || '-' }}
                    </td>
                    <td>{{ item.homeLocation }}</td>
                    <td class="lien-col">
                      <v-tooltip
                        location="top"
                        content-class="top-tooltip"
                        transition="fade-transition"
                      >
                        <template #activator="{ props }">
                          <span v-bind="props">
                            <v-checkbox
                              v-model="item.includeLienInfo"
                              class="align-start"
                              :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                              :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                              :ripple="false"
                              hide-details
                            />
                          </span>
                        </template>
                        <div class="pt-2 pb-2">
                          Select this to include a Personal Property Registry (PPR) lien search for the manufactured
                          home for an additional fee.
                          You must have the manufactured home selected before you can include the home's lien search.
                        </div>
                      </v-tooltip>
                    </td>
                  </template>
                </template>
              </tr>
            </tbody>
          </template>
        </v-table>
      </v-col>
    </v-row>
    <v-row
      v-else
      id="search-no-results-info"
      class="no-results-info pb-10"
      justify="center"
    >
      <v-col cols="8">
        <p class="no-results-title ma-0 pt-10">
          <b>Nil Result</b>
        </p>
        <p class="ma-0 pt-2">
          No registered homes can be found to match the
          search criteria above.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import {
  mhSearchMhrNumberHeaders,
  mhSearchMhrNumberHeadersReview,
  mhSearchNameHeaders,
  mhSearchNameHeadersReview,
  mhSearchSerialNumberHeaders,
  mhSearchSerialNumberHeadersReview
} from '@/resources'
import type { BaseHeaderIF, ManufacturedHomeSearchResultIF, SortOptionIF } from '@/interfaces'
import { FolioNumber } from '@/components/common'
import { SortingIcon } from '../common'
import { SearchedResultsMhrTableRow } from '@/components/tables/mhr'
import { RouteNames, UIMHRSearchTypeMap, UIMHRSearchTypes, UIMHRSearchTypeValues } from '@/enums'
import { cloneDeep, uniqBy, filter, sortBy, groupBy, orderBy } from 'lodash'
import { storeToRefs } from 'pinia'
import { useNavigation } from '@/composables'

export default defineComponent({
  name: 'SearchedResultsMhr',
  components: {
    FolioNumber,
    SortingIcon,
    SearchedResultsMhrTableRow
  },
  props: {
    isReviewMode: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const router = useRouter()
    const { goToDash } = useNavigation()
    const {
      // Actions
      setSelectedManufacturedHomes,
      setFolioOrReferenceNumber,
      setMhrSearchResultSortOption,
    } = useStore()
    const {
      // Getters
      getManufacturedHomeSearchResults,
      getFolioOrReferenceNumber,
      getSearchedType,
      getSelectedManufacturedHomes,
      getMhrSearchResultSortOption
    } = storeToRefs(useStore())

    const localState = reactive({
      searched: false,
      searchValue: '',
      searchType: null as UIMHRSearchTypes,
      selectAll: false,
      selectAllLien: false,
      folioNumber: getFolioOrReferenceNumber.value,
      tooltipTxtSrchMtchs: 'One or more of the selected matches appear in ' +
        'the same registration. That registration will only be shown once in the report.',
      results: [] as ManufacturedHomeSearchResultIF[],
      groupedResults: [] as object as { string: ManufacturedHomeSearchResultIF[] }, // results grouped by Mhr Number
      uniqueResults: [] as ManufacturedHomeSearchResultIF[],
      uniqueResultsSelected: computed((): ManufacturedHomeSearchResultIF[] => {
        return uniqBy(localState.activeResults, UIMHRSearchTypeValues.MHRMHR_NUMBER).filter(item => item.selected)
      }),
      uniqueResultsLienSelected: computed((): ManufacturedHomeSearchResultIF[] => {
        return uniqBy(localState.results, UIMHRSearchTypeValues.MHRMHR_NUMBER)
          .filter(item => item.selected && item.includeLienInfo)
      }),
      totalResultsLength: 0,
      headerSearchTypeSlot: computed((): string => {
        switch (getSearchedType.value?.searchTypeUI) {
          case UIMHRSearchTypes.MHROWNER_NAME:
          case UIMHRSearchTypes.MHRORGANIZATION_NAME:
            return `header.${UIMHRSearchTypeValues.MHROWNER_NAME}`
          case UIMHRSearchTypes.MHRSERIAL_NUMBER:
            return `header.${UIMHRSearchTypeValues.MHRSERIAL_NUMBER}`
          case UIMHRSearchTypes.MHRMHR_NUMBER:
            return `header.${UIMHRSearchTypeValues.MHRMHR_NUMBER}`
          default:
            return ''
        }
      }),
      itemSearchTypeSlot: computed((): string => {
        switch (getSearchedType.value?.searchTypeUI) {
          case UIMHRSearchTypes.MHROWNER_NAME:
          case UIMHRSearchTypes.MHRORGANIZATION_NAME:
            return `item.${UIMHRSearchTypeValues.MHROWNER_NAME}`
          case UIMHRSearchTypes.MHRSERIAL_NUMBER:
            return `item.${UIMHRSearchTypeValues.MHRSERIAL_NUMBER}`
          case UIMHRSearchTypes.MHRMHR_NUMBER:
            return `item.${UIMHRSearchTypeValues.MHRMHR_NUMBER}`
          default:
            return ''
        }
      }),
      selectedMatchesLength: computed((): number => {
        return localState.results?.filter(item => item.selected === true).length
      }),
      selectedLiensLength: computed((): number => {
        return localState.results?.filter(item => item.includeLienInfo === true).length
      }),
      headers: computed((): Array<BaseHeaderIF> => {
        switch (localState.searchType) {
          case UIMHRSearchTypes.MHROWNER_NAME:
            return props.isReviewMode ? mhSearchNameHeadersReview : mhSearchNameHeaders
          case UIMHRSearchTypes.MHRORGANIZATION_NAME:
            return props.isReviewMode ? mhSearchNameHeadersReview : mhSearchNameHeaders
          case UIMHRSearchTypes.MHRMHR_NUMBER:
            return props.isReviewMode ? mhSearchMhrNumberHeadersReview : mhSearchMhrNumberHeaders
          case UIMHRSearchTypes.MHRSERIAL_NUMBER:
            return props.isReviewMode ? mhSearchSerialNumberHeadersReview : mhSearchSerialNumberHeaders
          default:
            return null
        }
      }),
      headerSlotLabel: computed((): string => {
        return localState.searchType === UIMHRSearchTypes.MHRMHR_NUMBER ? 'Registration Number' : localState.searchType
      }),
      ownerOrOrgHeader: computed((): string => {
        const found = getManufacturedHomeSearchResults.value?.results
        if (found) {
          return found[0]?.organizationName ? 'Organization' : 'Owner'
        } else return ''
      }),
      areAllSelected: computed((): boolean => {
        return localState.results?.every(result => result && result.selected === true)
      }),
      activeResults: computed((): any => {
        const selectedResults = cloneDeep(getSelectedManufacturedHomes.value)
        const baseResults = cloneDeep(getManufacturedHomeSearchResults.value?.results)
        // Map selected results with base results when user navigates back to edit selections further
        const activeResults = baseResults?.map(result => {
          const matchedResult = selectedResults?.find(({ id }) => id === result.id)
          return {
            ...result,
            ...(matchedResult && {
              selected: matchedResult.selected,
              includeLienInfo: matchedResult.includeLienInfo
            })
          }
        })
        // Get unique MHR Numbers with corresponding search type (Owner Name, Serial Num, etc.)
        localState.uniqueResults = uniqBy(selectedResults, UIMHRSearchTypeValues.MHRMHR_NUMBER)

        return props.isReviewMode
          ? selectedResults
          : activeResults
      }),
      isOwnerOrOrgSearch: computed((): boolean => {
        return [UIMHRSearchTypes.MHROWNER_NAME, UIMHRSearchTypes.MHRORGANIZATION_NAME].includes(localState.searchType)
      }),
      sortOptions: computed((): SortOptionIF => {
        return getMhrSearchResultSortOption.value
      })
    })

    const reviewAndConfirm = (): void => {
      router.push({ name: RouteNames.MHRSEARCH_CONFIRM })
    }

    // check if MHR number belongs to multiple results
    const hasMultipleSelections = (mhrNumber: string): boolean => {
      return filter(localState.results, { mhrNumber }).length > 1
    }

    // check if MHR number selection is first of
    const isFirstSelectionOfMultiples = (mhrNumber: string, id: number): boolean => {
      const multipleSelections = filter(localState.results, { mhrNumber })
      return multipleSelections.findIndex(item => item.id === id) === 0
    }

    // check if MHR number belongs to multiple selected results
    const hasMhrNumberSelected = (mhrNumber: string): boolean => {
      return filter(localState.results, { mhrNumber, selected: true }).length < 1
    }

    const getOwnerName = (item: ManufacturedHomeSearchResultIF): string => {
      if (item?.ownerName) {
        return `
          ${item.ownerName?.last},
          ${item.ownerName?.first}
          ${item.ownerName?.middle || item.ownerName?.second || ''}`
      } else if (item?.organizationName) {
        return item.organizationName
      } else return '-'
    }

    const getOwnerCount = (item: ManufacturedHomeSearchResultIF): string => {
      const count = item.activeCount + item.exemptCount + item.historicalCount
      return count > 1 ? `(${count})` : ''
    }
    const getItemClass = (item: ManufacturedHomeSearchResultIF): string => {
      let rowClass = ''
      if (props.isReviewMode) {
        const searchType = UIMHRSearchTypeMap[localState.searchType] // serialNumber, ownerName, etc.
        // get an array of search results based on its 'searchType'
        // check index of item, if its 0 then it's a unique entry, otherwise the rest are duplicates
        rowClass = localState.groupedResults[item.mhrNumber]
          .findIndex(group => group[searchType] === item[searchType]) === 0
          ? 'unique-reg-num' // only the first ManufacturedHomeSearchResultIF from the group will be unique
          : 'duplicate-reg-num'
      }
      return item.selected && !props.isReviewMode ? 'selected' : rowClass
    }

    const onSelectionCheckboxClick = (item: ManufacturedHomeSearchResultIF): void => {
      // will set same selected state for all of the results within same group (results with unique mhrNumber)
      const selectedState = item.selected as boolean
      // filter unique results based on mhrNumber
      filter(localState.results, { mhrNumber: item.mhrNumber })
        .forEach((result: ManufacturedHomeSearchResultIF) => {
          // set selected for each result
          result.selected = !selectedState
          if (!result.selected) {
            result.includeLienInfo = false
          }
        })
    }

    const setIncludeLienInfo = (item: ManufacturedHomeSearchResultIF): void => {
      filter(localState.results, { mhrNumber: item.mhrNumber })
      .forEach((result: ManufacturedHomeSearchResultIF) => {
        result.includeLienInfo = !result.includeLienInfo
      })
    }
    const getOwnerStatus = (ownerStatus: string): string => {
      if (ownerStatus === 'PREVIOUS') {
        if (ownerStatus === 'PREVIOUS') return 'HISTORICAL'
        else return ownerStatus
      } else return ''
    }

    // return adaptive text for owner status count(s)
    const getOwnerStatusText = (item: ManufacturedHomeSearchResultIF): string => {
      let returnText = ''
      if (item.activeCount > 0) {
        returnText += 'ACTIVE'
        if (item.activeCount > 1) returnText += ` (${item.activeCount})`
        hasMultipleStatus(item) ? returnText += ',\n' : returnText += '\n'
      }
      if (item.exemptCount > 0) {
        returnText += 'EXEMPT'
        if (item.exemptCount > 1) returnText += ` (${item.exemptCount})`
        hasMultipleStatus(item) ? returnText += ',\n' : returnText += '\n'
      }
      if (item.historicalCount > 0) {
        returnText += 'HISTORICAL'
        if (item.historicalCount > 1) returnText += ` (${item.historicalCount})`
      }
      return returnText
    }

    const hasMultipleStatus = (item: ManufacturedHomeSearchResultIF): boolean => {
      return (item.activeCount > 0 && item.exemptCount > 0) ||
        (item.activeCount > 0 && item.historicalCount > 0) ||
        (item.exemptCount > 0 && item.historicalCount > 0)
    }

    const noSelectedOwner = (item: ManufacturedHomeSearchResultIF): boolean => {
      let filteredResults = localState.results?.filter(result => result.mhrNumber === item.mhrNumber)
      filteredResults = filteredResults.filter(result => result.selected)
      return filteredResults.length < 1
    }

    const updateFolioOrReference = (folioOrReference: string): void => {
      setFolioOrReferenceNumber(folioOrReference)
    }

    const sortTable = (header: string, sortable: boolean) => {
      if (!sortable) { return }
      const isAsc = header === localState.sortOptions.sortBy 
                              ? !localState.sortOptions.isAsc
                              : false
      localState.results = orderBy(localState.results, header, isAsc ? 'asc' : 'desc')
      setMhrSearchResultSortOption({
          sortBy: header, 
          isAsc: isAsc
        })
    }

    onMounted(async () => {
      const resp = getManufacturedHomeSearchResults.value
      if (!resp) goToDash()
      localState.searchValue = resp?.searchQuery?.criteria.value || getOwnerName(resp?.searchQuery?.criteria)
      localState.searched = true
      localState.searchType = getSearchedType.value?.searchTypeUI || ''
      localState.results = localState.activeResults
      localState.results = localState.results?.map(result => {
        // includeLienInfo needs to be initialized because it doesn't exist in the DB/results response
        return result.includeLienInfo !== true ? { ...result, includeLienInfo: false } : result
      })

      if (props.isReviewMode) {
        let sortedResults
        if (localState.sortOptions.sortBy === '') {
          sortedResults = sortBy(localState.results, UIMHRSearchTypeValues.MHRMHR_NUMBER)
          setMhrSearchResultSortOption({
            sortBy: UIMHRSearchTypeValues.MHRMHR_NUMBER,
            isAsc: true
          })
        } else {
          sortedResults = localState.results
        }
        localState.groupedResults = groupBy(localState.results, UIMHRSearchTypeValues.MHRMHR_NUMBER)
      }

      localState.totalResultsLength = resp.totalResultsSize
      if (localState.searchType === UIMHRSearchTypes.MHRMHR_NUMBER && localState.totalResultsLength === 1) {
        // Select search result if an MHR Number Search and search results equals 1.
        localState.results = localState.results.map(result => ({ ...result, selected: true }))
      }
    })

    watch(() => localState.results, (): void => {
      const selectedManufacturedHomes = cloneDeep(localState.results?.filter(result => result.selected === true))
      setSelectedManufacturedHomes(selectedManufacturedHomes)
    }, { deep: true })

    watch(() => localState.selectedLiensLength, (): void => {
      if (localState.selectedLiensLength < localState.selectedMatchesLength) {
        localState.selectAllLien = false
      }
    })

    watch(() => localState.selectAll, (val: boolean): void => {
      localState.results = localState.results.map(result => ({ ...result, selected: val }))
      if (val && localState.selectAllLien) {
        localState.results = localState.results.map(result => ({ ...result, includeLienInfo: val }))
      }
      if (!val) {
        localState.results = localState.results.map(result => ({ ...result, includeLienInfo: val }))
      }
    })

    watch(() => localState.selectAllLien, (val: boolean): void => {
      filter(localState.results, 'selected').forEach(result => {
        result.includeLienInfo = val
      })
    })

    return {
      UIMHRSearchTypes,
      reviewAndConfirm,
      hasMultipleSelections,
      isFirstSelectionOfMultiples,
      hasMhrNumberSelected,
      getOwnerName,
      getOwnerStatus,
      noSelectedOwner,
      getOwnerCount,
      getOwnerStatusText,
      hasMultipleStatus,
      updateFolioOrReference,
      getItemClass,
      onSelectionCheckboxClick,
      sortTable,
      setIncludeLienInfo,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

th {
  padding-bottom: 10px !important;
}

.header-checkbox {
  :deep(.v-selection-control .v-label) {
    color: $gray9;
    font-size: 0.875rem;
    font-weight: bold;
  }
}

:deep(.v-selection-control .v-label) {
  color: $gray7;
  font-size: 0.875rem;
  align-items: flex-start;
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

:deep(.v-selection-control__input>.v-icon) {
  color: $app-blue !important;
  align-items: flex-start;
}

:deep(.v-table__wrapper) {
  max-height: 550px;
}

:deep(.v-table>.v-table__wrapper>table>tbody>tr>td) {
  padding: 8px 16px;
  vertical-align: top !important;
}
:deep(.v-table>.v-table__wrapper>table>thead>tr>th) {
  vertical-align: top !important;
  box-shadow: inset 0 -3px 0 #dee2e6;
}

.no-border-bottom td {
  border-bottom: none !important;
}

.lien-col {
  min-width: 12rem;
}
:deep(.v-selection-control__input) {
  align-items: flex-start;
}
:deep(.v-selection-control) {
  align-items: flex-start;
}
.bg-lt-blue{
 background-color: $app-lt-blue; 
}
.search-sub-title{
  color: #212529;
}
</style>
