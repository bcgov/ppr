<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import type { PropType } from 'vue'

const props = defineProps({
  options: {
    type: Array as PropType<any>,
    required: true,
  },
  valueKey: {
    type: String,
    required: true,
  },
  labelKey: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: false,
    default: "",
  },
})


const selected = ref([])

const items = computed(() => {
  return props.options.filter(option => !option.isFixed)
})

const emit = defineEmits(['change']) 

const handleCheckboxChange = (value: any, checked: boolean) => {
  if (checked) {
    // Add to selection if not already present
    if (!selected.value.includes(value)) {
      selected.value.push(value)
    }
  } else {
    // Remove from selection
    const index = selected.value.indexOf(value)
    if (index > -1) {
      selected.value.splice(index, 1)
    }
  }
  emit('change', selected.value)
}

onMounted(() => {
  selected.value = props.options
    .filter(option => !option.isFixed)
    .map(option => option[props.valueKey])
})
</script>
<template>
  <USelect
    class="text-gray-700 text-light"
    :placeholder="label"
    :items="items"
    :value-key="valueKey"
    :label-key="labelKey"
    size="lg"
    multiple
    trailing-icon="i-mdi-arrow-drop-down"
  >
  <div v-if="label" class="px-2">{{ label }}</div>
  <template #item="{item}">
    <UCheckbox
      :model-value="selected.includes(item[valueKey])"
      :name="item[valueKey]"
      :label="item[labelKey]"
      @update:model-value="(checked) => handleCheckboxChange(item[valueKey], checked)"
    />
  </template>
  </USelect>
</template>
