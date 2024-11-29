<template>
  <sbc-signout :redirectUrl="logoutURL" />
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'

export default defineComponent({
  name: 'Signout',
  components: {
    SbcSignout
  },
  setup () {
    const localState = reactive({
      logoutURL: computed(() => {
        const url = `${sessionStorage.getItem('REGISTRY_URL')}?logout=true`
        return url ? url : null
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
</style>
