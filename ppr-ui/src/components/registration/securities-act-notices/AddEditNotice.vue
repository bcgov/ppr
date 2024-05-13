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
        Indicate if the there is a Notice of Lien or Proceedings
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
              v-model="noticeType"
              class="mt-0 pr-1"
              inline
              hideDetails="true"
              :rules="required('')"
            >
              <v-radio
                id="lien-option"
                class="radio-one"
                :class="{'selected-radio': noticeType === SaNoticeTypes.NOTICE_OF_LIEN}"
                label="Lien"
                :value="SaNoticeTypes.NOTICE_OF_LIEN"
              />
              <v-radio
                id="proceeding-option"
                class="radio-two"
                :class="{'selected-radio': noticeType === SaNoticeTypes.NOTICE_OF_PROCEEDINGS}"
                label="Proceedings"
                :value="SaNoticeTypes.NOTICE_OF_PROCEEDINGS"
              />
            </v-radio-group>

            <InputFieldDatePicker
              class="mt-8 mr-3"
              :title="'Effective Date (Optional)'"
              :initialValue="effectiveDate"
              @emitCancel="effectiveDate = ''"
              @emitDate="effectiveDate = $event"
            />
          </v-col>
        </v-row>

        <!-- Actions -->
        <v-row
          noGutters
          class="justify-end mt-5 mr-3"
        >
          <v-btn
            class="mr-3 px-5 font-weight-bold"
            variant="outlined"
            @click="emits('cancel')"
          >
            Cancel
          </v-btn>
          <v-btn
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
import { SaNoticeTypes } from '@/enums'
import { useInputRules } from '@/composables'

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
  notice?: AddEditSaNoticeIF
}>(), {
  isEditing: false,
  notice: null
})

/** Local Properties **/
const validateAddEditNotice = ref(false)
const isFormValid = ref(false)
const noticeType = ref(props.notice?.noticeType || null)
const effectiveDate = ref(props.notice?.effectiveDate || '')
const addEditLabel = computed(() => props.isEditing ? 'Edit' : 'Add')
const isInvalidAddEditNotice = computed( () => {
  return validateAddEditNotice.value && !isFormValid.value
})

/** Local Functions **/
const submitAddEditNotice = async () => {
  validateAddEditNotice.value = true
  await noticeFormRef.value.validate()

  if(isFormValid.value) {
    emits('done', {
      noticeType: noticeType.value,
      effectiveDate: effectiveDate.value
    })
  }
}


</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
