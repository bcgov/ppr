<template>
  <div id="remarks-container">
    <h2>Remarks</h2>
    <p class="mt-2">{{ description }}</p>
    <v-form ref="remarksForm" v-model="isFormValid">
      <v-card
        id="remarks-card"
        class="py-6 px-8 rounded"
        :class="{ 'border-error-left': showBorderError }"
        flat
      >
        <v-row>
          <v-col cols="2">
              <label
                for="remarks-textarea"
                class="generic-label"
                :class="{ 'error-text': showBorderError }"
              >Add Remarks</label>
            </v-col>
          <v-col cols="10">
            <v-textarea
              id="remarks-textarea"
              v-model.trim="remarks"
              filled
              :counter="remarksMaxLength"
              :rules="maxLength(remarksMaxLength)"
              :label="label"
              class="pl-1"
              data-test-id="remarks-textarea"
              :error-messages="showRemarksRequiredMsg ? 'Enter remarks' : ''"
            ></v-textarea>
          </v-col>
        </v-row>
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { useInputRules } from '@/composables'
import { FormIF } from '@/interfaces'
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'

export default defineComponent({
  name: 'Remarks',
  emits: ['isValid', 'setStoreProperty'],
  props: {
    unitNoteRemarks: {
      type: String,
      required: true
    },
    description: {
      type: String
    },
    validate: {
      type: Boolean,
      default: false
    },
    isRequired: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { maxLength } = useInputRules()

    const remarksForm = ref(null) as FormIF

    const localState = reactive({
      remarksMaxLength: 420,
      label: props.isRequired ? 'Remarks' : 'Remarks (Optional)',
      isFormValid: false,
      remarks: props.unitNoteRemarks,
      showBorderError: computed(() => props.validate && !localState.isFormValid),
      showRemarksRequiredMsg: computed((): boolean => props.validate && props.isRequired && localState.remarks === '')
    })

    watch(
      () => localState.remarks,
      (val: string) => {
        emit('setStoreProperty', val)
      }
    )

    watch(() => props.validate, async (val) => {
      if (val) remarksForm.value?.validate()
    }, { immediate: true })

    watch(() => localState.isFormValid, (val: boolean) => {
      emit('isValid', val)
    })

    return {
      maxLength,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
