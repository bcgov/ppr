<template>
  <v-card v-if="showAutoComplete" class="auto-complete-card" elevation="5">
    <v-row no-gutters justify="center">
      <v-col no-gutters cols="12">
        <v-list v-if="autoCompleteResults && autoCompleteResults.length > 0" class="pt-0">
          <v-list-item-group v-model="autoCompleteSelected">
            <v-list-item
              v-for="(result, i) in autoCompleteResults"
              :key="i"
              class="pt-0 pb-0 pl-3 auto-complete-item"
              :class="{ disabled: isSPGP(result.legalType) }"
              :disabled="isSPGP(result.legalType)"
            >
              <v-list-item-content class="px-3">
                <v-list-item-subtitle>
                  <v-row class="auto-complete-row">
                    <v-col cols="3">{{ result.identifier }}</v-col>
                    <v-col cols="8">{{ result.name }}</v-col>
                    <v-col cols="1">
                      <v-tooltip
                        v-if="isSPGP(result.legalType)"
                        right
                        nudge-right="3"
                        content-class="right-tooltip pa-5"
                        transition="fade-transition"
                      >
                        <template v-slot:activator="{ on }">
                          <v-icon class="mt-n1" color="primary" v-on="on">
                            mdi-information-outline
                          </v-icon>
                        </template>
                        Registered owners of a manufactured home cannot be a sole proprietorship, partnership or limited
                        partnership. The home must be registered in the name of the sole proprietor or partner (person
                        or business).
                      </v-tooltip>
                    </v-col>
                  </v-row>
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
        <v-list v-else-if="!isSearchResultSelected && showDropdown && !searching && autoCompleteResults.length === 0">
          <v-list-item class="auto-complete-item">
            <v-list-item-content class="px-2 pt-1 pb-0">
              <v-list-item-subtitle>
                <v-row class="auto-complete-row">
                  <v-col id="no-party-matches">
                    <p>
                      <strong>
                        No matches found.
                      </strong>
                    </p>
                    <p>
                      Ensure you have entered the correct, full legal name of the organization before entering the phone
                      number and mailing address.
                    </p>
                  </v-col>
                </v-row>
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { SearchResponseI } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useSearch } from '@/composables/useSearch'
import { BusinessTypes } from '@/enums/business-types'

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
    }
  },
  setup (props, { emit }) {
    const { searchBusiness } = useSearch()

    const localState = reactive({
      autoCompleteIsActive: props.setAutoCompleteIsActive,
      autoCompleteResults: [],
      autoCompleteSelected: null,
      showAutoComplete: computed((): boolean => props.searchValue.length >= 3),
      searching: false,
      isSearchResultSelected: false
    })

    const updateAutoCompleteResults = async (searchValue: string) => {
      localState.searching = true
      const response: SearchResponseI = await searchBusiness(searchValue)
      // check if results are still relevant before updating list
      if (searchValue === props.searchValue && response?.searchResults.results) {
        localState.autoCompleteResults = response?.searchResults.results
      }
      localState.searching = false
    }

    const isSPGP = (businessType: string): boolean => {
      return businessType === (BusinessTypes.GENERAL_PARTNERSHIP || BusinessTypes.SOLE_PROPRIETOR)
    }

    watch(
      () => localState.autoCompleteSelected,
      (val: number) => {
        if (val >= 0) {
          const searchValue = localState.autoCompleteResults[val]?.name
          localState.autoCompleteIsActive = false
          localState.isSearchResultSelected = true
          emit('search-value', searchValue)
        }
      }
    )
    watch(
      () => localState.autoCompleteIsActive,
      (val: boolean) => {
        if (!val) localState.autoCompleteResults = []
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
      (val: string) => {
        if (localState.autoCompleteIsActive) {
          updateAutoCompleteResults(val)
          localState.isSearchResultSelected = false
        }
      }
    )
    watch(
      () => localState.searching,
      (val: boolean) => {
        emit('searching', val)
      }
    )

    return {
      isSPGP,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#auto-complete-close-btn {
  color: $gray5 !important;
  background-color: transparent !important;
}
.auto-complete-item {
  min-height: 0;
}

.auto-complete-card {
  position: absolute;
  z-index: 3;
  margin-top: -25px;
  width: 70%;
  p {
    white-space: pre-line;
  }
}
.close-btn-row {
  height: 1rem;
}

.auto-complete-item:hover {
  color: $primary-blue !important;
  background-color: $gray1 !important;
}

.auto-complete-item[aria-selected='true'] {
  color: $primary-blue !important;
  background-color: $blueSelected !important;
}

.auto-complete-item:focus {
  background-color: $gray3 !important;
}

.auto-complete-row {
  width: 35rem;
  color: $gray7 !important;
}

.auto-complete-row:hover {
  color: $primary-blue !important;
}

.auto-complete-item.disabled {
  &:hover {
    background-color: #f1f3f5 !important;
  }

  .auto-complete-row {
    color: $gray7;
  }
}
</style>
