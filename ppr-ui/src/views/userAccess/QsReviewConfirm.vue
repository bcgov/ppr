<template>
  <span>Qualified Supplier Review Confirm Placeholder</span>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'

export default defineComponent({
  name: 'QsReviewConfirm',
  components: {},
  props: {},
  setup (props, context) {
    const localState = reactive({})

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
