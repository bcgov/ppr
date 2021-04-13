<template>
  <sbc-signout :redirect-url="logoutURL" />
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
  private get logoutURL (): string {
    const url = sessionStorage.getItem('AUTH_URL')
    if (url) return url
    return null
  }
}
</script>

<style lang="scss" scoped>
</style>
