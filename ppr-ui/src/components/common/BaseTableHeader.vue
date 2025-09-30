<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { FilterTypes } from '@/enums'

const props = defineProps<{
  columnData: any,
  modelValue: string | number | undefined,
  isSorted: string | boolean,
  showClearFilterButton: boolean
}>()

const emit = defineEmits(['filterTable', 'toggleSort', 'resetFilter']) 
const update = (value: any) => {
  emit('filterTable', props.columnData.id, value)
}

const cleanField = () => {
  emit('filterTable', props.columnData.id, '')
}

const resetFilters = () => {
  emit('resetFilter')
}
const filterValue = computed({
  get: () => props.modelValue,
  set: (value) => {
    emit('filterTable', props.columnData.id, value)
  }
})

const showXButton = computed(() => {
  return !!props.modelValue
})
const sortIcon = computed(() => {
  if(!props.isSorted) return
  return props.isSorted === 'desc'? 'i-mdi-arrow-down' : 'i-mdi-arrow-up'
})
</script>

<template>
  <div
    class="flex flex-col gap-2"
  >
    <div
      class="text-gray-600 text-sm"
      :title="columnData.header || columnData.filter.placeholder"
    >
      <div
        :class="[
          'flex items-center gap-1',
          columnData.id === 'actions' ? 'justify-center' : ''
        ]"
        @click.stop="emit('toggleSort')"
      >
        <div class="truncate">
          {{ columnData.filter.placeholder || columnData.header }}
        </div>
        <UIcon
          v-if="columnData.sortable && isSorted"
          :name="sortIcon"
          class="text-gray-500 cursor-pointer hover:text-gray-700"
        />
      </div>
    </div>
    <UInput
      v-if="columnData.filter.type == FilterTypes.TEXT_FIELD"
      :model-value="modelValue"
      :placeholder="columnData.filter.placeholder"
      size="lg"
      :ui="{base: 'px-2 placeholder:text-bcGovGray-700 font-medium'}"
      @update:model-value="update"
    >
      <template #trailing>
        <UButton
          v-if="showXButton"          
          color="gray"
          variant="link"
          class="text-primary"
          icon="i-mdi-cancel-circle"
          :padded="false"
          @click="cleanField"
        />
      </template>
    </UInput>

    <div 
      v-else-if="columnData.filter.type === FilterTypes.SELECT"
      class="relative w-full"
    >
      <USelect
        :key="columnData.filter.key || 'select'"
        :items="columnData.filter.options"
        :model-value="modelValue"
        :placeholder="columnData.filter.placeholder"
        size="lg"
        class="custom-select font-medium pr-8 w-full"
        :ui="{ item: 'hover:text-blue-500 hover:bg-bcGovGray-100', placeholder: 'text-bcGovGray-700'}"
        @update:model-value="update"
      />
      <UButton
        v-if="showXButton"
        variant="link"
        class="text-primary absolute right-6 top-1/2 transform -translate-y-1/2 z-20"
        icon="i-mdi-cancel-circle"
        :padded="false"
        @click="cleanField"
      />
    </div>

    <RangeDatePickerPreset
      v-else-if="columnData.filter.type === FilterTypes.DATE_PICKER"
      v-model="filterValue"
      :placeholder="columnData.filter.placeholder"
      size="lg"
    />

    <UButton
      v-else-if="columnData.filter.type === FilterTypes.ACTIONS"
      :class="{ 'opacity-0 pointer-events-none': !showClearFilterButton }"
      size="md"
      variant="outline"
      class="px-2"
      icon="i-mdi-cancel-circle"
      @click="resetFilters()"
    >
      Clear Filter
    </UButton>
  </div>
</template>

