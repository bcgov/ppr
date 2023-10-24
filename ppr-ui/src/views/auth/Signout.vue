<template>
  <sbc-signout :redirect-url="logoutURL" />
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
// Common Component
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
        if (url) return url
        return null
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
