<template>
  <FormCard
    id="add-edit-notice"
    :label="`${addEditLabel} Notice`"
    :class="{ 'border-error-left' : isInvalidAddEditNotice }"
  >
    <template #formSlot>
      <!-- Validation Error message -->
      <p
        v-if="isInvalidAddEditNotice"
        class="error-text mt-1 mb-3 fs-12"
      >
        Indicate if the there is a Notice of Lien and Charge or Proceedings
      </p>

      <v-form
        id="notice-form"
        ref="noticeFormRef"
        v-model="isFormValid"
      >
        <!-- Notice Type Selector -->
        <v-row
          noGutters
          class="justify-end"
        >
          <v-col>
            <v-radio-group
              id="notice-type-options"
              v-model="securitiesActNoticeType"
              class="mt-0 pr-1"
              inline
              hideDetails="true"
              :disabled="isAmendment && isEditing && notice?.action !== ActionTypes.ADDED"
              :rules="required('')"
            >
              <v-radio
                id="lien-option"
                class="radio-one"
                :class="{'selected-radio': securitiesActNoticeType === SaNoticeTypes.NOTICE_OF_LIEN}"
                label="Lien and Charge"
                :value="SaNoticeTypes.NOTICE_OF_LIEN"
              />
              <v-radio
                id="proceedings-option"
                class="radio-two"
                :class="{'selected-radio': securitiesActNoticeType === SaNoticeTypes.NOTICE_OF_PROCEEDINGS}"
                label="Order or Proceedings"
                :value="SaNoticeTypes.NOTICE_OF_PROCEEDINGS"
              />
            </v-radio-group>

            <InputFieldDatePicker
              class="mt-8 mr-3"
              :title="'Effective Date (Optional)'"
              :initialValue="effectiveDateTime?.split('T')[0]"
              :minDate="null"
              :maxDate="localTodayDate(new Date(), true)"
              @emitCancel="effectiveDateTime = ''"
              @emitDate="effectiveDateTime = $event"
            />
          </v-col>
        </v-row>

        <!-- Actions -->
        <v-row
          noGutters
          class="justify-end mt-5 mr-3"
        >
          <v-btn
            id="cancel-add-edit-notice"
            class="mr-3 px-5"
            variant="outlined"
            @click="emits('cancel')"
          >
            Cancel
          </v-btn>
          <v-btn
            id="submit-add-edit-notice"
            class="px-5 font-weight-bold"
            @click="submitAddEditNotice()"
          >
            Done
          </v-btn>
        </v-row>
      </v-form>
    </template>
  </FormCard>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { FormCard, InputFieldDatePicker } from '@/components/common'
import { AddEditSaNoticeIF, FormIF } from '@/interfaces'
import { ActionTypes, SaNoticeTypes } from '@/enums'
import { useInputRules } from '@/composables'
import { localTodayDate } from '@/utils'
import { isEqual } from 'lodash'

/** Composables **/
const { required } = useInputRules()

/** Refs **/
const noticeFormRef: FormIF = ref(null)

/** Emits **/
const emits = defineEmits<{
  cancel: [value: boolean]
  done: [value: AddEditSaNoticeIF]
}>()

/** Props **/
const props = withDefaults(defineProps<{
  isEditing?: boolean,
  notice?: AddEditSaNoticeIF,
  isAmendment?: boolean
}>(), {
  isEditing: false,
  notice: null,
  isAmendment: false
})

/** Local Properties **/
const validateAddEditNotice = ref(false)
const isFormValid = ref(false)
const securitiesActNoticeType = ref(props.notice?.securitiesActNoticeType || null)
const effectiveDateTime = ref(props.notice?.effectiveDateTime || '')
const addEditLabel = computed(() => props.isEditing ? 'Edit' : 'Add')
const isInvalidAddEditNotice = computed( () => validateAddEditNotice.value && !isFormValid.value)
const isAmendedEffectiveDate = computed( () => {
  return effectiveDateTime.value
    ? !isEqual(props.notice?.effectiveDateTime?.split('T')[0], effectiveDateTime.value.split('T')[0])
    : !!props.notice?.effectiveDateTime
})

/** Local Functions **/
const submitAddEditNotice = async () => {
  validateAddEditNotice.value = true
  await noticeFormRef.value.validate()

  if(isFormValid.value) {
    emits('done', {
      ...props.notice,
      securitiesActNoticeType: securitiesActNoticeType.value,
      effectiveDateTime: effectiveDateTime.value,
      securitiesActOrders: props.notice?.securitiesActOrders || [],
      ...props.isAmendment && {
        ...props.isEditing && isAmendedEffectiveDate.value && props.notice.action !== ActionTypes.ADDED && {
          noticeId: props.notice?.noticeId,
          action: ActionTypes.EDITED
        },
        ...!props.isEditing && !props.notice?.action && {
          action: ActionTypes.ADDED
        }
      }
    })
  }
}


</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
