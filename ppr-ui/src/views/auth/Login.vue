<template>
  <sbc-login :redirectUrl="redirectUrl" />
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
// Common Component
import SbcLogin from 'sbc-common-components/src/components/SbcLogin.vue'

/**
 * Operation:
 * 1. When this component is first loaded (ie, we are not authenticated) then the
 *    SbcLogin component will redirect us to log in.
 */
export default defineComponent({
  name: 'Login',
  components: {
    SbcLogin
  },
  setup (props, context) {
    const localState = reactive({
      redirectUrl: computed(() => {
        return (context.root.$route.query.redirect as string)
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
