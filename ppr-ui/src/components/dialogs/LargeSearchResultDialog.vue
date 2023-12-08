<template>
  <BaseDialog
    :setDisplay="setDisplay"
    :setOptions="setOptions"
    @proceed="proceed($event)"
  >
    <template #content>
      <p class="dialog-text">
        <b>{{ setNumberRegistrations }} registrations</b> will be included in your PDF search result
        report along with an overiew of the search results. Reports containing more than 75 results <b>may
          take up to 20 minutes to generate.</b>
      </p>
      <p>
        You can change the selected registrations to reduce your report size or generate
        your report now with these selected matches. Once generated, the report will appear
        in your search result list.
      </p>
    </template>
  </BaseDialog>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs
} from 'vue'
import BaseDialog from './BaseDialog.vue'
import { DialogOptionsIF } from '@/interfaces'

export default defineComponent({
  name: 'LargeSearchResultDialog',
  components: {
    BaseDialog
  },
  props: {
    setDisplay: {
      type: Boolean,
      default: false
    },
    setOptions: {
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
      updateFailed: false
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
