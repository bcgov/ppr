<template>
  <v-form
    ref="form"
    :attach="attach"
    class="date-picker-form"
  >
    <v-menu
      v-model="displayPicker"
      persistent
      :closeOnContentClick="false"
      transition="scale-transition"
      location="bottom right"
    >
      <template #activator="{ props, isActive }">
        <v-text-field
          id="date-text-field"
          ref="dateTextField"
          v-bind="props"
          v-model="dateText"
          appendInnerIcon="mdi-calendar"
          :class="{'date-text-field-pointer': (isActive || disablePicker)}"
          :clearable="clearable"
          :clearIcon="'mdi-close'"
          :errorMessages="errorMsg"
          :error="!!errorMsg"
          :label="title"
          :rules="inputRules"
          :disabled="isActive || disablePicker"
          :hint="hint"
          :persistentHint="persistentHint"
          persistentClear
          readonly
          variant="filled"
          color="primary"
        />
      </template>
      <v-card
        flat
        class="pb-2"
        width="500"
      >
        <BaseDatePicker
          id="date-picker-calendar"
          :defaultSelectedDate="defaultDate"
          :setMinDate="minDate ? new Date(minDate) : null"
          :setMaxDate="maxDate ? new Date(maxDate): null"
          @selected-date="dateHandler"
        />

        <span class="float-right">
          <v-btn
            id="btn-done"
            variant="plain"
            color="primary"
            @click="emitDate"
          >
            <strong>OK</strong>
          </v-btn>
          <v-btn
            id="btn-cancel"
            variant="plain"
            color="primary"
            @click="emitCancel"
          >
            Cancel
          </v-btn>
        </span>
      </v-card>
    </v-menu>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { useRoute } from 'vue-router'
import { convertDate, dateToYyyyMmDd, yyyyMmDdToDate } from '@/utils'
import { FormIF } from '@/interfaces'
import BaseDatePicker from '@/components/common/BaseDatePicker.vue'

export default defineComponent({
  name: 'InputFieldDatePicker',
  components: { BaseDatePicker },
  props: {
    attach: { type: String, default: null },
    title: { type: String, default: '' },
    errorMsg: { type: String, default: null },
    inputRules: { type: Array, default: () => [] },
    disablePicker: { type: Boolean, default: false },
    initialValue: { type: String, default: '' },
    minDate: { type: String, default: '' },
    maxDate: { type: String, default: '' },
    hint: { type: String, default: '' },
    persistentHint: { type: Boolean, default: false },
    clearable: { type: Boolean, default: false }
  },
  emits: ['emitDate', 'emitCancel'],
  setup (props, context) {
    const route = useRoute()
    const form = ref(null) as FormIF
    const dateTextField = ref(null)
    const localState = reactive({
      defaultDate: props.initialValue && yyyyMmDdToDate(props.initialValue) || null,
      dateText: props.initialValue && convertDate(props.initialValue, false, false) || null,
      displayPicker: false
    })


    /** Handle emitted Date and format for display **/
    const dateHandler = (val: Date): void => {
      localState.defaultDate = val
      localState.dateText =  convertDate(val, false, false)
    }
    /** Clear local model after each action. */
    const clearDate = (): void => {
      localState.dateText = ''
      localState.displayPicker = false
    }

    /** Triggers the form validation, exposed for easier . */
    const validate = (): boolean => {
      return form.value.validate()
    }

    /** Returns whether date validation passes. */
    const isDateValid = (): boolean => {
      return dateTextField.value?.valid
    }

    /** Emit date to add or remove. */
    const emitDate = (): void => {
      localState.defaultDate && context.emit('emitDate', dateToYyyyMmDd(localState.defaultDate))
      localState.displayPicker = false
    }

    /** Emit cancel event and clear the date. */
    const emitCancel = (): void => {
      context.emit('emitCancel', true)
      clearDate()
    }

    /** Watch route and close picker on update **/
    watch(() => route, (): void => {
      localState.displayPicker = false
    })

    return {
      dateHandler,
      form,
      dateTextField,
      emitDate,
      emitCancel,
      validate,
      isDateValid,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

:deep(.dp__menu) {
  border: none;
}

:deep(.dp__main) {
  display: block;
}

// Unset inner widths of BaseDatePicker for reactive implementations
:deep(.base-date-picker), :deep(.base-date-picker__header), :deep(.dp__main), :deep(.base-date-picker__select) {
  width: 100%;
}
</style>
