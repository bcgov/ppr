<template>
  <v-container
    id="ppr-party-code"
    fluid
    class="bg-white px-0 py-6 no-gutters"
  >
    <v-row
      class="px-6"
      align="center"
    >
      <v-col cols="6">
        <v-text-field
          id="txt-code"
          v-model="searchValue"
          variant="filled"
          :label="searchFieldLabel"
          persistent-hint
          hint="Enter at least the first 3 characters"
          :class="isAutoCompleteDisabled ? 'disabled-custom' : ''"
          :disabled="isAutoCompleteDisabled"
        />
      </v-col>
      <v-col
        cols="6"
        class="pt-0 mt-n5"
        :class="{ 'disabled-text': isAutoCompleteDisabled }"
      >
        or
        <a
          v-if="!isMhrPartySearch"
          id="add-party"
          class="generic-link pl-2"
          :class="{ 'disabled-text': isAutoCompleteDisabled }"
          :disabled="isAutoCompleteDisabled"
          @click="goToAddSecuredParty"
        >Add a {{ partyWord }} Party that doesn't have a code
        </a>
        <span v-else>Manually enter submitting party information below</span>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <PartyAutocomplete
          v-if="setAutoCompleteActive"
          :auto-complete-items="autoCompleteResults"
          :default-click-to-add="false"
          :is-registering-party="isRegisteringParty"
          :is-mhr-party-search="isMhrPartySearch"
          @selectItem="selectItem($event)"
          @closeAutoComplete="closeAutoComplete"
        />
      </v-col>
    </v-row>
    <v-row
      v-if="registrationFlowType !== RegistrationFlowType.AMENDMENT && !isRegisteringParty && !isMhrPartySearch"
      class="px-6"
      align="center"
    >
      <v-col
        cols="auto"
        class="pr-0"
      >
        <v-checkbox
          id="add-registering-party"
          v-model="registeringPartySelected"
          class="reg-checkbox pa-0 ma-0"
          :hide-details="true"
          :disabled="isAutoCompleteDisabled"
          @click="addRegisteringParty"
        />
      </v-col>
      <v-col
        class="pl-0"
        :class="{ 'disabled-text': isAutoCompleteDisabled }"
      >
        Include the Registering Party as a Secured Party
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  computed
} from 'vue'
import { useStore } from '@/store/store'
import { PartyAutocomplete } from '@/components/parties/party'
import { RegistrationFlowType } from '@/enums'
import { SearchPartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { partyCodeSearch } from '@/utils'
import { storeToRefs } from 'pinia'

export default defineComponent({
  components: {
    PartyAutocomplete
  },
  props: {
    isAutoCompleteDisabled: {
      type: Boolean,
      default: false
    },
    registeringPartyAdded: {
      type: Boolean,
      default: false
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
  emits: [
    'selectItem',
    'hideSearch',
    'showSecuredPartyAdd',
    'addRegisteringParty',
    'removeRegisteringParty'
  ],
  setup (props, context) {
    const { getRegistrationFlowType } = storeToRefs(useStore())
    const registrationFlowType = getRegistrationFlowType.value
    const localState = reactive({
      searchValue: '',
      autoCompleteResults: null,
      setAutoCompleteActive: false,
      registeringPartySelected: false,
      resultAdded: [],
      partyCode: 0,
      partyWord: computed((): string => props.isRegisteringParty
        ? 'Registering'
        : 'Secured'),
      searchFieldLabel: computed((): string => {
        if (props.isMhrPartySearch) return 'Use PPR Party Code or Name'
        else if (props.isRegisteringParty) return 'Registering Party Code or Name'
        else return 'Secured Party Code or Name'
      })
    })

    const goToAddSecuredParty = () => {
      if (localState.searchValue) {
        localState.searchValue = ''
        localState.setAutoCompleteActive = false
        closeAutoComplete()
      }
      context.emit('showSecuredPartyAdd')
    }

    const addRegisteringParty = () => {
      if (localState.registeringPartySelected) {
        context.emit('addRegisteringParty')
      } else {
        context.emit('removeRegisteringParty')
      }
    }

    const closeAutoComplete = () => {
      localState.setAutoCompleteActive = false
      localState.autoCompleteResults = []
    }

    const selectItem = (selectedItem) => {
      localState.searchValue = ''
      context.emit('selectItem', selectedItem)
      context.emit('hideSearch')
    }

    const updateAutoCompleteResults = async (searchValue: string) => {
      const response: [SearchPartyIF] = await partyCodeSearch(
        searchValue,
        false
      )
      // check if results are still relevant before updating list
      if ((response?.length > 0) && (searchValue === localState.searchValue)) {
        localState.autoCompleteResults = response
        localState.setAutoCompleteActive = true
      }
      if ((response?.length < 1) && (searchValue === localState.searchValue)) {
        localState.autoCompleteResults = []
        localState.setAutoCompleteActive = true
      }
    }

    watch(
      () => localState.searchValue,
      (val: string) => {
        if (localState.searchValue.length >= 3) {
          updateAutoCompleteResults(val)
        }
        if (localState.searchValue.length === 0) {
          localState.setAutoCompleteActive = false
        }
      }
    )
    watch(
      () => props.registeringPartyAdded,
      (sel: boolean) => {
        localState.registeringPartySelected = sel
      }
    )

    return {
      goToAddSecuredParty,
      addRegisteringParty,
      closeAutoComplete,
      registrationFlowType,
      RegistrationFlowType,
      selectItem,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';

.close-btn-row {
  height: 1rem;
}
</style>
