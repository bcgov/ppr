<template>
  <sbc-signout :redirect-url="registryUrl" />
</template>

<script lang="ts">
// Libraries
import { Component, Prop, Vue } from 'vue-property-decorator'

// Components
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'

@Component({
  components: {
    SbcSignout
  }
})
export default class Signout extends Vue {
  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string
}
</script>

<style lang="scss" scoped>
</style>
