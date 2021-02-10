<template>
  <sbc-signin @sync-user-profile-ready="onProfileReady()" />
</template>

<script lang="ts">
// Libraries
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'

// Components
import SbcSignin from 'sbc-common-components/src/components/SbcSignin.vue'

/**
 * Operation:
 * 1. When this component is first loaded (ie, we are not authenticated) then the
 *    SbcSgnin component will redirect us to log in.
 * 2. When this component is reloaded (ie, we are now authenticated) then the
 *    SbcSignin component will emit "sync-user-profile-ready".
 */
@Component({
  components: {
    SbcSignin
  }
})
export default class Signin extends Vue {
  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  /** Called when user profile is ready (ie, the user is authenticated). */
  private onProfileReady () {
    // let App know that data can now be loaded
    this.emitProfileReady()

    if (this.$route.query.redirect) {
      // navigate to the route we originally came from
      this.$router.push(this.$route.query.redirect as string)
    } else {
      console.error('Signin page missing redirect param') // eslint-disable-line no-console
      // redirect to PPR home page
      window.location.assign(this.registryUrl)
    }
  }

  /** Emits Profile Ready event. */
  @Emit('profileReady')
  private emitProfileReady (profileReady: boolean = true): void {}
}
</script>

<style lang="scss" scoped>
</style>
