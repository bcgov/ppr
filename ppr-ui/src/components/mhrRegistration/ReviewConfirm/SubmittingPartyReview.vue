<template>
  <v-card flat id="-summary" class="mt-6">
    <header class="review-header">
      <v-icon class="ml-2" color="darkBlue">mdi-account</v-icon>
      <label class="font-weight-bold pl-2">Submitting Party</label>
    </header>

    <div :class="{ 'invalid-section': false }">
      <section class="mx-6 pt-8" v-if="true">
        <span>
          <v-icon color="error">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link
            :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.SUBMITTING_PARTY}` }"
          >Return to this step to finish it</router-link>
        </span>
      </section>

      <!-- divider -->
      <div class="px-4">
        <v-divider />
      </div>

      <!-- -->
      <template>
        <section class="pt-6" id="review-submitting-party-section">
          <!-- Insert Review mode of component here -->
        </section>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { RouteNames } from '@/enums'

export default defineComponent({
  name: 'SubmittingPartyReview',
  components: {},
  props: {},
  setup () {
    const localState = reactive({})

    return {
      RouteNames,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.review-header {
  display: flex; // to align icons
  background-color: $BCgovBlue5O;
  padding: 1.25rem;
  color: $gray9;
}
</style>
