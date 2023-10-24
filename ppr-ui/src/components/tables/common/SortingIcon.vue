<template>
  <span>
    <v-icon
      v-if="sortAsc"
      size="small"
      color="black"
      data-test-id="down-arrow-icon"
      @click="emitSort(true)"
    >
      mdi-arrow-down
    </v-icon>
    <v-icon
      v-else
      size="small"
      color="black"
      data-test-id="up-arrow-icon"
      @click="emitSort(false)"
    >
      mdi-arrow-up
    </v-icon>
  </span>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'

export default defineComponent({
  name: 'SortingIcon',
  components: {},
  props: {
    sortAsc: {
      type: Boolean,
      default: false
    }
  },
  emits: ['sortEvent'],
  setup (props, context) {
    const localState = reactive({})
    const emitSort = isAsc => context.emit('sortEvent', isAsc)

    return {
      emitSort,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
