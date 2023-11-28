<template>
  <v-container class="bg-white pa-0 ma-0">
    <!-- Table Header -->
    <section
      id="search-meta-info"
      class="px-6 pt-8"
    >
      <v-row noGutters>
        <p class="search-sub-title">
          {{ searchType }} - <b>"{{ searchValue }}"</b>
        </p>
      </v-row>
      <v-row
        v-if="searched && !isReviewMode"
        id="search-summary-info"
        class="result-info pt-6"
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
          class="pl-0"
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
              :defaultFolioNumber="folioNumber"
              @folioNumber="updateFolioOrReference($event)"
              @folioError="folioError = $event"
            />
            <v-btn
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
        class="result-info"
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
                  <!-- First Header -->
                  <!-- Search selection checkbox -->
                  <template v-if="index === 0 && !isReviewMode">
                    <v-tooltip
                      location="top"
                      contentClass="top-tooltip"
                      transition="fade-transition"
                    >
                      <template #activator="{ props }">
                        <span v-bind="props">
                          <v-checkbox
                            id="select-all-checkbox"
                            v-model="selectAll"
                            class="header-checkbox ma-0 pa-0"
                            hideDetails
                            :label="headerSlotLabel"
                          />
                        </span>
                      </template>
                      <div class="pt-2 pb-2">
                        Select this to include all manufactured homes.
                      </div>
                    </v-tooltip>
                  </template>

                  <!-- Last Header -->
                  <!-- Lien selection checkbox -->
                  <template v-else-if="index === 9 && !isReviewMode">
                    <v-checkbox
                      id="select-all-lien-checkbox"
                      v-model="selectAllLien"
                      class="header-checkbox ma-0 pa-0"
                      label="Include lien information for all selections"
                      :disabled="selectedMatchesLength === 0"
                      hideDetails
                    />
                  </template>

                  <!-- Standard Headers -->
                  <template v-else>
                    <span
                      v-if="header.value === 'ownerName'"
                      :class="index === 0 && 'pl-8'"
                    >
                      {{ ownerOrOrgHeader }} Name
                    </span>
                    <span
                      v-else-if="header.value === 'ownerStatus'"
                      :class="index === 0 && 'pl-8'"
                    >
                      {{ ownerOrOrgHeader }} Status
                    </span>
                    <span v-else>
                      {{ header.text }}
                    </span>
                  </template>
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
                  <td>
                    <v-checkbox
                      v-model="item.selected"
                      :label="isReviewMode ? getOwnerName(item) + ' ' + getOwnerCount(item) : getOwnerName(item) "
                      :ripple="false"
                      hideDetails
                      @click="onSelectionCheckboxClick(item)"
                    />
                  </td>
                  <template v-if="!isReviewMode">
                    <td>{{ getOwnerStatusText(item) }}</td>
                    <td>{{ item.mhrNumber }}</td>
                    <td>{{ item.status }}</td>
                    <td>{{ item.baseInformation.year || '-' }}</td>
                    <td>{{ item.baseInformation.make || '-' }}</td>
                    <td>{{ item.baseInformation.model || '-' }}</td>
                    <td>{{ item.homeLocation }}</td>
                    <td>{{ item.serialNumber }}</td>
                    <td class="lien-col">
                      <v-tooltip
                        location="top"
                        contentClass="top-tooltip"
                        transition="fade-transition"
                      >
                        <template #activator="{ props }">
                          <span v-bind="props">
                            <v-checkbox
                              v-model="item.includeLienInfo"
                              :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                              :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                              :ripple="false"
                              hideDetails
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
                  <template v-else>
                    <template v-if="hasMultipleSelections(item.mhrNumber)">
                      <template v-if="isFirstSelectionOfMultiples(item.mhrNumber, item.id)">
                        <td>
                          <v-tooltip
                            location="top"
                            contentClass="top-tooltip"
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
                          {{ item.baseInformation.year }} {{ item.baseInformation.make }}
                          {{ item.baseInformation.model }}
                        </td>
                        <td>{{ item.homeLocation }}</td>
                        <td>{{ item.serialNumber }}</td>
                        <td class="lien-col">
                          <v-tooltip
                            location="top"
                            contentClass="top-tooltip"
                            transition="fade-transition"
                          >
                            <template #activator="{ props }">
                              <span v-bind="props">
                                <v-checkbox
                                  v-model="item.includeLienInfo"
                                  :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                                  :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                                  :ripple="false"
                                  hideDetails
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
                        {{ item.baseInformation.year }} {{ item.baseInformation.make }}
                        {{ item.baseInformation.model }}
                      </td>
                      <td>{{ item.homeLocation }}</td>
                      <td>{{ item.serialNumber }}</td>
                      <td class="lien-col">
                        <v-tooltip
                          location="top"
                          contentClass="top-tooltip"
                          transition="fade-transition"
                        >
                          <template #activator="{ props }">
                            <span v-bind="props">
                              <v-checkbox
                                v-model="item.includeLienInfo"
                                :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                                :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                                :ripple="false"
                                hideDetails
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
                  <td v-if="hasMultipleSelections(item.mhrNumber) && isReviewMode">
                    <v-tooltip
                      location="top"
                      contentClass="top-tooltip"
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
                      :label="item.mhrNumber"
                      :ripple="false"
                      hideDetails
                      @click="onSelectionCheckboxClick(item)"
                    />
                  </td>
                  <template v-if="!isReviewMode">
                    <td>{{ item.status }}</td>
                    <td>{{ getOwnerName(item) }}</td>
                    <td>{{ getOwnerStatusText(item) }}</td>
                    <td>{{ item.baseInformation.year || '-' }}</td>
                    <td>{{ item.baseInformation.make || '-' }}</td>
                    <td>{{ item.baseInformation.model || '-' }}</td>
                    <td>{{ item.homeLocation }}</td>
                    <td>{{ item.serialNumber }}</td>
                    <td class="lien-col">
                      <v-tooltip
                        location="top"
                        contentClass="top-tooltip"
                        transition="fade-transition"
                      >
                        <template #activator="{ props }">
                          <span v-bind="props">
                            <v-checkbox
                              v-model="item.includeLienInfo"
                              :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                              :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                              :ripple="false"
                              hideDetails
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
                  <template v-else>
                    <td>{{ getOwnerName(item) }}</td>
                    <td>
                      {{ item.baseInformation.year }} {{ item.baseInformation.make }} {{ item.baseInformation.model }}
                    </td>
                    <td>{{ item.homeLocation }}</td>
                    <td>{{ item.serialNumber }}</td>
                    <td class="lien-col">
                      <v-tooltip
                        location="top"
                        contentClass="top-tooltip"
                        transition="fade-transition"
                      >
                        <template #activator="{ props }">
                          <span v-bind="props">
                            <v-checkbox
                              v-model="item.includeLienInfo"
                              :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                              :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                              :ripple="false"
                              hideDetails
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
                  <td :class="item.selected && !isReviewMode ? 'selected-row' : ''">
                    <v-checkbox
                      v-model="item.selected"
                      :label="item.activeCount > 1
                        ? `${item.serialNumber} (${item.activeCount})`
                        : `${item.serialNumber}`"
                      :ripple="false"
                      hideDetails
                      @click="onSelectionCheckboxClick(item)"
                    />
                  </td>
                  <template v-if="!isReviewMode">
                    <td>{{ item.mhrNumber }}</td>
                    <td>{{ item.status }}</td>
                    <td>{{ getOwnerName(item) }}</td>
                    <td>{{ getOwnerStatusText(item) }}</td>
                    <td>{{ item.baseInformation.year || '-' }}</td>
                    <td>{{ item.baseInformation.make || '-' }}</td>
                    <td>{{ item.baseInformation.model || '-' }}</td>
                    <td>{{ item.homeLocation }}</td>
                    <td class="lien-col">
                      <v-tooltip
                        location="top"
                        contentClass="top-tooltip"
                        transition="fade-transition"
                      >
                        <template #activator="{ props }">
                          <span v-bind="props">
                            <v-checkbox
                              v-model="item.includeLienInfo"
                              :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                              :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                              :ripple="false"
                              hideDetails
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
                  <template v-else>
                    <td class="font-weight-bold">
                      {{ item.mhrNumber }}
                    </td>
                    <td>{{ getOwnerName(item) }}</td>
                    <td>
                      {{ item.baseInformation.year }} {{ item.baseInformation.make }}
                      {{ item.baseInformation.model }}
                    </td>
                    <td>{{ item.homeLocation }}</td>
                    <td class="lien-col">
                      <v-tooltip
                        location="top"
                        contentClass="top-tooltip"
                        transition="fade-transition"
                      >
                        <template #activator="{ props }">
                          <span v-bind="props">
                            <v-checkbox
                              v-model="item.includeLienInfo"
                              :label="`${!isReviewMode ? 'Include lien' : 'Lien'} information`"
                              :disabled="isReviewMode ? hasMhrNumberSelected(item.mhrNumber) : !item.selected"
                              :ripple="false"
                              hideDetails
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
import { BaseHeaderIF, ManufacturedHomeSearchResultIF } from '@/interfaces'
import { FolioNumber } from '@/components/common'
import { RouteNames, UIMHRSearchTypeMap, UIMHRSearchTypes, UIMHRSearchTypeValues } from '@/enums'
import { cloneDeep, uniqBy, filter, sortBy, groupBy } from 'lodash'
import { storeToRefs } from 'pinia'
import { useNavigation } from '@/composables'

