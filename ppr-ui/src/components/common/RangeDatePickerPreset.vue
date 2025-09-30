<script setup lang="ts">
import { shallowRef, computed, watch, onMounted } from 'vue'
import {
  CalendarDate,
  today,
  DateFormatter,
  getLocalTimeZone
} from '@internationalized/date'
import { calculatePreviousDate } from '@/utils'
import { dateRangePresets } from '@/resources'

const props = defineProps({
  placeholder: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: null,
  },
  modelValue: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const df = new DateFormatter('en-US', {
  month: 'short',
  day: 'numeric'
})

const dateRange = shallowRef({start: undefined, end: undefined})

onMounted(() => {
  // Initialize dateRange from modelValue if provided
  if (props.modelValue && props.modelValue.start && props.modelValue.end) {
    dateRange.value = {
      start: new CalendarDate(
        props.modelValue.start.year,
        props.modelValue.start.month,
        props.modelValue.start.day
      ),
      end: new CalendarDate(
        props.modelValue.end.year,
        props.modelValue.end.month,
        props.modelValue.end.day
      )
    }
  }
})

const customLabel = computed(() => {
  if (dateRange.value.start) {
    if (dateRange.value.end) {
      return `${df.format(dateRange.value.start.toDate(getLocalTimeZone()))}
        - ${df.format(dateRange.value.end.toDate(getLocalTimeZone()))}`
    } else {
      return df.format(dateRange.value.start.toDate(getLocalTimeZone()))
    }
  }
  return props.placeholder
})

const handleSideBar = (option) => {
  dateRange.value = {
    start: calculatePreviousDate(option),
    end: today()
  }
}

const resetDateRange = () => {
  dateRange.value = { start: undefined, end: undefined }
}
// Watch for changes in dateRange and emit the updated value
watch(dateRange, (newValue) => {
  if (newValue.start && newValue.end) {
    emit('update:modelValue', {
      start: {
        year: newValue.start.year,
        month: newValue.start.month,
        day: newValue.start.day
      },
      end: {
        year: newValue.end.year,
        month: newValue.end.month,
        day: newValue.end.day
      }
    })
  } else if (!newValue.start && !newValue.end) {
    // Emit null when both dates are cleared
    emit('update:modelValue', null)
  }
}, { deep: true })
</script>

<template>
  <UPopover>
    <UInput
      :size="size"
      :model-value="customLabel"
      :ui="{ base: 'text-left placeholder:text-bcGovGray-700 font-medium' }"
    >
      <template #trailing>
        <UButton
          v-if="dateRange.start"
          variant="link"
          class="text-primary"
          icon="i-mdi-cancel-circle"
          :padded="false"
          @click="resetDateRange()"
        />
        <UIcon name="i-mdi-calendar" class="w-5 h-5" />
      </template>
    </UInput>
      <template #content>
        <div class="flex">
          <div class="flex gap-y-3 flex-col px-5 items-start justify-center font-light">
            <ULink
              v-for="(option, i) in dateRangePresets"
              :key="i"
              class="block"
              @click="handleSideBar(option.value)"
            >
              {{ option.label }}
            </ULink>
          </div>
          <UCalendar v-model="dateRange" class="p-2" range :number-of-months="2" />
        </div>
      </template>
  </UPopover>
</template>
