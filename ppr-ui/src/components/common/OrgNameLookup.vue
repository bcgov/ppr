<template>
  <div id="org-name-lookup">
    <v-text-field
      id="org-name"
      ref="orgNameSearchField"
      v-model="searchValue"
      variant="filled"
      persistentHint
      :hint="fieldHint"
      :label="fieldLabel"
      :rules="orgNameRules"
      :clearable="showClear"
      @click:clear="showClear = false"
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
      @search-value="setSearchValue"
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
      autoCompleteSearchValue: ''
    })

    const setSearchValue = (searchValueTyped: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValueTyped
      localState.showClear = true
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
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

    return {
      setSearchValue,
      setCloseAutoComplete,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
