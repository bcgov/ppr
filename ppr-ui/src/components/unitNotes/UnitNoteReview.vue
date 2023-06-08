<template>
  <div>
    // Review and Confirm placeholder
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'

export default defineComponent({
  name: 'UnitNoteReview',
  setup () {
    const localState = reactive({
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped></style>
