<template>
  <FormCard
    id="add-edit-court-order"
    :label="`${addEditLabel} Court Order`"
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
  courtOrder?: any
}>(), {
  isEditing: false,
  courtOrder: null
})

/** Local Properties **/
const addEditLabel = computed(() => props.isEditing ? 'Edit' : 'Add')

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
