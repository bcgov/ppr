<template>
  <v-form :attach="attach" ref="form" class="date-picker-form">
    <v-menu v-model="displayPicker"
            :close-on-click="false"
            :close-on-content-click="false"
            :nudge-top="nudgeTop"
            :nudge-bottom="nudgeBottom"
            :nudge-left="nudgeLeft"
            :nudge-right="nudgeRight"
            transition="scale-transition"
            offset-y
            bottom
            min-width="290"
    >
      <template v-slot:activator="{ on }">
        <span :class="{'date-text-field-pointer': enableSelector}" v-on="enableSelector && on">
          <v-text-field id="date-text-field"
                        ref="dateTextField"
                        append-icon="mdi-calendar"
                        autocomplete="chrome-off"
                        :clearable="clearable"
                        :error-messages="errorMsg"
                        :error="!!errorMsg"
                        :value="displayDate"
                        :label="title"
                        :name="Math.random()"
                        :rules="inputRules"
                        :disabled="disablePicker"
                        :hint="hint"
                        :persistent-hint="persistentHint"
                        @click:clear="emitClear()"
                        @keydown="$event.preventDefault()"
                        @keyup.enter="emitDate(dateText)"
                        readonly
                        filled
          />
        </span>
      </template>
      <v-date-picker id="date-picker-calendar" width="490" v-model="dateText" :min="minDate" :max="maxDate">
        <template v-slot:default>
          <div>
            <v-btn id="btn-done" text color="primary" @click="emitDate(dateText)"><strong>OK</strong></v-btn>
            <v-btn id="btn-cancel" text color="primary" @click="emitCancel()">Cancel</v-btn>
          </div>
        </template>
      </v-date-picker>
    </v-menu>
  </v-form>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { yyyyMmDdToPacificDate } from '@/utils'
// eslint-disable-next-line no-unused-vars
import { FormIF } from '@/interfaces'

export default defineComponent({
  name: 'SharedDatePicker',
  emits: ['emitDate', 'emitCancel', 'emitClear'],
  props: {
    attach: { type: String, default: null },
    title: { type: String, default: '' },
    errorMsg: { type: String, default: null },
    inputRules: { type: Array, default: () => [] },
    disablePicker: { type: Boolean, default: false },
    initialValue: { type: String, default: '' },
    minDate: { type: String, default: '' },
    maxDate: { type: String, default: '' },
    nudgeTop: { type: Number, default: null },
    nudgeBottom: { type: Number, default: null },
    nudgeRight: { type: Number, default: null },
    nudgeLeft: { type: Number, default: null },
    hint: { type: String, default: '' },
    persistentHint: { type: Boolean, default: false },
    clearable: { type: Boolean, default: false }
  },
  setup (props, context) {
    const localState = reactive({
      dateText: null,
      displayPicker: false,
      /** The display Date. */
      displayDate: computed((): string => {
        return yyyyMmDdToPacificDate(localState.dateText, true)
      }),
      /** True when the picker is not displayed or disabled. */
      enableSelector: computed((): boolean => {
        return !localState.displayPicker && !props.disablePicker
      })
    })

    const form = ref(null) as FormIF
    const dateTextField = ref(null)

    /** Clear local model after each action. */
    const clearDate = (): void => {
      localState.dateText = ''
      localState.displayPicker = false
    }

    /** Triggers the form validation. */
    const validateForm = (): boolean => {
      // @ts-ignore - function exists
      return context.refs.form.validate()
    }

    /** Returns whether date validation passes. */
    const isDateValid = (): boolean => {
      // @ts-ignore - function exists
      return context.refs?.dateTextField?.valid
    }

    /** Called before component is mounted. */
    onBeforeMount((): void => {
      localState.dateText = props.initialValue
    })

    /** Emit date to add or remove. */
    const emitDate = (date: string): void => {
      context.emit('emitDate', date)
      localState.displayPicker = false
    }

    /** Emit cancel event and clear the date. */
    const emitCancel = (): void => {
      context.emit('emitCancel', true)
      clearDate()
    }

    /** Emit clear event and clear the date. */
    const emitClear = (): void => {
      context.emit('emitClear', true)
      clearDate()
    }

    watch(() => localState.dateText, (dateText: string): void => {
      context.emit('emitDateSync', dateText)
    })

    watch(() => context.root.$route, (): void => {
      localState.displayPicker = false
    })

    return {
      form,
      dateTextField,
      emitDate,
      emitCancel,
      emitClear,
      validateForm,
      isDateValid,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.date-text-field-pointer {
  cursor: pointer;

  // disable pointer events when disabled
  .v-text-field.v-input--is-disabled {
    pointer-events: none;
  }
  // enable pointer events when enabled
  .v-text-field:not(.v-input--is-disabled) {
    pointer-events: auto;
  }
}

::v-deep .v-card__actions {
  justify-content: flex-end;
}

::v-deep .v-input .v-label {
  font-weight: normal;
  color: $gray7;
}

::v-deep .v-icon.v-icon {
  color: $app-blue
}

::v-deep .v-picker__title__btn:not(.v-picker__title__btn--active) {
  opacity: 1;
}

::v-deep .v-date-picker-table__current {
  border-color: $app-blue !important;
}

::v-deep .v-date-picker-table__current .v-btn__content{
  color: $app-blue !important;
}

::v-deep .theme--light.v-date-picker-table th {
  color: $gray9
}

::v-deep .v-date-picker-table .v-btn {
  color: $gray7
}

::v-deep .theme--light.v-btn:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
  background-color: $app-blue !important;
  border-color: $app-blue !important;
  color: white !important;
}

::v-deep .v-btn:not(.v-btn--text):not(.v-btn--outlined).v-btn--active:before {
  opacity: 0;
}

::v-deep .v-icon.v-icon.v-icon--link {
  cursor: text;
}

::v-deep .v-icon.v-icon.v-icon--link.mdi-close {
  cursor: pointer;
}

::v-deep .theme--light.v-icon.v-icon.v-icon--disabled {
  color: $app-blue !important;
}

::v-deep .v-input--is-disabled {
  opacity: 0.4;
}

::v-deep .theme--light.v-text-field.v-input--is-disabled .v-input__slot:before {
  border-image: none;
}

::v-deep .v-text-field.v-input--is-readonly .v-input__slot:before {
  border-style: solid !important;
}
</style>
