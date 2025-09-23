<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { PropType } from 'vue'

const props = defineProps({
  options: {
    type: Array as PropType<any>,
    required: true,
  },
  valueAttribute: {
    type: String,
    required: true,
  },
  optionAttribute: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: false,
    default: "",
  },
})
const emit = defineEmits(["change"]) 

const selected = ref([])

onMounted(() => {
  try {
    selected.value = props.options.map((option) => option[props.valueAttribute])
  } catch (error) {
    console.error(error)
  }
})
</script>
<template>
  <USelect
    class="text-gray-700 text-light"
    :placeholder="label"
    :items="options"
    :value-key="valueAttribute"
    :label-key="optionAttribute"
    size="lg"
    multiple
    :ui="{
      icon: { trailing: { pointer: '' } },
      size: { md: 'h-[44px]' },
      color: 'primary'
    }"
    trailing-icon="i-mdi-arrow-drop-down"
    @update:model-value="emit('change', $event)"
  >
    <template #item="{ item, selected: isSelected }">
      <UCheckbox
        :model-value="isSelected"
        :name="item[valueAttribute]"
        :label="item[optionAttribute]"
      />
    </template>
  </USelect>
</template>
