<template>
  <div class="bg-white">
    <v-container class="py-7">
      <tombstone-discharge
        v-if="displayDischarge || displayRenewal || displayAmendment || displayMhrInformation"
        :is-mhr-information="displayMhrInformation"
      />
      <tombstone-default v-else />
    </v-container>
  </div>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useRoute } from 'vue-router'
// local
import { TombstoneDefault, TombstoneDischarge } from '@/components/tombstone'

export default defineComponent({
  name: 'Tombstone',
  components: {
    TombstoneDefault,
    TombstoneDischarge
  },
  setup () {
    const route = useRoute()
    const localState = reactive({
      currentPath: computed((): string => {
        return route.path
      }),
      displayDischarge: computed((): boolean => {
        return localState.currentPath.includes('discharge')
      }),
      displayRenewal: computed((): boolean => {
        return localState.currentPath.includes('renew')
      }),
      displayAmendment: computed((): boolean => {
        return localState.currentPath.includes('amend')
      }),
      displayMhrInformation: computed((): boolean => {
        return localState.currentPath.includes('mhr-information') || localState.currentPath.includes('exemption')
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
