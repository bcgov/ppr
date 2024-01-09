<template>
  <div id="org-name-lookup">
    <v-text-field
      ref="orgNameSearchField"
      v-model="searchValue"
      variant="filled"
      persistentHint
      persistentClear
      :hint="fieldHint"
      :label="fieldLabel"
      :rules="orgNameRules"
      :clearable="showClear"
      :clearIcon="'mdi-close'"
      @click:clear="showClear = false"
      @keydown="manualEntryHandler"
      @update:focused="manualEntryFocusHandler"
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
      :nilSearchText="nilSearchText"
      :searchValue="autoCompleteSearchValue"
      :setAutoCompleteIsActive="autoCompleteIsActive"
      @searchValue="setSearchValue"
      @searching="loadingSearchResults = $event"
    />
  </div>
</template>
<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from 'vue'
import { BusinessSearchAutocomplete } from '@/components/search'

export default defineComponent({
  name: 'OrgNameLookup',
  components: {
    BusinessSearchAutocomplete
  },
  props: {
    baseValue: { type: String, default: '' },
    fieldLabel: { type: String, default: 'Find or enter the Full Legal Name of the Business' },
    fieldHint: { type: String, default: '' },
    disableManualEntry: { type: Boolean, default: false },
    orgNameRules: { type: Array as () => Array<(v:any)=>string|boolean>, default: () => [] },
    nilSearchText: {
      type: String,
      default: 'Ensure you have entered the correct, full legal name of the organization before entering the phone' +
        ' number and mailing address.'
    }
  },
  emits: ['updateOrgName'],
  setup (props, { emit }) {
    const localState = reactive({
      searchValue: props.baseValue || '',
      showClear: false,
      loadingSearchResults: false,
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      lookupResultSelected: false
    })

    const setSearchValue = (searchValueTyped: string) => {
      localState.lookupResultSelected = true
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValueTyped
      localState.showClear = true
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    /**
     * Clear search values if manual entry is disabled and a selection has already been made
     **/
    const manualEntryHandler = () => {
      if (props.disableManualEntry && localState.lookupResultSelected) {
        localState.searchValue = ''
        localState.lookupResultSelected = false
      }
    }

    /**
     * Clear search value when manual entry is disabled, no selection has been made and the field focus updates
     * Delay the process to allow for result selection interaction when calling on update:focus event
    **/
    const manualEntryFocusHandler = async () => {
      setTimeout(() => {
        if (props.disableManualEntry && !localState.lookupResultSelected) {
          localState.searchValue = ''
        }
      }, 100)
    }

    watch(() => localState.searchValue, (val: string) => {
      if (val?.length >= 3) {
        localState.autoCompleteSearchValue = val
        // show autocomplete results when there is a searchValue
        localState.autoCompleteIsActive = val !== ''
      } else {
        localState.autoCompleteSearchValue = val
        localState.autoCompleteIsActive = false
      }

      emit('updateOrgName', val)
    })

    watch(() => localState.lookupResultSelected, (val: boolean) => {
      if (!val) localState.searchValue = ''
    })

    return {
      setSearchValue,
      setCloseAutoComplete,
      manualEntryHandler,
      manualEntryFocusHandler,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
