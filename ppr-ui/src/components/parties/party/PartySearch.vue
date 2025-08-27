<template>
  <v-container
    id="ppr-party-code"
    class="bg-white px-0 py-6 noGutters rounded"
  >
    <v-row
      class="px-6"
      align="center"
    >
      <v-col :cols="hideManualSearchLabel ? 12 : 6">
        <v-text-field
          id="txt-code"
          v-model="searchValue"
          variant="filled"
          color="primary"
          :label="searchFieldLabel"
          persistent-hint
          hint="Enter at least the first 3 characters"
          :class="isAutoCompleteDisabled ? 'disabled-custom' : ''"
          :disabled="isAutoCompleteDisabled"
        />
      </v-col>
      <v-col
        v-if="!hideManualSearchLabel"
        cols="6"
        class="pt-0 mt-n5 d-flex"
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
        <p
          v-else
          class="ml-2"
        >
          Manually enter submitting party information below
        </p>
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
          @select-item="selectItem($event)"
          @close-auto-complete="closeAutoComplete"
        />
      </v-col>
    </v-row>
    <v-row
      v-if="getRegistrationFlowType !== RegistrationFlowType.AMENDMENT && !isRegisteringParty && !isMhrPartySearch"
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
          hide-details
          :disabled="isAutoCompleteDisabled"
          @update:model-value="addRegisteringParty"
        />
      </v-col>
      <v-col
        class="pl-0"
        :class="{ 'disabled-text': isAutoCompleteDisabled }"
      >
        <p>Include the Registering Party as a Secured Party</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useStore } from '@/store/store'
import { PartyAutocomplete } from '@/components/parties/party'
import { RegistrationFlowType } from '@/enums'
import type { SearchPartyIF } from '@/interfaces'
import { partyCodeSearch } from '@/utils/ppr-api-helper'
import { storeToRefs } from 'pinia'

const props = withDefaults(defineProps<{
  isAutoCompleteDisabled?: boolean
  registeringPartyAdded?: boolean
  isRegisteringParty?: boolean
  isMhrPartySearch?: boolean
  hideManualSearchLabel?: boolean
}>(), {
  isAutoCompleteDisabled: false,
  registeringPartyAdded: false,
  isRegisteringParty: false,
  isMhrPartySearch: false,
  hideManualSearchLabel: false
})

const emit = defineEmits<{
  (e: 'selectItem', value: any): void
  (e: 'hideSearch' | 'showSecuredPartyAdd' | 'addRegisteringParty' | 'removeRegisteringParty'): void
}>()

const { getRegistrationFlowType } = storeToRefs(useStore())

const searchValue = ref('')
const autoCompleteResults = ref<SearchPartyIF[] | null>(null)
const setAutoCompleteActive = ref(false)
const registeringPartySelected = ref(false)
const resultAdded = ref([])
const partyCode = ref(0)
const partyWord = computed((): string => props.isRegisteringParty ? 'Registering' : 'Secured')
const searchFieldLabel = computed((): string => {
  if (props.isMhrPartySearch) return 'Use PPR Party Code or Name'
  else if (props.isRegisteringParty) return 'Registering Party Code or Name'
  else return 'Secured Party Code or Name'
})

function goToAddSecuredParty() {
  if (searchValue.value) {
    searchValue.value = ''
    setAutoCompleteActive.value = false
    closeAutoComplete()
  }
  emit('showSecuredPartyAdd')
}

function addRegisteringParty() {
  if (registeringPartySelected.value) {
    emit('addRegisteringParty')
  } else {
    emit('removeRegisteringParty')
  }
}

function closeAutoComplete() {
  setAutoCompleteActive.value = false
  autoCompleteResults.value = []
}

function selectItem(selectedItem: any) {
  searchValue.value = ''
  emit('selectItem', selectedItem)
  emit('hideSearch')
}

async function updateAutoCompleteResults(searchValueArg: string) {
  const response: SearchPartyIF[] = await partyCodeSearch(searchValueArg, false)
  if ((response?.length > 0) && (searchValueArg === searchValue.value)) {
    autoCompleteResults.value = response
    setAutoCompleteActive.value = true
  }
  if ((response?.length < 1) && (searchValueArg === searchValue.value)) {
    autoCompleteResults.value = []
    setAutoCompleteActive.value = true
  }
}

watch(() => searchValue.value, (val: string) => {
  if (val.length >= 3) {
    updateAutoCompleteResults(val)
  }
  if (val.length === 0) {
    setAutoCompleteActive.value = false
  }
})

watch(() => props.registeringPartyAdded, (sel: boolean) => {
  registeringPartySelected.value = sel
})

</script>

<style lang="scss" module>
@use '@/assets/styles/theme.scss' as *;
.close-btn-row {
  height: 1rem;
}
</style>
