<template>
  <div class="bg-white">
    <v-container class="py-8">
      <TombstoneDynamic
        v-if="displayTombstoneDynamic"
        :isMhrInformation="displayMhrInformation"
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

export default defineComponent({
  name: 'Tombstone',
  components: {
    TombstoneDefault,
    TombstoneDynamic
  },
  setup () {
    const route = useRoute()
    const localState = reactive({
      currentPath: computed((): string => {
        return route.path
      }),
      displayTombstoneDynamic: computed((): boolean => {
        return ['discharge', 'renew', 'amend', 'mhr-information', 'exemption']
          .some(path => localState.currentPath.includes(path))
      }),
      displayMhrInformation: computed((): boolean => {
        return localState.currentPath.includes('mhr-information')
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
