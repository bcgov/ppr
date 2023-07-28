<template>
  <span>Qualified Supplier Information Placeholder</span>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'

export default defineComponent({
  name: 'QsInformation',
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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
