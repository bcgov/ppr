<template>
  <div class="bg-white">
    <v-container class="py-8">
      <TombstoneDynamic
        v-if="displayTombstoneDynamic"
        :isMhrInformation="displayMhrInformation"
        :actionInProgress="actionInProgress"
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
import { TombstoneDefault, TombstoneDynamic } from '@/components/tombstone'
import { useMhrCorrections } from '@/composables'

export default defineComponent({
  name: 'Tombstone',
  components: {
    TombstoneDefault,
    TombstoneDynamic
  },
  props: {
    actionInProgress: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const route = useRoute()
    const { isMhrCorrection } = useMhrCorrections()
    const localState = reactive({
      currentPath: computed((): string => {
        return route.path
      }),
      displayTombstoneDynamic: computed((): boolean => {
        return isMhrCorrection.value || ['discharge', 'renew', 'amend', 'mhr-information', 'exemption']
          .some(path => localState.currentPath.includes(path))
      }),
      displayMhrInformation: computed((): boolean => {
        return ['mhr-information', 'exemption'].some(path => localState.currentPath.includes(path))
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
@media print {
  .px-15 {
    padding-left: 10px !important;
    padding-right: 10px !important;
  }
}
</style>
