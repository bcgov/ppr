<template>
  <div>
    <sbc-login :redirect-url="redirectUrl" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useRoute } from 'vue-router'
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
  setup () {
    const route = useRoute()
    const localState = reactive({
      redirectUrl: computed(() => {
        return (route.query.redirect as string)
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
