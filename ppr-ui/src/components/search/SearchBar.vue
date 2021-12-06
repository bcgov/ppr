<template>
  <v-container fluid no-gutters class="white pa-6">
    <confirmation-dialog
      :setDisplay="confirmationDialog"
      :setOptions="dialogOptions"
      :setSettingOption="settingOption"
      @proceed="searchAction($event)"
    />
    <staff-payment-dialog
      attach=""
      class="mt-10"
      :setDisplay="staffPaymentDialogDisplay"
      :setOptions="staffPaymentDialog"
      :setShowCertifiedCheckbox="true"
      @proceed="onStaffPaymentChanges($event)"
    />
    <v-row no-gutters class="pt-2">
      <v-col :class="[$style['search-info'], 'select-search-text']">
        <span>
          Select a search category and then enter a value to search.
        </span>
        <span v-if="!isStaffBcolReg">
          <span>
            Each search incurs a
          </span>
          <v-tooltip
            class="pa-2 pt-2"
            content-class="top-tooltip"
            top
            transition="fade-transition"
          >
            <template v-slot:activator="{ on, attrs }">
              <span v-bind="attrs" v-on="on" :class="$style['fee-info']"> fee of ${{ fee }}.</span>
            </template>
            <v-row no-gutters class="pt-2 pb-2">
              <span>
                Each search will incur a fee of ${{ fee }},
                including searches that return no results.
              </span>
            </v-row>
          </v-tooltip>
        </span>
      </v-col>
      <v-col v-if="!isStaffBcolReg && !isStaffSbc" align-self="end" cols="4">
        <folio-number :defaultFolioNumber="folioNumber" @folio-number="updateFolioNumber"/>
      </v-col>
      <v-col align-self="end" cols="1" class="pl-3"/>
    </v-row>
    <v-row no-gutters class="pt-1">
      <v-col class="ml-n6 pl-6" cols="4">
        <v-select
          id="search-select"
          class="search-bar-type-select"
          :error-messages="categoryMessage ? categoryMessage : ''"
          filled
          :items="searchTypes"
          item-disabled="selectDisabled"
          item-text="searchTypeUI"
          :label="selectedSearchType ? '' : searchTypeLabel"
          return-object
          v-model="selectedSearchType"
        >
          <template slot="item" slot-scope="data">
            <span :id="`search-bar-${data.item.searchTypeUI}`">
              {{ data.item.searchTypeUI }}
            </span>
          </template>
        </v-select>
      </v-col>
      <v-col v-if="!isIndividualDebtor" cols="7" class="pl-3">
        <v-tooltip content-class="bottom-tooltip"
                   bottom
                   :open-on-hover="false"
                   :disabled="!searchPopUp"
                   transition="fade-transition"
                   :value="showSearchPopUp && searchPopUp">
          <template v-slot:activator="scope" & v-on="scope.on">
            <v-text-field
              id="search-bar-field"
              class="search-bar-text-field"
              autocomplete="off"
              :disabled="!selectedSearchType"
              :error-messages="searchMessage ? searchMessage : ''"
              filled
              :hint="searchHint"
              :hide-details="hideDetails"
              persistent-hint
              :placeholder="selectedSearchType ? selectedSearchType.textLabel: 'Select a category first'"
              v-model="searchValue"/>
          </template>
          <v-row v-for="(line, index) in searchPopUp" :key="index" class="pt-2 pl-3">
            {{ line }}
          </v-row>
        </v-tooltip>
        <auto-complete :searchValue="autoCompleteSearchValue"
                       :setAutoCompleteIsActive="autoCompleteIsActive"
                       @search-value="setSearchValue"
                       @hide-details="setHideDetails">
        </auto-complete>
      </v-col>
      <v-col v-else cols="7" class="pl-3">
        <v-row no-gutters>
          <v-col cols="4">
            <v-text-field id="first-name-field"
                          autocomplete="off"
                          :error-messages="searchMessageFirst ? searchMessageFirst : ''"
                          filled
                          :hint="searchHintFirst"
                          persistent-hint
                          placeholder="First Name"
                          v-model="searchValueFirst"/>
          </v-col>
          <v-col cols="4" class="pl-3">
            <v-text-field id="second-name-field"
                          autocomplete="off"
                          :error-messages="searchMessageSecond ? searchMessageSecond : ''"
                          filled
                          :hint="searchHintSecond"
                          persistent-hint
                          placeholder="Middle Name (Optional)"
                          v-model="searchValueSecond"/>
          </v-col>
          <v-col cols="4" class="pl-3">
            <v-text-field id="last-name-field"
                          autocomplete="off"
                          :error-messages="searchMessageLast ? searchMessageLast : ''"
                          filled
                          :hint="searchHintLast"
                          persistent-hint
                          placeholder="Last Name"
                          v-model="searchValueLast"/>
          </v-col>
        </v-row>
      </v-col>
      <v-col class="pl-3 pt-2" style="width: 250px;">
        <v-row no-gutters>
          <v-btn :id="$style['search-btn']"
                 class="search-bar-btn primary mr-2"
                 :loading="searching"
                 @click="searchCheck">
            <v-icon>mdi-magnify</v-icon>
          </v-btn>

          <v-menu v-if="isStaffBcolReg" offset-y left nudge-bottom="4">
            <template v-slot:activator="{ on }">
              <v-btn v-on="on" :id="$style['client-search']" outlined class="down-btn" color="primary">
                <v-icon color="primary">mdi-menu-down</v-icon>
              </v-btn>
            </template>
            <v-list class="actions__more-actions">
              <v-list-item @click="clientSearch()">
                <v-list-item-subtitle>
                  <v-icon style="font-size: 18px;padding-bottom: 2px;">mdi-magnify</v-icon>
                  <span>
                    Client Search
                  </span>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-row>
        <v-row v-if="!isStaffBcolReg" no-gutters>
          <span :id="$style['search-btn-info']" class="pl-1 pt-2 fee-text">
            ${{ fee }} fee
          </span>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'

