<template>
  <span>
    <v-icon
      v-if="sortAsc"
      small
      color="black"
      @click="emitSort(true)"
      data-test-id="down-arrow-icon"
    >
      mdi-arrow-down
    </v-icon>
    <v-icon
      v-else
      small
      color="black"
      @click="emitSort(false)"
      data-test-id="up-arrow-icon"
    >
      mdi-arrow-up
    </v-icon>
  </span>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'

export default defineComponent({
  name: 'SortingIcon',
  emits: ['sortEvent'],
  components: {},
  props: {
    sortAsc: {
      type: Boolean,
      default: false
    }
  },
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
