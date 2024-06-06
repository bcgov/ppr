<template>
  <FormCard
    id="add-edit-commission-order"
    :label="`${addEditLabel} Securities Commission Order`"
  >
    <template #formSlot>
      <v-form
        ref="commissionOrderFormRef"
        v-model="isValidCommissionOrderForm"
        class="pb-6 px-0"
      >
        <v-row noGutters>
          <v-col>
            <v-text-field
              id="commission-order-number"
              v-model.trim="commissionOrderData.fileNumber"
              variant="filled"
              color="primary"
              label="Commission Order Number"
              persistentHint
              :rules="fileNumberRules"
            />
          </v-col>
        </v-row>
        <v-row noGutters>
          <v-col class="pt-4">
            <InputFieldDatePicker
              id="court-date-text-field"
              ref="datePickerRef"
              class="court-date-text-input"
              nudgeRight="40"
              title="Date of Order"
              :initialValue="commissionOrderData?.orderDate.split('T')[0]"
              :minDate="null"
              :maxDate="localTodayDate(new Date(), true)"
              :persistentHint="true"
              :inputRules="required('This field is required')"
              :hint="'Enter the date of the order filing'"
              @emitDate="commissionOrderData.orderDate = $event"
              @emitCancel="commissionOrderData.orderDate = ''"
            />
          </v-col>
        </v-row>
        <v-row
          noGutters
        >
          <v-col
            class="pt-4"
          >
            <v-textarea
              id="effect-of-order"
              v-model.trim="commissionOrderData.effectOfOrder"
              class="pt-2"
              color="primary"
              variant="filled"
              label="Effect of Order (Optional)"
              counter="512"
              persistentCounter
              :rules="effectOfOrderRules"
            >
              <template #counter="{ counter }">
                <span>Characters: {{ counter }}</span>
              </template>
            </v-textarea>
          </v-col>
        </v-row>
      </v-form>

      <!-- Actions -->
      <v-row
        noGutters
        class="justify-end mt-5 mr-3"
      >
        <v-btn
          id="cancel-add-edit-order"
          class="mr-3 px-5"
          variant="outlined"
          @click="emits('cancel')"
        >
          Cancel
        </v-btn>
        <v-btn
          id="submit-add-edit-order"
          class="px-5 font-weight-bold"
          @click="submitAddEditCommissionOrder()"
        >
          Done
        </v-btn>
      </v-row>
    </template>
  </FormCard>
</template>

<script setup lang="ts">
import { computed, Ref, ref, watch } from 'vue'
import { FormCard } from '@/components/common'
import { CourtOrderIF, FormIF } from '@/interfaces'
import { useInputRules } from '@/composables'
import { localTodayDate } from '@/utils'
import { InputFieldDatePicker } from '@/components/common'

/** Refs **/
const commissionOrderFormRef: Ref<FormIF> = ref(null)
const datePickerRef: Ref<FormIF> = ref(null)

/** Composables **/
const { customRules, required, minLength, maxLength } = useInputRules()

/** Emits **/
const emits = defineEmits<{
  cancel: [value: boolean]
  done: [value: CourtOrderIF]
  isValid: [value: boolean]
}>()

/** Props **/
const props = withDefaults(defineProps<{
  isEditing?: boolean,
  commissionOrderProp?: CourtOrderIF
}>(), {
  isEditing: false,
  commissionOrderProp: null
})

/** Local Properties **/
const isValidCommissionOrderForm = ref(false)
const validateAddEditCommissionOrder = ref(false)
const commissionOrderData: Ref<any> = ref({
  courtOrder: false,
  fileNumber: '',
  orderDate: '',
  effectOfOrder: ''
})
const addEditLabel = ref(computed(() => props.isEditing ? 'Edit' : 'Add'))
const isFormValid = computed(() => isValidCommissionOrderForm.value && !!commissionOrderData.value.orderDate)

/** Form Rules **/
const fileNumberRules = customRules(
  required('This field is required'),
  minLength(5),
  maxLength(20)
)
const effectOfOrderRules = computed(() => {
  return !!commissionOrderData.value.effectOfOrder
    ? customRules(
      minLength(5),
      maxLength(512)
    )
    : []
})

/** Local Functions **/
const submitAddEditCommissionOrder = async () => {
  validateAddEditCommissionOrder.value = true
  await commissionOrderFormRef.value.validate()
  await datePickerRef.value.validate()

  if (isFormValid.value) {
    emits('done', commissionOrderData.value)
  }
}
watch(() => validateAddEditCommissionOrder.value,  (val: boolean) => {
  if (val) emits('isValid', isFormValid.value)
})
watch(() => isFormValid.value,  (val: boolean) => {
  if (validateAddEditCommissionOrder.value) emits('isValid', val)
})
watch(() => props.isEditing,  (val: boolean) => {
  if (val) commissionOrderData.value = { ...props.commissionOrderProp }
}, { immediate: true })

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
