<template>
  <FormCard
    label="Tax Certificate"
    class="mhr-tax-certificate mt-8"
    :showErrors="validate && state.selectedFutureDate === ''"
  >
    <template #formSlot>
      <InputFieldDatePicker
        id="expiry-date-picker"
        ref="expiryDatePickerRef"
        title="Tax Certificate Expiry Date"
        :initialValue="props.expiryDate"
        :inputRules="required('This field is required')"
        :minDate="state.minDate"
        :maxDate="state.maxDate"
        @emitDate="setDate($event)"
        @emitCancel="state.selectedFutureDate = ''"
        @emitClear="state.selectedFutureDate = ''"
      />
    </template>
  </FormCard>
</template>

<script setup lang="ts">

import { useInputRules } from "@/composables"
import { calendarDates } from "@/utils"
import { reactive, computed, watch, ref } from "vue"
import { FormCard, InputFieldDatePicker } from "../common"
import { useStore } from "@/store/store"
import { FormIF } from "@/interfaces"

const props = defineProps<{
  expiryDate?: string,
  validate: boolean
}>()

const expiryDatePickerRef = ref(null) as FormIF

const emit = defineEmits(['isValid', 'setStoreProperty'])

const { isRoleStaffReg } = useStore()
const { required } = useInputRules()

const state = reactive({
  selectedFutureDate: '',
  minDate: calendarDates.tomorrow,
  maxDate: computed(() => isRoleStaffReg ? null : calendarDates.startOfNextYear)
})

watch(() => props.validate, async () => {
  expiryDatePickerRef.value?.validate()
})

watch(() => state.selectedFutureDate, val => {
  emit('setStoreProperty', val)
  emit('isValid', !!val)
})

const setDate = (futureDate: string) => {
  state.selectedFutureDate = futureDate
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

</style>
