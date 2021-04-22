<template>
  <v-card v-if="showAutoComplete" :class="['mt-1', $style['auto-complete-card']]" elevation="5">
    <v-row no-gutters justify="end" :class="$style['close-btn-row']">
      <v-col cols="auto" justify="end" class="pt-0">
        <v-btn append
               icon
               x-small
               right
               :id="$style['auto-complete-close-btn']"
               class="auto-complete-close-btn"
               @click="autoCompleteIsActive=false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters justify="center" class="pl-2 pr-5">
      <v-col no-gutters cols="auto">
        <v-list class="pt-0">
          <v-list-item-group v-model="autoCompleteSelected">
            <v-list-item v-for="(result, i) in autoCompleteResults"
                         :key="i"
                         :class="['pt-0', 'pb-0', 'pl-1', $style['auto-complete-item']]">
              <v-list-item-content class="pt-2 pb-2">
                <v-list-item-title v-text="result.value"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { getAutoComplete } from '@/utils'
import { AutoCompleteResponseIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'AutoComplete',
  props: {
    setAutoCompleteIsActive: {
      type: Boolean
    },
    registrationTypeValue: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    const localState = reactive({
      autoCompleteIsActive: props.setAutoCompleteIsActive,
      autoCompleteResults: [],
      autoCompleteSelected: -1,
      showAutoComplete: computed((): boolean => {
        const value = localState.autoCompleteResults?.length > 0 && localState.autoCompleteIsActive
        emit('hide-details', value)
        return value
      })
    })
    const updateAutoCompleteResults = async (registrationTypeValue: string) => {
      const response: AutoCompleteResponseIF = await getAutoComplete(registrationTypeValue)
      // check if results are still relevant before updating list
      if (registrationTypeValue === props.registrationTypeValue && response?.results) {
        // will take up to 5 results
        localState.autoCompleteResults = response?.results.slice(0, 5)
      }
    }
    watch(() => localState.autoCompleteSelected, (val: number) => {
      if (val >= 0) {
        const typeValue = localState.autoCompleteResults[val]?.value
        localState.autoCompleteIsActive = false
        emit('reg-type-Value', typeValue)
      }
    })
    watch(() => localState.autoCompleteIsActive, (val: boolean) => {
      if (!val) localState.autoCompleteResults = []
    })
    watch(() => props.setAutoCompleteIsActive, (val: boolean) => {
      localState.autoCompleteIsActive = val
    })
    watch(() => props.registrationTypeValue, (val: string) => {
      if (localState.autoCompleteIsActive) {
        updateAutoCompleteResults(val)
      }
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
#auto-complete-close-btn {
  color: $gray5 !important;
  background-color: transparent !important;
}
.auto-complete-item {
  min-height: 0;
}
.auto-complete-card {
  max-width: 30rem;
  position: absolute;
  z-index: 3;
}
.close-btn-row {
  height: 1rem;
}
</style>
