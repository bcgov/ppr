<template>
  <section id="exemption-review" class="mt-9">
    REVIEW PLACEHOLDER
  </section>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'

export default defineComponent({
  name: 'ExemptionReview',
  components: {},
  props: {
    showErrors: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const localState = reactive({})

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
// TEMP PLACEHOLDER STYLING
section {
  min-height: 35vh;
}
</style>
