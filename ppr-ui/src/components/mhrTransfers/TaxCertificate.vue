<template>
  <FormCard
    label="Tax Certificate"
    class="mhr-tax-certificate mt-8"
    :show-errors="validate && state.selectedFutureDate === ''"
  >
    <template #formSlot>
      <InputFieldDatePicker
        id="expiry-date-picker"
        ref="expiryDatePickerRef"
        title="Tax Certificate Expiry Date"
        :initial-value="props.expiryDate"
        :input-rules="state.dateRules"
        :min-date="state.minDate"
        :max-date="state.maxDate"
        :disable-picker="state.certificateWaived"
        @emit-date="setDate($event)"
        @emit-cancel="state.selectedFutureDate = ''"
        @emit-clear="state.selectedFutureDate = ''"
      />

      <!-- Waive Certificate Checkbox -->
      <v-checkbox
        v-if="isRoleStaffReg"
        v-model="state.certificateWaived"
        class="ml-n3 mb-n8"
        label="Certificate requirement waived"
      />
    </template>
  </FormCard>
</template>

<script setup lang="ts">

import { useInputRules } from "@/composables"
import { calendarDates } from "@/utils"
import { reactive, computed, watch, ref, nextTick, onMounted } from 'vue'
import { FormCard, InputFieldDatePicker } from "../common"
import { useStore } from "@/store/store"
import type { FormIF } from "@/interfaces"
import { storeToRefs } from 'pinia'

const props = defineProps<{
  expiryDate?: string,
  validate: boolean
}>()

const expiryDatePickerRef = ref(null) as FormIF

const emit = defineEmits(['isValid', 'setStoreProperty', 'waiveCertificate'])

const { isRoleStaffReg, getMhrTransportPermitHomeLocation } = storeToRefs(useStore())
const { required } = useInputRules()

const state = reactive({
  certificateWaived: false,
  selectedFutureDate: '',
  dateRules: computed(() => !state.certificateWaived ? required('This field is required') : []),
  minDate: computed(() => isRoleStaffReg.value ? null : calendarDates.tomorrow),
  maxDate: computed(() => isRoleStaffReg.value ? null : calendarDates.startOfNextYear)
})

onMounted(() => {
  // Set the initial value of the certificate waived checkbox if the user is a staff member
  if (isRoleStaffReg.value) {
    state.certificateWaived = getMhrTransportPermitHomeLocation.value?.waiveCertificate
  }
})

watch(() => props.validate, async () => {
  expiryDatePickerRef.value?.validate()
})

watch(() => state.certificateWaived, async (val: boolean) => {
  if (val){
    emit('setStoreProperty', '')
    expiryDatePickerRef.value.clearDate()
    await nextTick()
    expiryDatePickerRef.value?.validate()
  }
  emit('isValid', val)
  emit('waiveCertificate', val)
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
