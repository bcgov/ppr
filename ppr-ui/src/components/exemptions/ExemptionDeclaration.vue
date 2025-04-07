<template>
  <div id="exemption-declaration">
    <p>Select the reason for the non-residential exemption.</p>
    <p
      v-if="validate && !declarationOption"
      class="error-text fs-14 mt-5"
    >
      Indicate if the home was destroyed or converted
    </p>
    <v-radio-group
      id="non-residential-type-options"
      v-model="declarationOption"
      class="mt-5 pr-1"
      inline
      hide-details="true"
    >
      <v-radio
        id="destroyed-option"
        class="radio-one"
        :class="{'selected-radio': NonResOptions === NonResOptions.DESTROYED}"
        :label="NonResOptions.DESTROYED"
        :value="NonResOptions.DESTROYED"
      />
      <v-radio
        id="converted-option"
        class="radio-two"
        :class="{'selected-radio': NonResOptions === NonResOptions.CONVERTED}"
        :label="NonResOptions.CONVERTED"
        :value="NonResOptions.CONVERTED"
      />
    </v-radio-group>

    <!-- Destroyed Options -->
    <template v-if="declarationOption === NonResOptions.DESTROYED">
      <p
        class="pt-6 pb-5"
      >
        Indicate what happened to the home
      </p>
      <p
        v-if="validate && !declarationReason"
        class="error-text fs-14 pb-5"
      >
        Select an option below
      </p>

      <v-radio-group
        id="destroyed-reason"
        v-model="declarationReason"
        class="mt-n2 ml-n2"
        hide-details="true"
        :error="validate && !declarationReason"
      >
        <v-radio
          v-for="reason in NonResDestroyedReasons"
          :id="`${reason}-radio`"
          :key="reason"
          :label="reason"
          :value="reason"
        />
        <v-text-field
          v-if="declarationReason === NonResDestroyedReasons.OTHER"
          id="destroyed-other-text"
          ref="otherTextFieldRef"
          v-model="otherReasonText"
          label="Please Specify"
          color="primary"
          class="mt-2 ml-7"
          :rules="otherFieldRules"
        />
      </v-radio-group>
    </template>

    <!-- Converted Options -->
    <template v-if="declarationOption === NonResOptions.CONVERTED">
      <p class="pt-6 pb-5">
        The home is presently used as
      </p>
      <p
        v-if="validate && !declarationReason"
        class="error-text fs-14 pb-5"
      >
        Select an option below
      </p>

      <v-radio-group
        id="converted-reason"
        v-model="declarationReason"
        class="mt-n2 ml-n2"
        hide-details="true"
        :error="validate && !declarationReason"
      >
        <v-radio
          v-for="reason in NonResConvertedReasons"
          :id="`${reason}-radio`"
          :key="reason"
          :label="reason"
          :value="reason"
        />
        <v-text-field
          v-if="declarationReason === NonResConvertedReasons.OTHER"
          id="converted-other-text"
          ref="otherTextFieldRef"
          v-model="otherReasonText"
          label="Please Specify"
          color="primary"
          class="mt-2 ml-7"
          :rules="otherFieldRules"
        />
      </v-radio-group>
    </template>

    <template v-if="!!declarationOption">
      <v-divider class="mt-4 mb-8" />

      <p class="generic-label">
        Date Home was {{ declarationOption }}
      </p>
      <InputFieldDatePicker
        id="declaration-date"
        ref="declarationDateRef"
        class="mt-4"
        title="Date"
        persistent-hint
        hint="Enter the date this manufactured home was no longer in use."
        :error-msg="(validate && !declarationDate)
          ? 'Enter the date this manufactured home was no longer in use.'
          : '' "
        :input-rules="dateFieldRules"
        :max-date="localTodayDate(new Date(), true)"
        @emit-date="declarationDate = $event"
        @emit-cancel="declarationDate = ''"
      />
    </template>
  </div>
</template>
<script setup lang="ts">
import type { Ref} from 'vue';
import { computed, nextTick, ref, watch } from 'vue'
import { InputFieldDatePicker } from '@/components/common'
import { NonResConvertedReasons, NonResDestroyedReasons, NonResOptions } from '@/enums'
import type { FormIF } from '@/interfaces'
import { useInputRules } from '@/composables'
import { localTodayDate } from '@/utils'

/** Props **/
const props = withDefaults(defineProps<{
  validate?: boolean
}>(), {
  validate: false
})

/** Emits **/
const emits = defineEmits<{
  updateOption: [value: string]
  updateReason: [value: string]
  updateOther: [value: string]
  updateDate: [value: string]
  updateValid: [value: boolean]
}>()

/** Composable **/
const { customRules, maxLength, required } = useInputRules()

/** Component Refs **/
const otherTextFieldRef:Ref<FormIF> = ref(null)
const declarationDateRef:Ref<typeof InputFieldDatePicker> = ref(null)

/** Component State **/
const declarationOption = ref('')
const declarationReason = ref('')
const otherReasonText = ref('')
const declarationDate = ref('')
const otherFieldRules = customRules(maxLength(75), required('This field is required'))
const dateFieldRules = customRules(required('Enter the date this manufactured home was no longer in use.'))
const isValidDeclaration = computed((): boolean => {
  const isReasonValid = declarationReason.value === NonResConvertedReasons.OTHER
    ? !!declarationReason.value && !!otherReasonText.value
    : !!declarationReason.value
  return !!declarationOption.value && !!isReasonValid && !!declarationDate.value
})

/** Watch Declaration Option and reset Declaration Reasons on Change **/
watch(() => declarationOption.value, () => {
  declarationReason.value = ''
  otherReasonText.value = ''
  declarationDateRef.value?.clearDate()
})

/** Watch Declaration Reason and reset Other Text on Change **/
watch(() => declarationReason.value, async (val) => {
  otherReasonText.value = ''
  if (props.validate && val === NonResDestroyedReasons.OTHER) {
    await nextTick()
    otherTextFieldRef.value?.validate()
  }
})

/** Watch each ref property individually and emit an event when it changes **/
watch(declarationOption, (val) => { emits('updateOption', val) })
watch(declarationReason, (val) => { emits('updateReason', val) })
watch(otherReasonText, (val) => { emits('updateOther', val) })
watch(declarationDate, (val) => { emits('updateDate', val) })
watch(isValidDeclaration, (val) => { emits('updateValid', val) })

/** Watch Validation flag to prompt component validation **/
watch(() => props.validate, (val: boolean) => {
  if (val && declarationOption.value) {
    otherTextFieldRef.value?.validate()
  }
})
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
:deep(.v-selection-control--error:not(.v-selection-control--disabled) .v-selection-control__input>.v-icon) {
  color: $gray7;
}
</style>
