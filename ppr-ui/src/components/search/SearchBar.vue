<template>
  <v-container class="bg-white px-6 py-6">
    <ConfirmationDialog
      :setDisplay="confirmationDialog"
      :setOptions="dialogOptions"
      :setSettingOption="settingOption"
      @proceed="searchAction"
    />
    <StaffPaymentDialog
      attach=""
      class="mt-10"
      :setDisplay="staffPaymentDialogDisplay"
      :setOptions="staffPaymentDialog"
      :setShowCertifiedCheckbox="true"
      @proceed="onStaffPaymentChanges($event)"
    />

    <!-- Intro and Folio -->
    <v-row
      noGutters
      class="py-2"
      align="center"
    >
      <v-col class="mt-n2">
        <p class="search-info">
          Select a search category and then enter a criteria to search.
        </p>
      </v-col>
      <v-col
        cols="3"
        :class="{ 'mr-16' : isRoleStaff }"
      >
        <FolioNumber
          class="mb-n2"
          :defaultFolioNumber="folioNumber"
          @folioNumber="updateFolioNumber"
          @folioError="folioError = $event"
        />
      </v-col>
    </v-row>

    <!-- Search Type Label -->
    <v-row
      noGutters
      class=" pt-n4 pb-4"
    >
      <v-col>
        <label
          v-if="typeOfSearch"
          class="search-type-label font-weight-bold"
          v-html="typeOfSearch"
        />
      </v-col>
    </v-row>

    <!-- Search Selector and Input Fields -->
    <v-row noGutters>
      <v-col class="search-selector-col mr-6">
        <SearchBarList
          :defaultSelectedSearchType="selectedSearchType"
          :defaultCategoryMessage="categoryMessage"
          @selected="returnSearchSelection($event)"
        />
      </v-col>

      <!-- Business Name Lookup -->
      <v-col
        v-if="isBusinessDebtor"
        :class="isRoleStaff ? 'staff-search-bar-field-col' : 'search-bar-field-col'"
      >
        <v-text-field
          id="txt-name-debtor"
          ref="debtorNameSearchField"
          v-model="searchValue"
          variant="filled"
          color="primary"
          label="Find or enter the Full Legal Name of the Business"
          persistentHint
          :hint="searchHint"
          :hideDetails="hideDetails"
          :clearable="showClear"
          :clearIcon="'mdi-close'"
          persistentClear
          :disabled="!selectedSearchType"
          :errorMessages="searchMessage ? searchMessage : ''"
          @click:clear="showClear = false"
        >
          <template #append-inner>
            <v-progress-circular
              v-if="loadingSearchResults"
              indeterminate
              color="primary"
              class="mx-3"
              :size="25"
              :width="3"
            />
          </template>
        </v-text-field>

        <BusinessSearchAutocomplete
          v-click-outside="setCloseAutoComplete"
          isPpr
          nilSearchText
          :searchValue="autoCompleteSearchValue"
          :setAutoCompleteIsActive="autoCompleteIsActive"
          @searchValue="setSearchValue"
          @searching="loadingSearchResults = $event"
        />
      </v-col>

      <v-col
        v-else-if="isMhrOrgSearch"
        :class="isRoleStaff ? 'staff-search-bar-field-col' : 'search-bar-field-col'"
      >
        <v-text-field
          id="txt-mhr-org-name"
          ref="mhrOrgNameRef"
          v-model="searchValue"
          variant="filled"
          color="primary"
          label="Enter an organization name"
          persistentHint
          persistentClear
          :hint="searchHint"
          :hideDetails="hideDetails"
          :clearable="showClear"
          :clearIcon="'mdi-close'"
          :disabled="!selectedSearchType"
          :errorMessages="searchMessage ? searchMessage : ''"
          @click:clear="showClear = false"
        >
          <template #append-inner>
            <v-progress-circular
              v-if="loadingSearchResults"
              indeterminate
              color="primary"
              class="mx-3"
              :size="25"
              :width="3"
            />
          </template>
        </v-text-field>

        <BusinessSearchAutocomplete
          v-click-outside="setCloseAutoComplete"
          nilSearchText
          isPpr
          :searchValue="autoCompleteSearchValue"
          :setAutoCompleteIsActive="autoCompleteIsActive"
          @searchValue="setSearchValue"
          @searching="loadingSearchResults = $event"
        />
      </v-col>

      <v-col
        v-else-if="!isIndividual"
        :class="isRoleStaff ? 'staff-search-bar-field-col' : 'search-bar-field-col'"
        class="tooltip-col"
      >
        <v-tooltip
          :model-value="showSearchPopUp"
          content-class="bottom-tooltip"
          location="bottom"
          transition="fade-transition"
          :open-on-hover="false"
        >
          <template #activator="{props}">
            <v-text-field
              id="search-bar-field"
              v-model="searchValue"
              v-bind="props"
              class="search-bar-text-field"
              autocomplete="off"
              :disabled="!selectedSearchType"
              :errorMessages="searchMessage ? searchMessage : ''"
              variant="filled"
              color="primary"
              :hint="searchHint"
              :hideDetails="hideDetails"
              persistentHint
              :label="selectedSearchType ? selectedSearchType.textLabel : 'Select a category first'"
              @enter="searchCheck()"
            />
          </template>
          <v-row
            v-for="(line, index) in searchPopUp"
            :key="index"
            class="pt-2 pl-3"
          >
            {{ line }}
          </v-row>
        </v-tooltip>
      </v-col>

      <v-col
        v-else
        :class="isRoleStaff ? 'staff-search-bar-field-col' : 'search-bar-field-col'"
      >
        <v-row noGutters>
          <v-col>
            <v-text-field
              id="first-name-field"
              v-model="searchValueFirst"
              :class="wrapClass"
              autocomplete="off"
              :errorMessages="searchMessageFirst ? searchMessageFirst : ''"
              variant="filled"
              color="primary"
              :hint="searchHintFirst"
              persistentHint
              :label="optionFirst"
              @keypress.enter="searchCheck()"
            />
          </v-col>
          <v-col class="px-2">
            <v-text-field
              id="second-name-field"
              v-model="searchValueSecond"
              autocomplete="off"
              :errorMessages="searchMessageSecond ? searchMessageSecond : ''"
              variant="filled"
              color="primary"
              :hint="searchHintSecond"
              persistentHint
              label="Middle Name (Optional)"
              @keypress.enter="searchCheck()"
            />
          </v-col>
          <v-col>
            <v-text-field
              id="last-name-field"
              v-model="searchValueLast"
              autocomplete="off"
              :errorMessages="searchMessageLast ? searchMessageLast : ''"
              variant="filled"
              color="primary"
              :hint="searchHintLast"
              persistentHint
              label="Last Name"
              @keypress.enter="searchCheck()"
            />
          </v-col>
        </v-row>
      </v-col>

      <!-- Search Submit Buttons -->
      <v-col class="pl-3 mt-1 search-btn-col">
        <v-btn
          id="search-btn"
          class="search-bar-btn bg-primary mr-3"
          :loading="searching"
          @click="searchCheck()"
        >
          <v-icon>mdi-magnify</v-icon>
        </v-btn>
        <v-menu
          v-if="(isStaffBcolReg || isRoleStaff) && !isStaffSbc"
          location="bottom right"
        >
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              id="client-search"
              variant="outlined"
              class="down-btn"
              color="primary"
              data-test-id="client-search-bar-btn"
            >
              <v-icon color="primary">
                mdi-menu-down
              </v-icon>
            </v-btn>
          </template>
          <v-list class="actions__more-actions">
            <v-list-item @click="clientSearch()">
              <v-list-item-subtitle class="fs-18">
                <v-icon>mdi-magnify</v-icon>
                Client Search
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
        <v-row
          v-if="showPprFeeHint"
          noGutters
        >
          <v-col>
            <p
              id="search-btn-info"
              class="fee-text fs-12"
            >
              ${{ fee }} fee
            </p>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <v-row noGutters>
      <v-col class="pt-1">
        <div
          v-if="showPprFeeHint || showMhrHint"
          class="ppr-mhr-info mt-5 mb-7"
        >
          <p class="fs-14">
            <v-icon size="20">
              mdi-information-outline
            </v-icon>
            <span
              v-if="showPprFeeHint"
              data-test-id="ppr-search-info"
            >
              Each Personal Property Registry search will incur a fee of ${{ fee }}, including searches that return
              no results.
            </span>
            <span
              v-else-if="showMhrHint"
              data-test-id="mhr-search-info"
            >
              You will have the option to include a Personal Property Registry lien / encumbrance search
              as part of your Manufactured Home Registry search.
            </span>
          </p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import _ from 'lodash'
