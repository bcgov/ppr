<template>
  <sbc-signin @sync-user-profile-ready="onProfileReady()" />
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import { useRoute, useRouter } from 'vue-router/composables'
// Common Component
import SbcSignin from 'sbc-common-components/src/components/SbcSignin.vue'
import { navigate } from '@/utils'

/**
 * Operation:
 * 1. When this component is first loaded (ie, we are not authenticated) then the
 *    SbcSgnin component will redirect us to log in.
 * 2. When this component is reloaded (ie, we are now authenticated) then the
 *    SbcSignin component will emit "sync-user-profile-ready".
 */
export default defineComponent({
  name: 'Signin',
  components: {
    SbcSignin
  },
  emits: ['profileReady'],
  props: {
    registryUrl: {
      type: String,
      default: 'https://bcregistry.ca'
    }
  },
  setup (props, context) {
    const route = useRoute()
    const router = useRouter()
    const localState = reactive({})

    /** Called when user profile is ready (ie, the user is authenticated). */
    const onProfileReady = () => {
      // let App know that data can now be loaded
      emitProfileReady()

      if (route.query.redirect) {
        // navigate to the route we originally came from
        router.push(route.query.redirect as string)
      } else {
        console.error('Signin page missing redirect param') // eslint-disable-line no-console
        // redirect to PPR home page
        navigate(props.registryUrl)
      }
    }
    const emitProfileReady = (profileReady: boolean = true) => {
      context.emit('profileReady', profileReady)
    }

    return {
      onProfileReady,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
</style>
