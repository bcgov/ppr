<template>
  <div
    class="caution-box pl-[30px] pr-[12px] pt-[22px] pb-[25px] fs-14 rounded"
    :class="{ 'alert-box': setAlert }"
  >
    <slot name="prependSLot" />
    <slot name="contentSLot">
      <p class="mb-0">
        <b>{{ setImportantWord }}:</b> <span v-html="setMsg" />
      </p>
    </slot>
    <slot name="appendSLot" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CautionBox',
  props: {
    setMsg: {
      type: String,
      default: ''
    },
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
@use '@/assets/styles/theme.scss' as *;
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
