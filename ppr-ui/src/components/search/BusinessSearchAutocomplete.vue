<template>
  <div class="auto-complete-wrapper">
    <v-card
      v-if="searchValue && searchValue.length >= 3 && !searching"
      id="business-search-autocomplete"
      class="auto-complete-card mt-n5"
      elevation="5"
    >
      <v-row
        no-gutters
        justify="center"
        class="px-0"
      >
        <v-col
          class="noGutters"
          cols="12"
        >
          <v-list
            v-if="autoCompleteResults && autoCompleteResults.length > 0"
            class="pt-0 results-list"
          >
            <v-list-item disabled>
              <v-row class="auto-complete-sticky-row">
                <v-col cols="24">
                  <p><span v-if="!isPPR">Active </span>B.C. Businesses:</p>
                </v-col>
              </v-row>
            </v-list-item>
            <v-list-item
              v-for="(result, i) in autoCompleteResults"
              :key="i"
              class="px-0"
              :class="{ 'disabled-item': isBusinessTypeSPGP(result.legalType) }"
            >
              <div
                v-if="isBusinessTypeSPGP(result.legalType)"
                class="info-tooltip"
              >
                <v-tooltip
                  location="right"
                  content-class="start-tooltip py-5"
                  :disabled="isPPR"
                >
                  <template #activator="{ props }">
                    <v-icon
                      v-bind="props"
                      class="mt-n1"
                      color="primary"
                    >
                      mdi-information-outline
                    </v-icon>
                  </template>
                  <p class="text-white">
                    Registered owners of a manufactured home cannot be a sole proprietorship, partnership or limited
                    partnership. The home must be registered in the name of the sole proprietor or partner (person or
                    business).
                  </p>
                </v-tooltip>
              </div>

              <v-list-item-subtitle
                class="auto-complete-item px-4 py-5"
                @mousedown="!isBusinessTypeSPGP(result.legalType) && selectResult(i)"
              >
                <v-row class="auto-complete-row">
                  <v-col cols="2">
                    {{ result.identifier }}
                  </v-col>
                  <v-col
                    cols="8"
                    class="org-name"
                  >
                    {{ result.name }}
                  </v-col>
                  <v-col
                    v-if="!isBusinessTypeSPGP(result.legalType)"
                    cols="2"
                    class="selectable"
                  >
                    Select
                  </v-col>
                </v-row>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <div
            v-else-if="hasNoMatches"
            id="no-party-matches"
            class="pa-5"
          >
            <p class="auto-complete-sticky-row">
              <span v-if="!isPPR">Active </span>B.C. Businesses:
            </p>
            <p class="mt-2">
              <strong>
                No <span v-if="!isPPR">active </span>B.C. businesses found.
              </strong>
            </p>
            <p class="mt-2">
              {{ nilSearchText }}
            </p>
          </div>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch, computed } from 'vue'
import type { SearchResponseI } from '@/interfaces'
import { useSearch } from '@/composables/useSearch'
import { BusinessTypes } from '@/enums/business-types'
import { debounce } from 'lodash'
import { sanitizeName } from '@/utils/utilities'

export default defineComponent({
  name: 'BusinessSearchAutocomplete',
  props: {
    setAutoCompleteIsActive: {
      type: Boolean
    },
    searchValue: {
      type: String,
      default: ''
    },
    showDropdown: {
      type: Boolean
    },
    isPPR: {
      type: Boolean,
      default: false
    },
    nilSearchText: {
      type: String,
      default: 'Ensure you have entered the correct, full legal name of the organization before entering the phone' +
          ' number and mailing address.'
    }
  },
  emits: ['searchValue', 'searching'],
  setup (props, { emit }) {
    const { searchBusiness } = useSearch()

    const localState = reactive({
      autoCompleteIsActive: props.setAutoCompleteIsActive,
      autoCompleteResults: null,
      autoCompleteSelected: null,
      searching: false,
      isSearchResultSelected: false,
      hasNoMatches: computed(
        (): boolean =>
          !localState.isSearchResultSelected &&
          localState.autoCompleteIsActive &&
          !localState.searching &&
          localState.autoCompleteResults &&
          localState.autoCompleteResults.length === 0
      )
    })

    const updateAutoCompleteResults = async (searchValue: string) => {
      localState.searching = true
      const response: SearchResponseI = await searchBusiness(searchValue, props.isPPR)
      // check if results are still relevant before updating list
      if (searchValue === props.searchValue && response?.searchResults?.results) {
        localState.autoCompleteResults = response.searchResults.results
      }
      localState.searching = false
    }

    const isBusinessTypeSPGP = (businessType: BusinessTypes): boolean => {
      // include all business types for PPR business searches
      return [BusinessTypes.GENERAL_PARTNERSHIP, BusinessTypes.SOLE_PROPRIETOR].includes(businessType) && !props.isPPR
    }

    const selectResult = (resultIndex: number) => {
      if (resultIndex >= 0) {
        console.log('Pre Sanitized Name: ', localState.autoCompleteResults[resultIndex]?.name)
        const searchValue = sanitizeName(localState.autoCompleteResults[resultIndex]?.name)
        console.log('Post Sanitized Name: ',  searchValue)

        localState.autoCompleteIsActive = false
        localState.isSearchResultSelected = true
        emit('searchValue', searchValue)
      }
    }

    watch(
      () => localState.autoCompleteIsActive,
      (val: boolean) => {
        if (!val) localState.autoCompleteResults = null
      }
    )
    watch(
      () => props.setAutoCompleteIsActive,
      (val: boolean) => {
        localState.autoCompleteIsActive = val
      }
    )
    watch(
      () => props.searchValue,
      debounce((val: string) => {
        if (localState.autoCompleteIsActive) {
          updateAutoCompleteResults(val)
          localState.isSearchResultSelected = false
        }
      }, 1000) // add one-second delay before triggering the search, as per UXA
    )
    watch(
      () => localState.searching,
      (val: boolean) => {
        emit('searching', val)
      }
    )

    return {
      selectResult,
      isBusinessTypeSPGP,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.auto-complete-wrapper {
  position: relative;
  padding: 0;
}

.auto-complete-item {
  min-height: 0;
}

strong, p {
  color: $gray7;
}

.auto-complete-sticky-row {
  color: $gray7;
  font-size: 14px;
}
.auto-complete-row {
  color: $gray7;
  font-size: 16px;

  .org-name {
    text-overflow: ellipsis;
    overflow: hidden;
  }
}

.auto-complete-card {
  position: absolute;
  width: 100%;
  z-index: 3;
  p {
    white-space: pre-line;
  }

  .results-list {
    max-height: 400px;
    overflow-y: scroll;
  }
}
.auto-complete-row:hover {
  cursor: pointer;
  color: $primary-blue;
}

.auto-complete-item[aria-selected='true'] {
  color: $primary-blue;
}

.auto-complete-item:focus {
  background-color: $gray3;
}

.info-tooltip {
  position: relative;
  float: right;
  top: 15px;
  right: 40px;
  width: 0px;
}

.selectable {
  color: $primary-blue !important;
  text-align: right;
  font-size: 14px;
}

.disabled-item {
  opacity: 0.6;
  background-color: $gray1;
  cursor: default;
  :hover {
    color: $gray7;
  }
}
</style>
