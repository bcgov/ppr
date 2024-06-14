<template>
  <v-card
    flat
    class="collapsible-card"
  >
    <header class="review-header">
      <label
        class="font-weight-bold d-flex"
        data-test-id="card-header-label"
      >
        <img
          class="mr-1"
          width="25"
          src="@/assets/svgs/homeownersicon_reviewscreen.svg"
        >
        {{ headerLabel }}
      </label>

      <v-btn
        variant="plain"
        color="primary"
        class="hide-help-btn px-0"
        data-test-id="card-toggle-label"
        :ripple="false"
        @click="toggleCardOpen"
      >
        <v-icon
          icon="mdi-eye"
          class="mr-1"
        />
        {{ state.isCardOpen ? 'Hide' : 'Show' }} {{ toggleLabel }}
      </v-btn>
    </header>
    <v-expand-transition>
      <div
        v-if="state.isCardOpen"
        data-test-id="card-slots"
      >
        <!-- Information/Description text slot -->
        <slot name="infoSlot" />

        <slot name="mainSlot" />
      </div>
    </v-expand-transition>
  </v-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  headerLabel: string,
  toggleLabel: string
}>()

const state = reactive({
  isCardOpen: true
})

const toggleCardOpen = () => {
  state.isCardOpen = !state.isCardOpen;
}

</script>

<style lang="scss" scoped>
.collapsible-card {
  .review-header {
    background-color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
