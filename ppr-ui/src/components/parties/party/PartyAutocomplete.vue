<template>
  <v-card
    id="party-search-auto-complete"
    v-click-outside="closeAutoComplete"
    class="pl-0 pr-2 auto-complete-card"
    flat
    elevation="5"
  >
    <v-row
      no-gutters
      justify="center"
      class="pl-2 pa-0"
    >
      <v-col
        class="no-gutters"
        cols="12"
      >
        <v-list
          v-if="autoCompleteItems && autoCompleteItems.length > 0"
          class="auto-complete-list"
        >
          <v-list-item
            v-for="(result, i) in autoCompleteItems"
            :key="i"
            v-model="autoCompleteSelected"
            :ripple="!isExistingSecuredParty(result.code, isRegisteringParty)"
            :class="
              [
                wasSelected(result),
                !isExistingSecuredParty(result.code, isRegisteringParty) ?
                  'auto-complete-item' : 'auto-complete-added-item'
              ]"
            :active-class="isExistingSecuredParty(result.code, isRegisteringParty) ? 'added-color' : ''"
            @mouseover="mouseOver = true"
            @mouseleave="mouseOver = false"
          >
            <v-row
              no-gutters
              class="auto-complete-row"
              :class="!mouseOver && wasSelected(result)"
            >
              <v-col
                cols="2"
                class="title-size"
              >
                {{ result.code }}
              </v-col>
              <v-col cols="8">
                <v-list-item-subtitle
                  :disabled="isExistingSecuredParty(result.code, isRegisteringParty)"
                  :class="{'auto-complete-added-item' : isExistingSecuredParty(result.code, isRegisteringParty)}"
                  @click="!isExistingSecuredParty(result.code, isRegisteringParty) && addResult(result, i)"
                >
                  <span class="title-size">{{ result.businessName }}</span>
                  <div class="mt-2">
                    {{ result.address.street }},
                    {{ result.address.city }}
                    {{ result.address.region }}
                    {{ getCountryName(result.address.country) }},
                    {{ result.address.postalCode }}
                  </div>
                </v-list-item-subtitle>
              </v-col>
              <v-col>
                <v-list-item-action
                  v-if="!isMhrPartySearch"
                  :disabled="isExistingSecuredParty(result.code, isRegisteringParty)"
                  class="auto-complete-action float-right mr-2 fs-14"
                >
                  <span
                    v-if="!resultAdded[i] && !isExistingSecuredParty(result.code, isRegisteringParty)"
                    @click="addResult(result, i)"
                  >
                    <v-icon class="icon-bump mt-n1">mdi-plus</v-icon>Add
                  </span>
                  <span
                    v-else
                    class="auto-complete-added"
                  >
                    <v-icon class="icon-bump auto-complete-added mt-n1">mdi-check</v-icon>Added
                  </span>
                </v-list-item-action>
              </v-col>
            </v-row>
          </v-list-item>
        </v-list>
        <v-list v-else>
          <v-list-item
            class="pt-0 pb-0 pl-1 auto-complete-item"
          >
            <v-list-item class="pt-2 pb-2">
              <v-list-item-subtitle>
                <v-row class="auto-complete-row">
                  <v-col
                    id="no-party-matches"
                    cols="12"
                    class="title-size"
                  >
                    No matches found. Check your name or number, or add a
                    {{ partyWord }} Party
                    that doesn't have a code.
                  </v-col>
                </v-row>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, computed } from 'vue'
import { useCountriesProvinces } from '@/composables/address/factories'
import { useSecuredParty } from '@/composables/parties'
import { ActionTypes } from '@/enums'
import { SearchPartyIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'PartyAutocomplete',
  props: {
    autoCompleteItems: {
      type: Array as () => Array<any>,
      default: () => []
    },
    isRegisteringParty: {
      type: Boolean,
      default: false
    },
    isMhrPartySearch: {
      type: Boolean,
      default: false
    }
  },
  emits: ['closeAutoComplete', 'selectItem'],
  setup (props, { emit }) {
    const { addSecuredParty, setRegisteringParty, isExistingSecuredParty } = useSecuredParty()
    const countryProvincesHelpers = useCountriesProvinces()
    const localState = reactive({
      searchValue: '',
      autoCompleteSelected: -1,
      resultAdded: [],
      selectedCode: null,
      mouseOver: false,
      partyWord: computed((): string => props.isRegisteringParty
        ? 'Registering'
        : 'Secured')
    })

    const wasSelected = (val: SearchPartyIF) => {
      return localState.selectedCode === val.code ? 'was-selected' : ''
    }

    const addResult = (party: SearchPartyIF, resultIndex) => {
      localState.resultAdded[resultIndex] = true
      const newParty: PartyIF = {
        code: party.code,
        businessName: party.businessName,
        emailAddress: party.emailAddress || '',
        address: party.address,
        personName: { first: '', middle: '', last: '' },
        contact: { ...party.contact }
      }

      if (props.isRegisteringParty) {
        newParty.action = ActionTypes.EDITED
        setRegisteringParty(newParty)
      } else if (props.isMhrPartySearch) {
        localState.selectedCode = newParty.code
      } else {
        addSecuredParty(newParty)
      }

      emit('selectItem', newParty)
      closeAutoComplete()
    }

    const closeAutoComplete = () => {
      emit('closeAutoComplete')
    }

    return {
      addResult,
      closeAutoComplete,
      isExistingSecuredParty,
      wasSelected,
      ...countryProvincesHelpers,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
//.auto-complete-item {
//  min-height: 0;
//}
//
.auto-complete-item:hover {
  cursor: pointer;
  color: $primary-blue !important;
  background-color: $gray1 !important;
}
.v-list-item {
  :hover {
    color: $primary-blue !important;
  }
}
.v-list-item-subtitle {
  color: $gray7;
  min-height: 50px;
  cursor: pointer;
  overflow: unset;
}
//.added-color {
//  color : $gray7 !important;
//}
//
//.auto-complete-added-item:hover {
//  background-color: $gray1 !important;
//}
//
//.auto-complete-added-item:hover .auto-complete-row{
//  color: $gray7 !important;
//}
//
//.auto-complete-item[aria-selected='true'] {
//  color: $primary-blue !important;
//  background-color: $blueSelected !important;
//}
//
//.auto-complete-item:focus {
//  background-color: $gray3 !important;
//}
//
//@media (min-width: 960px) {
//  .auto-complete-card {
//    width: 960px;
//  }
//}
//
//.auto-complete-card {
//  position: absolute;
//  z-index: 3;
//  margin-left: 20px;
//}
//.auto-complete-row {
//  width: 35rem;
//  color: $gray7 !important;
//}
//
//.was-selected {
//  background-color: $blueSelected;
//  color: $primary-blue !important;
//}
//
//.auto-complete-row:hover {
//  color: $primary-blue !important;
//}
//
.auto-complete-list {
  max-height: 450px;
}

//.auto-complete-action {
//  width: 150px;
//  flex-direction: row;
//  justify-content: flex-end;
//  font-size: 0.875rem;
//}
//.close-btn-row {
//  height: 1rem;
//}
//
//.title-size {
//  font-size: 1rem;
//}
//
//.icon-bump {
//  margin-bottom: 3px;
//}
</style>
