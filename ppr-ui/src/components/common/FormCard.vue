<template>
  <v-card
    id="form-card"
    flat
    class="pa-8"
    :class="{ 'border-error-left': showErrors }"
  >
    <v-row noGutters>
      <v-col cols="3">
        <label
          class="generic-label"
          :class="{ 'error-text': showErrors }"
        >{{ label }}</label>
      </v-col>
      <v-col
        cols="9"
      >
        <!-- Form information slot -->
        <slot name="infoSlot" />
        <!-- Form slot -->
        <slot name="formSlot" />
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'FormCard',
  props: {
    label: { type: String, default: 'Label' },
    showErrors: { type: Boolean, default: false }
  },
  setup () {}
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
