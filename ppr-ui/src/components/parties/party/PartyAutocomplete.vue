<template>
  <v-card
    v-if="autoCompleteIsActive"
    id="party-search-auto-complete"
    :class="['mt-1', $style['auto-complete-card']]"
    elevation="5"
    v-click-outside="closeAutoComplete"
  >
    <v-row no-gutters justify="center" class="pl-2">
      <v-col no-gutters cols="12">
        <v-list v-if="autoCompleteResults && autoCompleteResults.length > 0"
          :class="$style['auto-complete-list']" class="pt-0">
          <v-list-item-group v-model="autoCompleteSelected">
            <v-list-item
              v-for="(result, i) in autoCompleteResults"
              :key="i"
              :ripple="!isExistingSecuredParty(result.code)"
              :class="[
                'pt-0', 'pb-0', 'pl-1',
                $style[!isExistingSecuredParty(result.code) ? 'auto-complete-item' : 'auto-complete-added-item'],
                $style[wasSelected(result)]
              ]"
              :active-class="{'added-color' : isExistingSecuredParty(result.code)}"
              @mouseover="mouseOver = true"
              @mouseleave="mouseOver = false"
            >
              <v-list-item-content
                :disabled="isExistingSecuredParty(result.code)"
                :class="[
                  $style[isExistingSecuredParty(result.code) ? 'auto-complete-added-item' : ''], 'pt-2', 'pb-2'
                ]"
                @click="!isExistingSecuredParty(result.code) ? addResult(result, i) : ''"
              >
                <v-list-item-subtitle>
                  <v-row :class="[
                    $style['auto-complete-row'],
                    $style[mouseOver ? '' : wasSelected(result)]
                    ]
                  ">
                    <v-col cols="2" :class="$style['title-size']">
                      {{ result.code }}
                    </v-col>
                    <v-col cols="9"
                      ><span :class="$style['title-size']">{{ result.businessName }}</span>
                      <div class="mt-2">
                      {{ result.address.street }},
                      {{ result.address.city }}
                      {{ result.address.region }}
                      {{ getCountryName(result.address.country) }},
                      {{ result.address.postalCode }}
                      </div>
                    </v-col>
                  </v-row>
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action
                :disabled="isExistingSecuredParty(result.code)"
                v-if="!isMhrPartySearch"
                :class="[$style['auto-complete-action'], 'mt-n1']"
              >
                <span v-if="!resultAdded[i] && !isExistingSecuredParty(result.code)" @click="addResult(result, i)">
                  <v-icon :class="$style['icon-bump']">mdi-plus</v-icon>Add
                </span>
                <span class="auto-complete-added" v-else>
                  <v-icon :class="[$style['icon-bump'], 'auto-complete-added']">mdi-check</v-icon>Added
                </span>
              </v-list-item-action>
            </v-list-item>
          </v-list-item-group>
        </v-list>
        <v-list v-else-if="autoCompleteIsActive">
           <v-list-item
              :class="['pt-0', 'pb-0', 'pl-1', $style['auto-complete-item']]"
            >
              <v-list-item-content class="pt-2 pb-2">
                <v-list-item-subtitle>
                  <v-row :class="$style['auto-complete-row']">
                    <v-col cols="12" :class="$style['title-size']" id="no-party-matches">
                      No matches found. Check your name or number, or add a
                      {{ partyWord }} Party
                      that doesn't have a code.
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
// external libraries
import { defineComponent, reactive, toRefs, watch, computed } from '@vue/composition-api'
// local helpers / types / etc.
import { useCountriesProvinces } from '@/composables/address/factories'
import { useSecuredParty } from '@/components/parties/composables/useSecuredParty'
import { ActionTypes } from '@/enums'
import { SearchPartyIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useActions } from 'vuex-composition-helpers'

export default defineComponent({
  props: {
    autoCompleteItems: {
      type: Array,
      default: []
    },
    setAutoCompleteActive: {
      type: Boolean,
      default: false
    },
    setIsRegisteringParty: {
      type: Boolean,
      default: false
    },
    isMhrPartySearch: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const {
      setMhrSubmittingParty
    } = useActions<any>([
      'setMhrSubmittingParty'
    ])
    const { addSecuredParty, setRegisteringParty, isExistingSecuredParty } = useSecuredParty(props, context)
    const countryProvincesHelpers = useCountriesProvinces()
    const localState = reactive({
      searchValue: '',
      autoCompleteIsActive: props.setAutoCompleteActive,
      autoCompleteSelected: -1,
      autoCompleteResults: [],
      resultAdded: [],
      selectedCode: null,
      mouseOver: false,
      isRegisteringParty: computed((): boolean => {
        return props.setIsRegisteringParty
      }),
      partyWord: computed((): string => {
        if (props.setIsRegisteringParty) {
          return 'Registering'
        }
        return 'Secured'
      })
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

      if (localState.isRegisteringParty) {
        newParty.action = ActionTypes.EDITED
        setRegisteringParty(newParty)
      } else if (props.isMhrPartySearch) {
        localState.selectedCode = newParty.code
        // pre-set country code to prevent clearing of base-address component fields (bug 13637)
        setMhrSubmittingParty({ key: 'address.country', value: newParty.address.country })
        // Set submitting party data to store
        for (const [key, value] of Object.entries(newParty)) {
          setMhrSubmittingParty({ key, value })
        }
      } else {
        addSecuredParty(newParty)
      }

      context.emit('selectItem')
      closeAutoComplete()
    }

    const closeAutoComplete = () => {
      localState.autoCompleteIsActive = false
      localState.resultAdded = []
    }

    watch(
      () => props.autoCompleteItems,
      (items: Array<any>) => {
        localState.autoCompleteResults = items
        if (items) {
          localState.autoCompleteIsActive = true
        } else {
          localState.autoCompleteIsActive = false
        }
      },
      { immediate: true, deep: true }
    )

    watch(
      () => props.setAutoCompleteActive,
      (val: boolean) => {
        localState.autoCompleteIsActive = props.setAutoCompleteActive
      }
    )

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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.auto-complete-item {
  min-height: 0;
}

.auto-complete-item:hover {
  color: $primary-blue !important;
  background-color: $gray1 !important;
}
.auto-complete-item:hover .auto-complete-row{
  color: $primary-blue !important;
}

.added-color {
  color : $gray7 !important;
}

.auto-complete-added-item:hover {
  background-color: $gray1 !important;
}

.auto-complete-added-item:hover .auto-complete-row{
  color: $gray7 !important;
}

.auto-complete-item[aria-selected='true'] {
  color: $primary-blue !important;
  background-color: $blueSelected !important;
}

.auto-complete-item:focus {
  background-color: $gray3 !important;
}

@media (min-width: 960px) {
  .auto-complete-card {
    width: 960px;
  }
}

.auto-complete-card {
  position: absolute;
  z-index: 3;
  margin-left: 20px;
}
.auto-complete-row {
  width: 35rem;
  color: $gray7 !important;
}

.was-selected {
  background-color: $blueSelected;
  color: $primary-blue !important;
}

.auto-complete-row:hover {
  color: $primary-blue !important;
}

.auto-complete-list {
  max-height: 450px;
  overflow-y: auto;
}

.auto-complete-action {
  width: 150px;
  flex-direction: row;
  justify-content: flex-end;
  font-size: 0.875rem;
}
.close-btn-row {
  height: 1rem;
}

.title-size {
  font-size: 1rem;
}

.icon-bump {
  margin-bottom: 3px;
}
</style>
