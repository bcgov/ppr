<template>
  <v-chip
    v-if="action"
    class="info-chip-badge mr-4"
    label x-small
    :color="['DELETED', 'DECEASED'].includes(action) ? '#grey lighten-2' : 'primary'"
    :data-test-id="`${action}-badge`"
  >
    <b>{{ action }}</b>
  </v-chip>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'

export default defineComponent({
  name: 'InfoChip',
  components: {},
  props: {
    action: {
      type: String,
      default: ''
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
</style>