import { search, staffSearch, validateSearchAction, validateSearchRealTime } from '@/utils'
import { SearchTypes } from '@/resources'
import { paymentConfirmaionDialog, staffPaymentDialog } from '@/resources/dialogOptions'
import {
  DialogOptionsIF, // eslint-disable-line no-unused-vars
  IndividualNameIF, // eslint-disable-line no-unused-vars
  SearchCriteriaIF, // eslint-disable-line no-unused-vars
  SearchTypeIF, // eslint-disable-line no-unused-vars
  SearchValidationIF, // eslint-disable-line no-unused-vars
  UserSettingsIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { SettingOptions, UISearchTypes } from '@/enums'
// won't render properly from @/components/search
import AutoComplete from '@/components/search/AutoComplete.vue'
import { FolioNumber } from '@/components/common'
import { ConfirmationDialog, StaffPaymentDialog } from '@/components/dialogs'

export default defineComponent({
  components: {
    AutoComplete,
    ConfirmationDialog,
    StaffPaymentDialog,
    FolioNumber
  },
  props: {
    defaultDebtor: {
      type: Object as () => IndividualNameIF
    },
    defaultFolioNumber: {
      type: String,
      default: ''
    },
    defaultSelectedSearchType: {
      type: Object as () => SearchTypeIF
    },
    defaultSearchValue: {
      type: String
    }
  },
  setup (props, { emit }) {
    const { setSearching, setStaffPayment } = useActions<any>(['setSearching', 'setStaffPayment'])
    const {
      getUserSettings,
      isSearching,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc,
      isSearchCertified,
      getStaffPayment
    } = useGetters<any>([
      'getUserSettings',
      'isSearching',
      'isRoleStaffBcol',
      'isRoleStaffReg',
      'isRoleStaffSbc',
      'isSearchCertified',
      'getStaffPayment'
    ])
    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      confirmationDialog: false,
      folioNumber: props.defaultFolioNumber,
      hideDetails: false,
      searchTypes: SearchTypes,
      searchValue: props.defaultSearchValue,
      searchValueFirst: props.defaultDebtor?.first,
      searchValueSecond: props.defaultDebtor?.second,
      searchValueLast: props.defaultDebtor?.last,
      searchTypeLabel: 'Select a search category',
      selectedSearchType: props.defaultSelectedSearchType,
      settingOption: SettingOptions.PAYMENT_CONFIRMATION_DIALOG,
      showSearchPopUp: true,
      staffPaymentDialogDisplay: false,
      staffPaymentDialog: staffPaymentDialog,
      validations: Object as SearchValidationIF,
      categoryMessage: computed((): string => {
        return localState.validations?.category?.message || ''
      }),
      dialogOptions: computed((): DialogOptionsIF => {
        const options = { ...paymentConfirmaionDialog }
        options.text = options.text.replace('8.50', localState.fee)
        return options
      }),
      fee: computed((): string => {
        if (isRoleStaffSbc.value) return '10.00'
        return '8.50'
      }),
      isIndividualDebtor: computed((): boolean => {
        if (localState.selectedSearchType?.searchTypeUI === UISearchTypes.INDIVIDUAL_DEBTOR) {
          return true
        }
        return false
      }),
      isStaffBcolReg: computed((): boolean => {
        return isRoleStaffBcol.value || isRoleStaffReg.value
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
      searchPopUp: computed((): Array<string> | boolean => {
        return localState.validations?.searchValue?.popUp || false
      }),
      showConfirmationDialog: computed((): boolean => {
        // don't show confirmation dialog if bcol or reg staff
        if (localState.isStaffBcolReg) return false

        const settings: UserSettingsIF = getUserSettings.value
        return settings?.paymentConfirmationDialog
      })
    })

    const getCriteria = () => {
      if (localState.isIndividualDebtor) {
        const first = localState.searchValueFirst?.trim()
        const second = localState.searchValueSecond?.trim()
        const last = localState.searchValueLast?.trim()
        return { debtorName: { first: first, second: second, last: last } }
      } else if (localState.selectedSearchType.searchTypeUI === UISearchTypes.BUSINESS_DEBTOR) {
        return { debtorName: { business: localState.searchValue?.trim() } }
      } else {
        let cleanedSearchValue = localState.searchValue?.trim()
        if (localState.selectedSearchType.searchTypeUI === UISearchTypes.AIRCRAFT) {
          // replaceAll fails in jest so use regex
          const dash = /-/g
          cleanedSearchValue = cleanedSearchValue?.replace(dash, '')
        }
        return { value: cleanedSearchValue }
      }
    }
    const getSearchApiParams = (): SearchCriteriaIF => {
      return {
        type: localState.selectedSearchType.searchTypeAPI,
        criteria: getCriteria(),
        clientReferenceId: localState.folioNumber
      }
    }
    const searchAction = async (proceed: boolean) => {
      localState.confirmationDialog = false
      if (proceed) {
        setSearching(true)
        emit('search-data', null) // clear any current results
        let resp
        if (isRoleStaffReg.value) {
          resp = await staffSearch(
            getSearchApiParams(),
            getStaffPayment.value,
            isSearchCertified.value)
          setStaffPayment(null)
        } else {
          resp = await search(getSearchApiParams(), '')
        }
        if (resp?.error) emit('search-error', resp.error)
        else {
          emit('searched-type', localState.selectedSearchType)
          if (localState.isIndividualDebtor) {
            emit('debtor-name', {
              first: localState.searchValueFirst,
              second: localState.searchValueSecond,
              last: localState.searchValueLast
            })
          } else emit('searched-value', localState.searchValue)
          emit('search-data', resp)
        }
        setSearching(false)
      }
    }
    const searchCheck = async () => {
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
    const setSearchValue = (searchValue: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValue
    }
    const togglePaymentConfirmation = (showDialog: boolean) => {
      emit('togglePaymentDialog', showDialog)
    }
    const updateFolioNumber = (folioNumber: string) => {
      localState.folioNumber = folioNumber
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
      } else {
        localState.staffPaymentDialogDisplay = true
      }
    }

    watch(() => localState.searchValue, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
      if (localState.selectedSearchType?.searchTypeUI === UISearchTypes.BUSINESS_DEBTOR &&
          localState.autoCompleteIsActive) {
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
      if (val.searchTypeUI !== UISearchTypes.BUSINESS_DEBTOR) localState.autoCompleteIsActive = false
      else localState.autoCompleteIsActive = true
    })

    return {
      ...toRefs(localState),
      getSearchApiParams,
      onStaffPaymentChanges,
      searchAction,
      searchCheck,
      setHideDetails,
      setSearchValue,
      clientSearch,
      togglePaymentConfirmation,
      updateFolioNumber
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
#search-btn, #client-search {
  height: 2.85rem;
  min-width: 0 !important;
  width: 3rem;
}
#search-btn-info {
  color: $gray8;
  font-size: 0.725rem;
}
.search-info {
  color: $gray8;
  font-size: 0.875rem;
}
.search-title {
  color: $gray9;
  font-size: 1rem;
}
.fee-info {
  border-bottom: 1px dotted $gray9;
}
.folio-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  font-size: 0.825rem !important;
}
.folio-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.folio-close-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  position: absolute;
}
.folio-close-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.folio-edit-card {
  width: 15rem;
  position: absolute;
  z-index: 3;
}
.folio-header {
  color: $gray9;
}
.folio-info {
  color: $gray7;
  font-size: 0.875rem;
}
</style>
