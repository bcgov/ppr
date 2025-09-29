<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
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


const selected = ref([])

const items = computed(() => {
  return props.options.filter(option => !option.isFixed)
})

const emit = defineEmits(['change']) 
onMounted(() => {
  selected.value = props.options
    .filter(option => !option.isFixed)
    .map(option => option[props.valueAttribute])
})
</script>
<template>
  <USelect
    v-model="selected"
    class="text-gray-700 text-light"
    :placeholder="label"
    :items="items"
    :value-key="valueAttribute"
    :label-key="optionAttribute"
    size="lg"
    multiple
    trailing-icon="i-mdi-arrow-drop-down"
    @update:model-value="emit('change', $event)"
  >
  <div v-if="label" class="px-2">{{ label }}</div>
  </USelect>
</template>