export default defineComponent({
  name: 'SearchedResultsMhr',
  components: {
    FolioNumber
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
      setFolioOrReferenceNumber
    } = useStore()
    const {
      // Getters
      getManufacturedHomeSearchResults,
      getFolioOrReferenceNumber,
      getSearchedType,
      getSelectedManufacturedHomes
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
      if (props.isReviewMode) {
        // for review-only mode, clicking on a search result checkbox
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
      } else {
        if (!item.selected) {
          item.includeLienInfo = false
        }
        if (item.selected && localState.selectAllLien) {
          item.includeLienInfo = true
        }
      }
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

    onMounted(async () => {
      const resp = getManufacturedHomeSearchResults.value
      if (!resp) goToDash()
      localState.searchValue = resp?.searchQuery.criteria.value || getOwnerName(resp?.searchQuery.criteria)
      localState.searched = true
      localState.searchType = getSearchedType.value?.searchTypeUI || ''
      localState.results = localState.activeResults
      localState.results = localState.results?.map(result => {
        // includeLienInfo needs to be initialized because it doesn't exist in the DB/results response
        return result.includeLienInfo !== true ? { ...result, includeLienInfo: false } : result
      })
      // sort the results on the Review screen
      if (props.isReviewMode) {
        const sortedResults = sortBy(localState.results, UIMHRSearchTypeValues.MHRMHR_NUMBER)
        localState.groupedResults = groupBy(sortedResults, UIMHRSearchTypeValues.MHRMHR_NUMBER)
        localState.results = sortedResults
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
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

th {
  vertical-align: middle !important;
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
}

:deep(.v-table__wrapper) {
  max-height: 550px;
}

:deep(.v-table>.v-table__wrapper>table>tbody>tr>td) {
  padding: 8px 16px;
}

.no-border-bottom td {
  border-bottom: none !important;
}

.lien-col {
  min-width: 12rem;
}
</style>
