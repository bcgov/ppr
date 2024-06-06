<template>
  <FormCard
    id="add-edit-court-order"
    :label="`${addEditLabel} Court Order`"
  >
    <template #formSlot>
      <v-form
        ref="courtOrderFormRef"
        v-model="isValidCourtOrderForm"
        class="pb-6 px-0"
      >
        <v-row
          noGutters
        >
          <v-col>
            <v-text-field
              id="txt-court-name"
              v-model.trim="courtOrderData.courtName"
              variant="filled"
              color="primary"
              label="Court Name"
              hint="For example: Supreme Court of British Columbia"
              persistentHint
              :rules="nameRules"
            />
          </v-col>
        </v-row>
        <v-row
          noGutters
        >
          <v-col
            class="pt-4"
          >
            <v-text-field
              id="txt-court-registry"
              v-model.trim="courtOrderData.courtRegistry"
              variant="filled"
              color="primary"
              label="Court Registry"
              hint="The location (city) of the court. For example: Richmond"
              persistentHint
              :rules="registryRules"
            />
          </v-col>
        </v-row>
        <v-row
          noGutters
        >
          <v-col
            class="pt-4"
          >
            <v-text-field
              id="txt-court-file-number"
              v-model.trim="courtOrderData.fileNumber"
              variant="filled"
              color="primary"
              label="Court File Number"
              persistentHint
              :rules="fileNumberRules"
            />
          </v-col>
        </v-row>
        <v-row
          noGutters
        >
          <v-col
            class="pt-4"
          >
            <InputFieldDatePicker
              id="court-date-text-field"
              ref="datePickerRef"
              class="court-date-text-input"
              nudgeRight="40"
              title="Date of Order"
              :initialValue="courtOrderData?.orderDate.split('T')[0]"
              :minDate="null"
              :maxDate="localTodayDate(new Date(), true)"
              :persistentHint="true"
              :inputRules="required('This field is required')"
              :hint="'Enter the date of the order filing'"
              @emitDate="courtOrderData.orderDate = $event"
              @emitCancel="courtOrderData.orderDate = ''"
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
              v-model.trim="courtOrderData.effectOfOrder"
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
          @click="submitAddEditCourtOrder()"
        >
          Done
        </v-btn>
      </v-row>
    </template>
  </FormCard>
</template>

<script setup lang="ts">
import { computed, Ref, ref, watch } from 'vue'
import { FormCard, InputFieldDatePicker } from '@/components/common'
import { CourtOrderIF, FormIF } from '@/interfaces'
import { useInputRules } from '@/composables'
import { localTodayDate } from '@/utils'

/** Refs **/
const courtOrderFormRef: Ref<FormIF> = ref(null)
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
  courtOrderProp?: CourtOrderIF
}>(), {
  isEditing: false,
  courtOrderProp: null
})

/** Local Properties **/
const isValidCourtOrderForm = ref(false)
const validateAddEditCourtOrder = ref(false)
const courtOrderData: Ref<CourtOrderIF> = ref({
  courtOrder: true,
  courtName: '',
  courtRegistry: '',
  fileNumber: '',
  orderDate: '',
  effectOfOrder: ''
})
const addEditLabel = ref(computed(() => props.isEditing ? 'Edit' : 'Add'))
const isFormValid = computed(() => isValidCourtOrderForm.value && !!courtOrderData.value.orderDate)

/** Form Rules **/
const nameRules = customRules(
  required('This field is required'),
  minLength(5),
  maxLength(256)
)
const registryRules = customRules(
  required('This field is required'),
  minLength(5),
  maxLength(64)
)
const fileNumberRules = customRules(
  required('This field is required'),
  minLength(5),
  maxLength(20)
)
const effectOfOrderRules = computed(() => {
  return !!courtOrderData.value.effectOfOrder
    ? customRules(
      minLength(5),
      maxLength(512)
    )
    : []
})

/** Local Functions **/
const submitAddEditCourtOrder = async () => {
  validateAddEditCourtOrder.value = true
  await courtOrderFormRef.value.validate()
  await datePickerRef.value.validate()

  if (isFormValid.value) {
    emits('done', courtOrderData.value)
  }
}
watch(() => validateAddEditCourtOrder.value,  (val: boolean) => {
  if (val) emits('isValid', isFormValid.value)
})
watch(() => isFormValid.value,  (val: boolean) => {
  if (validateAddEditCourtOrder.value) emits('isValid', val)
})
watch(() => props.isEditing,  (val: boolean) => {
  if (val) courtOrderData.value = { ...props.courtOrderProp }
}, { immediate: true })

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
