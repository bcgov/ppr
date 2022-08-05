<template>
  <div id="mhr-home-location">
    <section id="mhr-home-location-type-wrapper" class="mt-10">
      <h2>Location Type</h2>
      <p class="mt-2 mb-6">
        Indicate the type of location for the home.
      </p>

      <!-- Home Location Type -->
      <HomeLocationType :class="{ 'border-error-left': false }" />
    </section>

    <section id="mhr-home-civic-address-wrapper" class="mt-10">
      <h2>Civic Address of the Home</h2>
      <p class="mt-2">
        Enter the Street Address (Number and Name) and City for the location of the home. Must be located in B.C.
      </p>
      <HomeCivicAddress :class="{ 'border-error-left': false }" />
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { HomeLocationType, HomeCivicAddress } from '@/components/mhrRegistration'

@Component({
  components: {
    HomeLocationType,
    HomeCivicAddress
  }
})
export default class HomeLocation extends Vue {
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#mhr-home-location {
  /* Set "header-counter" to 0 */
  counter-reset: header-counter;
}

h2::before {
  /* Increment "header-counter" by 1 */
  counter-increment: header-counter;
  content: counter(header-counter) '. ';
}
</style>
