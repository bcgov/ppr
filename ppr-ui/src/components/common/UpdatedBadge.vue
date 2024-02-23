<template>
  <div>
    <v-chip
      v-if="hasChanges"
      id="updated-badge-component"
      xSmall
      variant="flat"
      color="primary"
      :data-test-id="`${action.toLocaleLowerCase()}-badge`"
    >
      <b>{{ action.toUpperCase() }}</b>
    </v-chip>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { BaseDataUnionIF } from '@/interfaces'
import { deepChangesComparison } from '@/utils'

const props = withDefaults(defineProps<{
  action?: string,
  baseline: BaseDataUnionIF,
  currentState: BaseDataUnionIF
}>(), {
  action: 'Corrected',
  baseline: null,
  currentState: null
})

/** Is true when there is a difference between the baseline and current state **/
const hasChanges = computed(() => {
  return deepChangesComparison(props.baseline, props.currentState)
})
</script>
