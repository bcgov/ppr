<template>
  <div
    v-if="hasChanges"
    id="updated-badge-component"
  >
    <v-chip
      xSmall
      variant="flat"
      color="primary"
      :data-test-id="`${action}-badge`"
    >
      <b class="fs-10">{{ action }}</b>
    </v-chip>
  </div>
</template>
<script setup lang="ts">
import { computed, PropType } from 'vue'
import { BaseDataUnionIF } from '@/interfaces'
import { deepChangesComparison } from '@/utils'
import { isEqual } from 'lodash'

const props = withDefaults(defineProps<{
  action?: string,
  baseline: PropType<BaseDataUnionIF>
  currentState: PropType<BaseDataUnionIF>,
  isCaseSensitive?: boolean
}>(), {
  action: 'CORRECTED',
  baseline: null,
  currentState: null,
  isCaseSensitive: false
})

/** Is true when there is a difference between the baseline and current state **/
const hasChanges = computed(() => {
  if (props.isCaseSensitive) {
    return !isEqual(props.baseline, props.currentState)
  }
  // deep case-insensitive comparison
  return deepChangesComparison(props.baseline, props.currentState)
})
</script>
