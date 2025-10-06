<script setup lang="ts">
import { shallowRef, computed, watch, onMounted, ref } from 'vue'
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

const dateRange = computed({
  get: () => {
    if (props.modelValue && props.modelValue.start && props.modelValue.end) {
      return {
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
    return { start: undefined, end: undefined }
  },
  set: (value) => {
    if (value.start && value.end) {
      emit('update:modelValue', {
        start: {
          year: value.start.year,
          month: value.start.month,
          day: value.start.day
        },
        end: {
          year: value.end.year,
          month: value.end.month,
          day: value.end.day
        }
      })
    } else {
      emit('update:modelValue', null)
    }
  }
})

const customLabel = computed(() => {
  if (dateRange.value.start) {
    if (dateRange.value.end) {
      const startDate = df.format(dateRange.value.start.toDate(getLocalTimeZone()))
      const endDate = df.format(dateRange.value.end.toDate(getLocalTimeZone()))
      return `${startDate} - ${endDate}`
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

const open = ref(false)

const resetDateRange = () => {
  dateRange.value = { start: undefined, end: undefined }
}

watch(() => dateRange.value, (newValue) => {
  if (newValue.start && newValue.end) {
    // Close the popover when both dates are selected
    open.value = false
  }
}, { deep: true })
</script>

<template>
  <UPopover v-model:open="open">
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
