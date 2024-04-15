<template>
  <div id="exemption-declaration">
    <p>Select the reason for the non-residential exemption.</p>
    <v-radio-group
      id="non-residential-type-options"
      v-model="declarationOption"
      class="mt-5 pr-1"
      inline
      hideDetails="true"
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
      <p class="py-6">
        Indicate what happened to the home
      </p>

      <v-radio-group
        id="destroyed-reason"
        v-model="declarationReason"
        class="mt-n2 ml-n2"
        hideDetails="true"
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
        />
      </v-radio-group>
    </template>

    <!-- Converted Options -->
    <template v-if="declarationOption === NonResOptions.CONVERTED">
      <p class="py-6">
        The home is presently used as
      </p>

      <v-radio-group
        id="converted-reason"
        v-model="declarationReason"
        class="mt-n2 ml-n2"
        hideDetails="true"
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
        persistentHint
        hint="Enter the date this manufactured home was no longer in use."
        @emitDate="declarationDate = $event"
      />
    </template>
  </div>
</template>
<script setup lang="ts">
import { Ref, ref, watch } from 'vue'
import { InputFieldDatePicker } from '@/components/common'
import { NonResConvertedReasons, NonResDestroyedReasons, NonResOptions } from '@/enums'
import { FormIF } from '@/interfaces'

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
}>()

/** Component Refs **/
const otherTextFieldRef:Ref<FormIF> = ref(null)
const declarationDateRef:Ref<typeof InputFieldDatePicker> = ref(null)

/** Component State **/
const declarationOption = ref('')
const declarationReason = ref('')
const otherReasonText = ref('')
const declarationDate = ref('')

/** Watch Declaration Option and reset Declaration Reasons on Change **/
watch(() => declarationOption.value, () => {
  declarationReason.value = ''
  otherReasonText.value = ''
  declarationDateRef.value?.clearDate()
})

/** Watch each ref property individually and emit an event when it changes **/
watch(declarationOption, (val) => { emits('updateOption', val) })
watch(declarationReason, (val) => { emits('updateReason', val) })
watch(otherReasonText, (val) => { emits('updateOther', val) })
watch(declarationDate, (val) => { emits('updateDate', val) })

/** Watch Validation flag to prompt component validation **/
watch(() => props.validate, (val: boolean) => {
  if (val) {
    declarationDateRef.value.validate()
    otherTextFieldRef.value.validate()
  }
})
</script>
