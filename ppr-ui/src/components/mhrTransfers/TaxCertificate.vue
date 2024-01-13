<template>
  <div class="mhr-tax-certificate mt-8">
    <FormCard
      label="Tax Certificate"
      :showErrors="false"
      :class="{'border-error-left': false}"
    >
      <template #formSlot>
        <InputFieldDatePicker
          id="expiry-date-picker"
          ref="expiryDatePicker"
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
  </div>
</template>

<script setup lang="ts">

import { useInputRules } from "@/composables"
import { calendarDates } from "@/utils"
import { reactive, computed, watch } from "vue"
import { FormCard, InputFieldDatePicker } from "../common"
import { useStore } from "@/store/store"

const props = defineProps<{
  expiryDate?: string
}>()

const emit = defineEmits(['updateTaxCertificate'])

const { isRoleStaffReg } = useStore()
const { required } = useInputRules()

const state = reactive({
  selectedFutureDate: '',
  minDate: calendarDates.tomorrow,
  maxDate: computed(() => isRoleStaffReg ? null : calendarDates.endOfYear)
})

watch(() => state.selectedFutureDate, val => {
  emit('updateTaxCertificate', val)
})

const setDate = (futureDate: string) => {
  state.selectedFutureDate = futureDate
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

</style>