import { mhrSearch, search, staffSearch, validateSearchAction, validateSearchRealTime } from '@/utils'
import { MHRSearchTypes, SearchTypes } from '@/resources'
import { paymentConfirmaionDialog, staffPaymentDialog } from '@/resources/dialogOptions'

import {
  DialogOptionsIF,
  IndividualNameIF,
  SearchCriteriaIF,
  SearchTypeIF,
  SearchValidationIF,
  UserSettingsIF
} from '@/interfaces'

import { APIMHRMapSearchTypes, APISearchTypes, SettingOptions } from '@/enums'
import SearchBarList from '@/components/search/SearchBarList.vue'
import BusinessSearchAutocomplete from '@/components/search/BusinessSearchAutocomplete.vue'
import { FolioNumber } from '@/components/common'
import { ConfirmationDialog, StaffPaymentDialog } from '@/components/dialogs'
import { useSearch } from '@/composables/useSearch'
import { storeToRefs } from 'pinia'

export default defineComponent({
  components: {
    BusinessSearchAutocomplete,
    ConfirmationDialog,
    StaffPaymentDialog,
    FolioNumber,
    SearchBarList
  },
  props: {
    defaultDebtor: {
      type: Object as () => IndividualNameIF,
      default: () => {}
    },
    defaultFolioNumber: {
      type: String,
      default: ''
    },
    defaultSelectedSearchType: {
      type: Object as () => SearchTypeIF,
      default: () => {}
    },
    defaultSearchValue: {
      type: String,
      default: ''
    },
    isNonBillable: {
      type: Boolean,
      default: false
    },
    serviceFee: {
      default: 1.50,
      type: Number || String
    }
  },
  emits: [
    'debtorName',
    'searchData',
    'searchError',
    'searchedType',
    'searchedValue',
    'togglePaymentDialog'
  ],
  setup (props, { emit }) {
    const {
      // Actions
      setIsStaffClientPayment,
      setSearching,
      setStaffPayment,
      setFolioOrReferenceNumber,
      setSelectedManufacturedHomes
    } = useStore()
    const {
      // Getters
      getUserSettings,
      isSearching,
      isRoleStaff,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc,
      isSearchCertified,
      getStaffPayment,
      hasPprEnabled,
      hasMhrEnabled
    } = storeToRefs(useStore())
    const { isMHRSearchType, isPPRSearchType, mapMhrSearchType } = useSearch()
    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      confirmationDialog: false,
      folioNumber: props.defaultFolioNumber,
      folioError: false,
      hideDetails: false,
      loadingSearchResults: false,
      showClear: false,
      searchValue: props.defaultSearchValue,
      searchValueFirst: props.defaultDebtor?.first,
      searchValueSecond: props.defaultDebtor?.second,
      searchValueLast: props.defaultDebtor?.last,
      selectedSearchType: props.defaultSelectedSearchType,
      settingOption: SettingOptions.PAYMENT_CONFIRMATION_DIALOG,
      staffPaymentDialogDisplay: false,
      staffPaymentDialog,
      validations: Object as SearchValidationIF,
      showSearchPopUp: computed((): boolean => {
        return localState.searchPopUp.length > 0
      }),
      categoryMessage: computed((): string => {
        return localState.validations?.category?.message || ''
      }),
      showPprFeeHint: computed((): boolean => {
        return !(isRoleStaffBcol.value || isRoleStaffReg.value) && ((hasPprEnabled.value && !hasMhrEnabled.value) ||
          isPPRSearchType(localState.selectedSearchType?.searchTypeAPI))
      }),
      showMhrHint: computed((): boolean => {
        return !(isRoleStaffBcol.value || isRoleStaffReg.value) && ((hasMhrEnabled.value && !hasPprEnabled.value) ||
          isMHRSearchType(localState.selectedSearchType?.searchTypeAPI))
      }),
      dialogOptions: computed((): DialogOptionsIF => {
        const options = { ...paymentConfirmaionDialog }
        options.text = options.text.replace('8.50', localState.fee)
        return options
      }),
      fee: computed((): string => {
        if (isRoleStaffSbc.value) return '10.00'
        if (props.isNonBillable) {
          const serviceFee = `${props.serviceFee}`
          if (serviceFee.includes('.')) {
            // the right side of the decimal
            const decimalStr = serviceFee.substring(serviceFee.indexOf('.') + 1)
            if (decimalStr.length === 2) return serviceFee
            // else add zero
            return serviceFee + '0'
          }
          // add decimal
          return serviceFee + '.00'
        }
        return '8.50'
      }),
      isIndividual: computed((): boolean => {
        return (localState.selectedSearchType?.searchTypeAPI === APISearchTypes.INDIVIDUAL_DEBTOR) ||
          (localState.selectedSearchType?.searchTypeAPI === APIMHRMapSearchTypes.MHROWNER_NAME)
      }),
      isBusinessDebtor: computed((): boolean => {
        return localState.selectedSearchType?.searchTypeAPI === APISearchTypes.BUSINESS_DEBTOR
      }),
      isMhrOrgSearch: computed((): boolean => {
        return localState.selectedSearchType?.searchTypeAPI === APIMHRMapSearchTypes.MHRORGANIZATION_NAME
      }),
      wrapClass: computed(() => {
        // Add wrap css class only to MHR Home Owner search fields
        if (localState.selectedSearchType?.searchTypeAPI !== APIMHRMapSearchTypes.MHROWNER_NAME) return ''
        return localState.searchMessageFirst || localState.searchMessageSecond ? 'hint-wrap' : 'hint-no-wrap'
      }),
      personalPropertySearchFee: computed((): string => {
        return localState.isRoleStaff || localState.isStaffSbc ? '10.00' : '8.50'
      }),
      manHomeSearchFee: computed((): string => {
        return localState.isRoleStaff || localState.isStaffSbc ? '10.00' : '7.00'
      }),
      comboSearchFee: computed((): string => {
        return localState.isRoleStaff || localState.isStaffSbc ? '15.00' : '12.00'
      }),
      isRoleStaff: computed((): boolean => {
        return isRoleStaff.value
      }),
      isStaffBcolReg: computed((): boolean => {
        return isRoleStaffBcol.value || isRoleStaffReg.value
      }),
      isRoleStaffReg: computed((): boolean => {
        return isRoleStaffReg.value
      }),
      isStaffSbc: computed((): boolean => {
        return isRoleStaffSbc.value
      }),
      searching: computed((): boolean => {
        return isSearching.value
      }),
      searchMessage: computed((): string => {
        return localState.validations?.searchValue?.message || ''
      }),
      optionFirst: computed((): string => {
        return isRoleStaffReg.value && isMHRSearchType(localState.selectedSearchType?.searchTypeAPI)
          ? 'First Name (Optional)'
          : 'First Name'
      }),
      typeOfSearch: computed((): string => {
        // only show the type of search if authorized to both types
        if (((hasPprEnabled.value && hasMhrEnabled.value) || isRoleStaff.value || localState.isStaffBcolReg)) {
          if (localState.selectedSearchType) {
            if (isPPRSearchType(localState.selectedSearchType.searchTypeAPI)) {
              return '<i aria-hidden="true" class="v-icon notranslate menu-icon mdi ' + SearchTypes[0].icon +
                '"></i>' + SearchTypes[0].textLabel
            }
            if (isMHRSearchType(localState.selectedSearchType.searchTypeAPI)) {
              return '<i aria-hidden="true" class="v-icon notranslate menu-icon mdi ' + MHRSearchTypes[0].icon +
                '"></i>' + MHRSearchTypes[0].textLabel
            }
          }
        }
        return ''
      }),
      searchMessageFirst: computed((): string => {
        return localState.validations?.searchValue?.messageFirst || ''
      }),
      searchMessageSecond: computed((): string => {
        return localState.validations?.searchValue?.messageSecond || ''
      }),
      searchMessageLast: computed((): string => {
        return localState.validations?.searchValue?.messageLast || ''
      }),
      searchHint: computed((): string => {
        if (localState.searchMessage) return ''
        else return localState.selectedSearchType?.hints?.searchValue || ''
      }),
      searchHintFirst: computed((): string => {
        if (localState.searchMessageFirst) return ''
        else return localState.selectedSearchType?.hints?.searchValueFirst || ''
      }),
      searchHintSecond: computed((): string => {
        if (localState.searchMessageSecond) return ''
        else return localState.selectedSearchType?.hints?.searchValueSecond || ''
      }),
      searchHintLast: computed((): string => {
        if (localState.searchMessageLast) return ''
        else return localState.selectedSearchType?.hints?.searchValueLast || ''
      }),
      searchPopUp: computed((): Array<string> => {
        return localState.validations?.searchValue?.popUp || []
      }),
      showConfirmationDialog: computed((): boolean => {
        // don't show confirmation dialog if bcol or reg staff
        if (localState.isStaffBcolReg || isMHRSearchType(localState.selectedSearchType?.searchTypeAPI)) return false

        const settings: UserSettingsIF = getUserSettings.value
        return settings?.paymentConfirmationDialog
      })
    })

    /**
     * the function take a string and remove all the zero-width space characters
     * and replace all smart quotes (closing single quote also used as apostrophe) to its corresponding straight quotes
     * @param dirtyValue the string we want to clean
     * @return the cleaned up string
     */
    const cleanUpInput = (dirtyValue: string | undefined) => {
      if (dirtyValue === undefined) {
        return undefined
      }
      return dirtyValue
        .trim()
        .replaceAll(/[\u200B-\u200D\uFEFF\u200E\u200F]|(?:&#x200E;)/g, '')
        .replaceAll(/[\u2018\u2019]/g, '\'')
        .replaceAll(/[\u201C\u201D]/g, '"')
    }

    const getCriteria = () => {
      if (localState.isIndividual) {
        const first = cleanUpInput(localState.searchValueFirst)
        const second = cleanUpInput(localState.searchValueSecond) // Also used for middle name in MHR searches
        const last = cleanUpInput(localState.searchValueLast)

        if (isPPRSearchType(localState.selectedSearchType.searchTypeAPI)) {
          return { debtorName: { first, second, last } }
        }
        if (isMHRSearchType(localState.selectedSearchType.searchTypeAPI)) {
          return { ownerName: { first, middle: second, last } }
        }
      } else if (localState.selectedSearchType.searchTypeAPI === APISearchTypes.BUSINESS_DEBTOR) {
        return { debtorName: { business: cleanUpInput(localState.searchValue) } }
      } else {
        const cleanedSearchValue = cleanUpInput(localState.searchValue)
        return { value: cleanedSearchValue }
      }
    }
    const getSearchApiParams = (): SearchCriteriaIF => {
      const searchTypeApi = localState.selectedSearchType.searchTypeAPI
      const type = isMHRSearchType(searchTypeApi) ? mapMhrSearchType(searchTypeApi) : searchTypeApi

      return {
        type,
        criteria: getCriteria(),
        clientReferenceId: localState.folioNumber
      }
    }
    const searchAction = _.throttle(async (proceed: boolean) => {
      localState.confirmationDialog = false
      if (proceed) {
        // pad mhr number with 0s
        if ((localState.selectedSearchType?.searchTypeAPI === APISearchTypes.MHR_NUMBER) ||
          (localState.selectedSearchType?.searchTypeAPI === APIMHRMapSearchTypes.MHRMHR_NUMBER)) {
          localState.searchValue.padStart(6, '0')
        }
        setSearching(true)
        emit('searchData', null) // clear any current results
        let resp
        if (isRoleStaffReg.value) {
          if (isPPRSearchType(localState.selectedSearchType?.searchTypeAPI)) {
            resp = await staffSearch(
              getSearchApiParams(),
              getStaffPayment.value,
              isSearchCertified.value)
            setStaffPayment(null)
          }
          if (isMHRSearchType(localState.selectedSearchType.searchTypeAPI)) {
            setSelectedManufacturedHomes([])
            setFolioOrReferenceNumber(localState.folioNumber)
            resp = await mhrSearch(getSearchApiParams(), '')
          }
        } else {
          if (isPPRSearchType(localState.selectedSearchType?.searchTypeAPI)) {
            resp = await search(getSearchApiParams(), '')
          }
          if (isMHRSearchType(localState.selectedSearchType.searchTypeAPI)) {
            // If SBC Staff - is always a search on clients behalf
            if (localState.isStaffSbc) setIsStaffClientPayment(true)

            setSelectedManufacturedHomes([])
            setFolioOrReferenceNumber(localState.folioNumber)
            resp = await mhrSearch(getSearchApiParams(), '')
          }
        }
        if (resp?.error) emit('searchError', resp.error)
        else {
          emit('searchedType', localState.selectedSearchType)
          if (localState.isIndividual) {
            emit('debtorName', {
              first: localState.searchValueFirst,
              second: localState.searchValueSecond,
              last: localState.searchValueLast
            })
          } else emit('searchedValue', localState.searchValue)
          emit('searchData', resp)
        }
        setSearching(false)
      }
    }, 2000, { trailing: false })
    const searchCheck = async () => {
      if (localState.folioError) {
        return
      }
      localState.validations = validateSearchAction(localState)
      if (localState.validations) {
        localState.autoCompleteIsActive = false
      } else if (localState.showConfirmationDialog) {
        localState.confirmationDialog = true
      } else {
        searchAction(true)
      }
    }
    const setHideDetails = (hideDetails: boolean) => {
      localState.hideDetails = hideDetails
    }
    const returnSearchSelection = (selection: SearchTypeIF) => {
      localState.selectedSearchType = selection
    }
    const setSearchValue = (searchValue: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValue
      localState.showClear = true
      if (document.getElementById('search-bar-field')) {
        document.getElementById('search-bar-field').focus()
      }
    }
    const togglePaymentConfirmation = (showDialog: boolean) => {
      emit('togglePaymentDialog', showDialog)
    }
    const updateFolioNumber = (folioNumber: string) => {
      localState.folioNumber = folioNumber
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    const onStaffPaymentChanges = (search: boolean): void => {
      if (search) {
        searchAction(true)
      }
      localState.staffPaymentDialogDisplay = false
    }

    const clientSearch = async () => {
      localState.validations = validateSearchAction(localState)
      if (localState.validations) {
        localState.autoCompleteIsActive = false
      } else if (isMHRSearchType(localState.selectedSearchType?.searchTypeAPI)) {
        setIsStaffClientPayment(true)
        searchAction(true)
      } else {
        localState.staffPaymentDialogDisplay = true
      }
    }

    watch(() => localState.searchValue, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
      if ((localState.isBusinessDebtor || localState.isMhrOrgSearch)) {
        localState.autoCompleteSearchValue = val
      }
      // show autocomplete results when there is a searchValue and if no error messages
      localState.autoCompleteIsActive = !localState.validations && val !== ''
    })
    watch(() => localState.searchValueFirst, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
    })
    watch(() => localState.searchValueSecond, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
    })
    watch(() => localState.searchValueLast, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
    })
    watch(() => localState.selectedSearchType, (val: SearchTypeIF) => {
      localState.validations = null
      localState.searchValue = null
      localState.autoCompleteIsActive = [APISearchTypes.BUSINESS_DEBTOR, APIMHRMapSearchTypes.MHRORGANIZATION_NAME]
        .includes(val.searchTypeAPI as APISearchTypes | APIMHRMapSearchTypes)
    })

    return {
      ...toRefs(localState),
      isMHRSearchType,
      getSearchApiParams,
      onStaffPaymentChanges,
      searchAction,
      searchCheck,
      setHideDetails,
      setSearchValue,
      setCloseAutoComplete,
      clientSearch,
      togglePaymentConfirmation,
      returnSearchSelection,
      updateFolioNumber
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

@media (min-width: 960px) {
  // To keep the inner content of cols adhering to the col width itself
  // we use min and max width instead of width.
  .search-selector-col {
    min-width: 400px;
    max-width: 400px;
  }
  .search-bar-field-col {
    min-width: 800px;
    max-width: 800px;
  }
  .staff-search-bar-field-col {
    min-width: 740px;
    max-width: 740px;
  }
}

:deep(.search-type-label .v-icon) {
  margin-top: -6px;
  font-size: 24px;
}

#search-btn, #client-search {
  height: 2.85rem;
  min-width: 0 !important;
  width: 3rem;
}

:deep(.v-btn__loader) {
  margin-left: -3px;
}
</style>
