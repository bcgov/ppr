<template>
  <FormCard
    id="add-edit-commission-order"
    :label="`${addEditLabel} Commission Order`"
    :class="{ 'border-error-left' : false }"
  >
    <template #formSlot />
  </FormCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { FormCard } from '@/components/common'

/** Props **/
const props = withDefaults(defineProps<{
  isEditing?: boolean,
  commissionOrder?: any
}>(), {
  isEditing: false,
  commissionOrder: null
})

/** Local Properties **/
const addEditLabel = computed(() => props.isEditing ? 'Edit' : 'Add')

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
