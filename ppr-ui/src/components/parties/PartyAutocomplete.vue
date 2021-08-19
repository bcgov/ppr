<template>
  <v-card
    v-if="autoCompleteIsActive"
    id="party-search-auto-complete"
    :class="['mt-1', $style['auto-complete-card']]"
    elevation="5"
    v-click-outside="closeAutoComplete"
  >
    <v-row no-gutters justify="center" class="pl-2 pr-5">
      <v-col no-gutters cols="12">
        <v-list :class="$style['auto-complete-list']" class="pt-0">
          <v-list-item-group v-model="autoCompleteSelected">
            <v-list-item
              v-for="(result, i) in autoCompleteResults"
              :key="i"
              :class="['pt-0', 'pb-0', 'pl-1', $style['auto-complete-item']]"
            >
              <v-list-item-content class="pt-2 pb-2">
                <v-list-item-subtitle>
                  <v-row :class="$style['auto-complete-row']">
                    <v-col cols="2">{{ result.code }}</v-col>
                    <v-col cols="9"
                      >{{ result.businessName }}<br />
                      {{ result.address.street }},
                      {{ result.address.city }}
                      {{ result.address.region }}
                      {{ getCountryName(result.address.country) }},
                      {{ result.address.postalCode }}
                    </v-col>
                  </v-row>
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action
                :class="$style['auto-complete-action']"
                class="mt-n1"
              >
                <span v-if="!resultAdded[i]" @click="addResult(result, i)">
                  <v-icon>mdi-plus</v-icon>Add
                </span>
                <span class="auto-complete-added" v-else>
                  <v-icon class="auto-complete-added">mdi-check</v-icon>Added
                </span>
              </v-list-item-action>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { SearchPartyIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useCountriesProvinces } from '@/composables/address/factories'
import { useSecuredParty } from './composables/useSecuredParty'

export default defineComponent({
  props: {
    autoCompleteItems: {
      type: Array,
      default: []
    }
  },
  setup (props, context) {
    const { addSecuredParty } = useSecuredParty(props, context)
    const countryProvincesHelpers = useCountriesProvinces()
    const localState = reactive({
      searchValue: '',
      autoCompleteIsActive: false,
      autoCompleteSelected: -1,
      autoCompleteResults: [],
      resultAdded: []
    })

    const addResult = (party: SearchPartyIF, resultIndex) => {
      localState.resultAdded[resultIndex] = true

      const newParty: PartyIF = {
        code: party.code,
        businessName: party.businessName,
        emailAddress: party.emailAddress || '',
        address: party.address,
        personName: { first: '', middle: '', last: '' }
      }
      addSecuredParty(newParty)
    }

    const closeAutoComplete = () => {
      localState.autoCompleteIsActive = false
      localState.resultAdded = []
    }

    watch(
      () => props.autoCompleteItems,
      (items: Array<any>) => {
        localState.autoCompleteResults = items
        if (items.length > 0) {
          localState.autoCompleteIsActive = true
        } else {
          localState.autoCompleteIsActive = false
        }
      },
      { immediate: true, deep: true }
    )

    return {
      addResult,
      closeAutoComplete,
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
  background-color: #e0e0e05c !important;
}

.auto-complete-item[aria-selected='true'] {
  color: $primary-blue !important;
  background-color: #e4edf7 !important;
}

.auto-complete-item:focus {
  background-color: #dee2e6b8 !important;
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
}
.close-btn-row {
  height: 1rem;
}
</style>
