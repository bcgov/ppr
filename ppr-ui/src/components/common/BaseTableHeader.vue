<script setup lang="ts">
import { computed } from 'vue'
type Option = { label: string; value: any }

const props = defineProps<{
  type: FilterType
  modelValue?: any
  options?: Option[]
  placeholder?: string
  label?: string
  sortable?: boolean
  sortDirection?: 'asc' | 'desc' | undefined
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
  (e: 'toggle-sort'): void
}>()

const update = (value: any) => emit('update:modelValue', value)

const sortIcon = computed(() => {
  return 'i-mdi-arrow-up'
})
</script>

<template>
  <div
    class="flex flex-col gap-2"
  >
    <div
      class="text-gray-600 text-sm"
      :title="label || placeholder"
    >
      <div
        class="flex items-center gap-1"
        @click.stop="emit('toggle-sort')"
      >
        <div class="truncate">{{ label || placeholder }}</div>
        <UIcon
          v-if="sortable"
          :name="sortIcon"
          class="text-gray-500 cursor-pointer hover:text-gray-700"
        />
      </div>
    </div>
    <UInput
      v-if="type === FilterTypes.TEXT_FIELD"
      class="font-medium"
      :placeholder="placeholder"
      :model-value="modelValue"
      size="lg"
      @update:model-value="update"
    >
    <template #trailing>
      <UButton
        v-show="true"
        color="gray"
        variant="link"
        icon="i-mdi-cancel-circle text-primary"
        :padded="false"
      />
    </template>
    </UInput>

    <USelect
      v-else-if="type === FilterTypes.SELECT"
      :items="options"
      :model-value="modelValue"
      :placeholder="placeholder"
      size="lg"
      class="custom-select font-medium"
      :ui="{
        base: 'text-base'
      }"
      @update:model-value="update"
    >
    <template #trailing>
      <UButton
        v-show="true"
        variant="link"
        icon="i-mdi-cancel-circle text-primary"
        :padded="false"
        
      />
      <UIcon name="i-mdi-arrow-drop-down" class="w-5 h-5 " />
    </template>
    </USelect>

    <RangeDatePickerPreset
      v-else-if="type === FilterTypes.DATE_PICKER"
      :model-value="modelValue"
      size="lg"
      @update:model-value="update"
    />
  </div>
</template>

