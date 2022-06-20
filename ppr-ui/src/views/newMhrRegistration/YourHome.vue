<template>
  <div id="mhr-describe-your-home">
    <ManufacturerMakeModel />

    <section id="mhr-home-sections" class="mt-10">
      <h2>Home Sections</h2>
      <p>Add the Serial Number and dimensions for each section of the home.</p>

      <HomeSections />
    </section>

    <section id="mhr-home-certification" class="mt-10">
      <h2>Home Certification</h2>

      <v-card flat class="mt-5">
        <span>HOME CERTIFICATION PLACEHOLDER</span>
      </v-card>
    </section>

    <section id="mhr-rebuilt-status" class="mt-10">
      <h2>Rebuilt Status</h2>

      <v-card flat class="mt-5">
        <span>REBUILT STATUS PLACEHOLDER</span>
      </v-card>
    </section>

    <OtherInformation :getErrorMessage="getMessage" />
  </div>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import {
  HomeSections,
  ManufacturerMakeModel,
  OtherInformation
} from '@/components/mhrRegistration/YourHome'
import { ErrorMixin } from '@/mixins'

@Component({
  components: {
    HomeSections,
    ManufacturerMakeModel
  }
})
export default class YourHome extends Mixins(ErrorMixin) {}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#mhr-describe-your-home {
  /* Set "header-counter" to 0 */
  counter-reset: header-counter;
}

h2::before {
  /* Increment "header-counter" by 1 */
  counter-increment: header-counter;
  content: counter(header-counter) '. ';
}
</style>
