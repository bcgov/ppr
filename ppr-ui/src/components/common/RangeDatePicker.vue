<template>
  <v-card
    ref="datePicker"
    class="date-selection registration-date"
    elevation="6"
    flat
  >
    <v-row noGutters>
      <v-col>
        <b
          class="date-selection__heading"
          :class="{ 'picker-err': startDate === null && datePickerErr }"
        >
          Select Start Date:
        </b>
        <BaseDatePicker
          class="date-selection__picker mt-2"
          :error="startDate === null && datePickerErr"
          :resetTrigger="resetTrigger"
          :setMaxDate="endDate || defaultMaxDate"
          @selectedDate="startDate = $event"
        />
      </v-col>
      <v-col class="pl-4">
        <b
          class="date-selection__heading"
          :class="{ 'picker-err': endDate === null && datePickerErr }"
        >
          Select End Date:
        </b>
        <BaseDatePicker
          class="date-selection__picker mt-2"
          :error="endDate === null && datePickerErr"
          :resetTrigger="resetTrigger"
          :setMinDate="startDate"
          :setMaxDate="defaultMaxDate"
          @selectedDate="endDate = $event"
        />
      </v-col>
    </v-row>
    <v-row
      class="pt-2 pr-2"
      noGutters
      justify="end"
    >
      <v-col cols="auto">
        <v-btn
          class="date-selection-btn bold"
          color="primary"
          size="small"
          variant="plain"
          @click="submitDateRange()"
        >
          <b>OK</b>
        </v-btn>
        <v-btn
          class="date-selection-btn ml-4"
          color="primary"
          size="small"
          variant="plain"
          @click="resetDateRange()"
        >
          Cancel
        </v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
// external
import { Ref, ref, watch } from 'vue'
// internal
import { BaseDatePicker } from '@/components/common'

const props = defineProps<{
  defaultEndDate?: Date
  defaultStartDate?: Date
  defaultMaxDate?: Date
  reset?: boolean
}>()
const emit = defineEmits<{(e: 'submit', value: { endDate: Date, startDate: Date }): void}>()

const datePickerErr = ref(false)
const endDate: Ref<Date> = ref(props.defaultEndDate || null)
const startDate: Ref<Date> = ref(props.defaultStartDate || null)
const resetTrigger = ref(false)

const resetDateRange = (): void => {
  resetTrigger.value = !resetTrigger.value
  datePickerErr.value = false
  emit('submit', { endDate: null, startDate: null })
}
watch(() => props.reset, () => { resetDateRange() })

const submitDateRange = (): void => {
  if (!startDate.value || !endDate.value) {
    datePickerErr.value = true
    return
  }
  datePickerErr.value = false
  emit('submit', { endDate: endDate.value, startDate: startDate.value })
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.date-selection {
  border-radius: 5px;
  z-index: 1001;
  left: 50%;
  margin-top: 100px;
  overflow: auto;
  padding: 20px 10px 8px 30px;
  position: absolute;
  transform: translate(-50%, 0);
  background-color: white;
  width: 700px;

  &__heading.picker-err {
    color: $error;
  }
}
</style>
