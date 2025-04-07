<template>
  <div
    v-if="hasChanges"
    id="updated-badge-component"
  >
    <v-chip
      x-small
      variant="flat"
      color="primary"
      :data-test-id="`${action}-badge`"
    >
      <b class="fs-10">{{ action }}</b>
    </v-chip>
  </div>
</template>
<script setup lang="ts">
import type { PropType } from 'vue';
import { computed } from 'vue'
import type { BaseDataUnionIF } from '@/interfaces'
import { deepChangesComparison } from '@/utils'

const props = withDefaults(defineProps<{
  action?: string,
  baseline?: PropType<BaseDataUnionIF>
  currentState?: PropType<BaseDataUnionIF>,
  isCaseSensitive?: boolean
}>(), {
  action: 'CORRECTED',
  baseline: null,
  currentState: null,
  isCaseSensitive: false
})

/**
 * Is true when there is a difference between the baseline and current state
 * By default string comparisons are insensitive unless activated by isCaseSensitive Prop
 **/
const hasChanges = computed(() => {
  return deepChangesComparison(props.baseline, props.currentState, props.isCaseSensitive)
})
</script>
