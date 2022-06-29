<template>
  <div id="mhr-describe-your-home">
    <section id="mhr-make-model" class="mt-10">
      <h2>Manufacturer, Make, and Model</h2>
      <p class="mt-2 mb-6">
        Enter the Year of Manufacture (not the model year), Make, and Model of
        the home.
      </p>
      <ManufacturerMakeModel />
    </section>

    <section id="mhr-home-sections" class="mt-10">
      <h2>Home Sections</h2>
      <p class="mt-2">Add the Serial Number and dimensions for each section of the home.</p>

      <HomeSections />
    </section>

    <section id="mhr-home-certification" class="mt-10">
      <h2>Home Certification</h2>
      <p class="mt-2">
        Enter either the Canadian Standards Association (CSA) number OR the Engineer's inspection information.
      </p>

      <HomeCertification :class="{ 'border-error-left': false }" />
    </section>

    <section id="mhr-rebuilt-status" class="mt-10">
      <h2>Rebuilt Status</h2>
      <p class="mt-2">
        If the home was rebuilt, include the description of the changes to the home (normally accompanied by a statutory
        declaration).
      </p>

      <RebuiltStatus class="mt-6" :class="{ 'border-error-left': false }" />
    </section>

    <section id="mhr-other-information" class="mt-10">
      <h2>Other Information</h2>
      <p class="mt-2">
        Include an other relevant information about the home.
      </p>

      <OtherInformation class="mt-6" :class="{ 'border-error-left': false }" />
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import {
  HomeCertification,
  HomeSections,
  ManufacturerMakeModel,
  RebuiltStatus,
  OtherInformation
} from '@/components/mhrRegistration/YourHome'

@Component({
  components: {
    HomeCertification,
    HomeSections,
    ManufacturerMakeModel,
    RebuiltStatus,
    OtherInformation
  }
})
export default class YourHome extends Vue {}
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
