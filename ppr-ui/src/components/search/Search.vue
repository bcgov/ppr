<template>
  <v-container fluid no-gutters>
    <v-row no-gutters>
      <v-col cols="3">
        <v-select id="search-type-select"
                  :error-messages="categoryMessage ? categoryMessage : ''"
                  filled
                  :items="searchTypes"
                  item-disabled="selectDisabled"
                  item-text="searchTypeUI"
                  :label="selectedSearchType ? '' : searchTypeLabel"
                  return-object
                  v-model="selectedSearchType">
        </v-select>
      </v-col>
      <v-col cols="7" class="pl-3">
        <v-tooltip content-class="bottom-tooltip"
                   bottom :open-on-hover="false"
                   :disabled="!searchPopUp"
                   transition="fade-transition"
                   :value="showSearchPopUp && searchPopUp">
          <template v-slot:activator="scope" & v-on="scope.on">
            <v-text-field :error-messages="searchMessage ? searchMessage : ''"
                          autocomplete="off"
                          :disabled="!selectedSearchType"
                          filled
                          :hint="searchHint"
                          :hide-details="hideDetails"
                          persistent-hint
                          :placeholder="selectedSearchType ? selectedSearchType.textLabel: 'Select a category first'"
                          v-model="searchValue">
            </v-text-field>
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
      <v-col cols="2" class="pl-3 pt-3">
        <v-row no-gutters>
          <v-btn id="search-btn" @click="searchAction">
            Search
            <v-icon right>mdi-magnify</v-icon>
          </v-btn>
        </v-row>
        <v-row no-gutters class="pl-1">
          <span id="search-btn-info">
            Each search incurs a fee
          </span>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'

import { validateSearchAction, validateSearchRealTime, PPRApiHelper } from '@/utils'
import { SearchTypes } from '@/resources'
import {
  SearchCriteriaIF, // eslint-disable-line no-unused-vars
  SearchResponseIF, // eslint-disable-line no-unused-vars
  SearchTypeIF, // eslint-disable-line no-unused-vars
  SearchValidationIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { UISearchTypes } from '@/enums'
// won't render properly from @/components/search
import AutoComplete from '@/components/search/AutoComplete.vue'

export default defineComponent({
  components: {
    AutoComplete
  },
  props: {
    defaultSelectedSearchType: {
      type: Object as () => SearchTypeIF
    },
    defaultSearchValue: {
      type: String
    }
  },
  setup (props, { emit }) {
    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      hideDetails: false,
      searchTypes: SearchTypes,
      searchValue: props.defaultSearchValue,
      searchTypeLabel: 'Select a search category',
      selectedSearchType: props.defaultSelectedSearchType,
      showSearchPopUp: true,
      validations: Object as SearchValidationIF,
      categoryMessage: computed((): string => {
        return localState.validations?.category?.message || ''
      }),
      searchMessage: computed((): string => {
        return localState.validations?.searchValue?.message || ''
      }),
      searchHint: computed((): string => {
        if (localState.searchMessage) return ''
        else return localState.selectedSearchType?.hints?.searchValue || ''
      }),
      searchPopUp: computed((): Array<string> | boolean => {
        return localState.validations?.searchValue?.popUp || false
      })
    })
    const getSearchApiParams = (): SearchCriteriaIF => {
      let cleanedSearchValue = localState.searchValue?.trim()
      if (localState.selectedSearchType.searchTypeUI === UISearchTypes.AIRCRAFT) {
        // replaceAll fails in jest so use regex
        const dash = /-/g
        cleanedSearchValue = cleanedSearchValue?.replace(dash, '')
      }
      return {
        type: localState.selectedSearchType.searchTypeAPI,
        criteria: {
          value: cleanedSearchValue
        }
      }
    }
    const searchAction = async () => {
      localState.validations = validateSearchAction(localState)
      if (localState.validations) return
      else emit('search-data', null) // clear any current results
      const apiHelper = new PPRApiHelper()
      const resp: SearchResponseIF = await apiHelper.search(getSearchApiParams())
      if (resp?.errors) emit('search-error', resp.errors)
      else emit('search-data', resp)
    }
    const setHideDetails = (hideDetails: boolean) => {
      localState.hideDetails = hideDetails
    }
    const setSearchValue = (searchValue: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValue
    }
    watch(() => localState.searchValue, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
      if (localState.selectedSearchType?.searchTypeUI === UISearchTypes.BUSINESS_DEBTOR &&
          localState.autoCompleteIsActive) {
        localState.autoCompleteSearchValue = val
      }
      // show autocomplete results there is a searchValue and if no error messages
      localState.autoCompleteIsActive = !localState.validations && val !== ''
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
      searchAction,
      setHideDetails,
      setSearchValue
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#search-btn {
  width: 9rem;
}
#search-btn-info {
  color: $gray8;
  font-size: 0.725rem;
}
::v-deep {
  .v-select-list {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .v-select__selections {
    line-height: 1.5rem !important;
  }
}
</style>
