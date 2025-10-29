<template>
  <div class="bg-white">
    <v-container class="py-6">
      <TombstoneDynamic
        v-if="displayTombstoneDynamic"
        :is-mhr-information="displayMhrInformation"
        :action-in-progress="actionInProgress"
      />
      <TombstoneDefault v-else />
    </v-container>
  </div>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useRoute } from 'vue-router'
// local
import { useMhrCorrections } from '@/composables'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'Tombstone',
  props: {
    actionInProgress: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const route = useRoute()
    const { isMhrCorrection } = useMhrCorrections()
    const { isMhrReRegistration } = storeToRefs(useStore())
    const localState = reactive({
      currentPath: computed((): string => {
        return route.path
      }),
      displayTombstoneDynamic: computed((): boolean => {
        return isMhrCorrection.value || isMhrReRegistration.value ||
          ['discharge', 'renew', 'amend', 'mhr-information', 'exemption', 'mhr-history', 'mhr-queue-transfer']
            .some(path => localState.currentPath.includes(path))
      }),
      displayMhrInformation: computed((): boolean => {
        return ['mhr-information', 'exemption', 'mhr-history'].some(path => localState.currentPath.includes(path))
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
@media print {
  .px-15 {
    padding-left: 10px !important;
    padding-right: 10px !important;
  }
}
</style>
