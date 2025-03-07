<template>
  <BaseDialog
    :set-display="display"
    :set-options="options"
    @proceed="proceed($event)"
  >
    <template #content>
      <p class="dialog-text">
        <b>{{ numberRegistrations }} exact match registrations</b> will be included in your PDF search result
        report along with an overiew of the search results.
      </p>
      <p class="body-text">
        Reports containing more than 75 results <b>may take up to 20 minutes to generate.</b> Once generated, the report
        will appear in your search result list.
      </p>
    </template>
  </BaseDialog>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from 'vue'
import type { DialogOptionsIF } from '@/interfaces'

export default defineComponent({
  name: 'LargeSearchResultDialog',
  props: {
    setDisplay: {
      type: Boolean,
      default: false
    },
    setOptions:  {
      type: Object as () => DialogOptionsIF,
      default: () => {}
    },
    setNumberRegistrations: {
      type: Number,
      default: 0
    }
  },
  emits: ['proceed'],
  setup (props, { emit }) {
    const localState = reactive({
      preventDialog: false,
      updateFailed: false,
      display: computed(() => {
        return props.setDisplay
      }),
      options: computed(() => {
        return props.setOptions
      }),
      numberRegistrations: computed(() => {
        return props.setNumberRegistrations
      })
    })

    const proceed = (val: boolean) => {
      emit('proceed', val)
    }

    return {
      proceed,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
