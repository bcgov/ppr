<template>
  <div class="caution-box">
    <p class="ma-0 pa-4">
      <b>{{ setImportantWord }}:</b> {{ setMsg }}
    </p>
  </div>
</template>

<script lang="ts">
// external
import { defineComponent } from 'vue-demi'

export default defineComponent({
  name: 'CautionBox',
  props: {
    setMsg: String,
    setImportantWord: {
      type: String,
      default: 'Important'
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.caution-box {
  background-color: $BCgovGold0;
  border: 1px solid $BCgovGold5;
  font-size: 0.875rem;
}
</style>
