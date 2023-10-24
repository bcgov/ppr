<template>
  <div
    class="caution-box px-4 pt-3 fs-14"
    :class="{ 'alert-box': setAlert }"
  >
    <slot name="prependSLot" />
    <p><b>{{ setImportantWord }}:</b> <span v-html="setMsg" /></p>
    <slot name="appendSLot" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CautionBox',
  props: {
    setMsg: String,
    setImportantWord: {
      type: String,
      default: 'Important'
    },
    setAlert: {
      type: Boolean,
      default: false
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.caution-box {
  display: flex;
  align-items: flex-start;
  background-color: $BCgovGold0;
  border: 1px solid $BCgovGold5;
}
.alert-box {
  background-color: $backgroundError;
  border: 1px solid $error;
}
</style>
