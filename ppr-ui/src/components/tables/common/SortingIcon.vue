<template>
  <span>
    <v-icon
      v-if="sortAsc"
      size="small"
      :color="color"
      data-test-id="down-arrow-icon"
      aria-label="Sort Ascending Button"
      @click="emitSort(true)"
    >
      mdi-arrow-down
    </v-icon>
    <v-icon
      v-else
      size="small"
      :color="color"
      data-test-id="up-arrow-icon"
      aria-label="Sort Descending Button"
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
    },
    color: {
      type: String,
      default: 'black'
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
