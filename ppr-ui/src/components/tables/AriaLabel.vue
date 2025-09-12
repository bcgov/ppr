<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    ariaText: { type: String, default: '' }
  }
})
</script>

<template>
  <span
    class="aria-label-only"
    aria-hidden="false"
  >
    {{ ariaText }}
  </span>
</template>

<style lang="scss" scoped>
.aria-label-only {
  display: none
}
</style>
