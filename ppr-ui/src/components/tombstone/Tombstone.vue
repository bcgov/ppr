<template>
  <v-container class="header-container view-container px-15 py-0" fluid style="background-color: white;">
    <div class="container pa-0" style="padding: 29px 0 !important;">
      <tombstone-discharge
        v-if="displayDischarge || displayRenewal || displayAmendment || displayMhrInformation"
        :isMhrInformation="displayMhrInformation"
      />
      <tombstone-default v-else />
    </div>
  </v-container>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from 'vue'
// local
import { TombstoneDefault, TombstoneDischarge } from '@/components/tombstone'

export default defineComponent({
  name: 'Tombstone',
  components: {
    TombstoneDefault,
    TombstoneDischarge
  },
  props: {
    setCurrentPath: {
      default: ''
    }
  },
  setup (props) {
    const localState = reactive({
      currentPath: computed((): string => {
        return props.setCurrentPath
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
