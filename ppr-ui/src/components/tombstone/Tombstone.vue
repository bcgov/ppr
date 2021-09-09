<template>
  <v-container class="view-container px-15 py-0" fluid style="background-color: white;">
    <div class="container pa-0" style="padding: 29px 0 !important;">
      <tombstone-discharge v-if="displayDischarge || displayRenewal" />
      <tombstone-default v-else />
    </div>
  </v-container>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
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
  setup (props, { root }) {
    const localState = reactive({
      currentPath: computed((): string => {
        return props.setCurrentPath
      }),
      displayDischarge: computed((): boolean => {
        return localState.currentPath.includes('discharge')
      }),
      displayRenewal: computed((): boolean => {
        return localState.currentPath.includes('renew')
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
