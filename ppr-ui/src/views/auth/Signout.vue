<template>
  <sbc-signout :redirect-url="baseURL" />
</template>

<script lang="ts">
// Libraries
import { Component, Vue } from 'vue-property-decorator'

// Components
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'

@Component({
  components: {
    SbcSignout
  }
})
export default class Signout extends Vue {
  /** The URL of the PPR home page. */
  private get baseURL (): string {
    return window.location.origin
  }
}
</script>

<style lang="scss" scoped>
</style>
