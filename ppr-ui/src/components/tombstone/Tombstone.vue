<template>
  <v-container class="view-container px-15 py-0" fluid style="background-color: white;">
    <div class="container pa-0 pt-6">
      <default-tombstone v-if="displayDefault" />
      <discharge-tombstone v-else-if="displayDischarge" />
    </div>
  </v-container>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
// local
import { DefaultTombstone, DischargeTombstone } from '@/components/tombstone'

export default defineComponent({
  name: 'Tombstone',
  components: {
    DefaultTombstone,
    DischargeTombstone
  },
  setup (props, { root }) {
    const localState = reactive({
      displayDefault: computed((): boolean => {
        return !root.$router.currentRoute.path.includes('discharge')
      }),
      displayDischarge: computed((): boolean => {
        return root.$router.currentRoute.path.includes('discharge')
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
