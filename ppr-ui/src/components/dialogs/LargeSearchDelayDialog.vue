<template>
  <base-dialog :setDisplay="display" :setOptions="options" @proceed="proceed($event)">
    <template v-slot:content>
      <p class="dialog-text">
      <b>{{ numberRegistrations }} exact match registrations</b> will be included in your PDF search result
      report along with an overiew of the search results.
      </p>
      <p class="body-text">
        Reports containing more than 75 results <b>may
        take up to 20 minutes to generate.</b> Once generated, the report will appear
        in your search result list.
      </p>
    </template>
  </base-dialog>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from 'vue'
// local components
import BaseDialog from './BaseDialog.vue'
// local types/helpers/etc.
import { DialogOptionsIF } from '@/interfaces' // eslint-disable-line

export default defineComponent({
  name: 'LargeSearchResultDialog',
  components: {
    BaseDialog
  },
  props: {
    setDisplay: { default: false },
    setOptions: Object as () => DialogOptionsIF,
    setNumberRegistrations: { default: 0 }
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
.body-text {
  color: $gray7;
}
</style>
