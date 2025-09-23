<script setup lang="ts">
import { CalendarDate, DateFormatter } from '@internationalized/date'
import { dateRangePresets } from '@/resources'

const emit = defineEmits(["update:modelValue"])

const props = defineProps({
  datePlaceholder: {
    type: String,
    default: 'Filing Date',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  isRangedPicker: {
    type: Boolean,
    default: false,
  },
  size: {
    type: String,
    default: null,
  },
  isFilter: {
    type: Boolean,
    default: false,
  },
  isTrailing: {
    type: Boolean,
    default: false,
  }
})

const date = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
})

const datePlaceholder = computed(() => {
  return props.isRangedPicker
    ? date.value?.end
      ? `${format(date.value?.start, "d MMMM, yyy")} - ${format(
          date.value?.end,
          "d MMMM, yyy"
        )}`
      : "Date Range"
    : format(date.value, "d MMMM, yyy")
})


const handleSideBar = () => {}

</script>

<template>
  <UPopover>
    <UInput
      class="w-full font-medium"
      :placeholder="date ? datePlaceholder : props.datePlaceholder"
      type="text"
      icon="i-mdi-calendar"
      :disabled="disabled"
      :trailing="true"
      :size="size"
      :ui="{
        icon: { trailing: { pointer: '' } },
        size: { md: 'h-[44px]' },
      }"
    >
      <template #trailing>
        <UButton
          color="gray"
          variant="link"
          icon="i-mdi-cancel-circle text-primary"
          :padded="false"
          @click.stop=""
        />
        <UIcon name="i-mdi-calendar" :class="['w-5 h-5', isFilter ? '' : 'text-primary']" />
      </template>
    </UInput>
    
    <template #content>
      <div class="flex">
        <div 
          class="flex gap-y-3 flex-col px-5 items-start justify-center font-light"
        >
          <ULink
            v-for="(option, i) in dateRangePresets"
            :key="i"
            class="block"
            @click="handleSideBar(option.value)"
          >
            {{ option.label }}
          </ULink>

        </div>
        <UCalendar v-model="modelValue" class="p-2" :number-of-months="2" range />
      </div>
    </template>
  </UPopover>
</template>
