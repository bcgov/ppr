<template>
  <div id="remarks-container">
    <h2>
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${content.title}` }}
    </h2>
    <p class="mb-6">
      {{ content.description }}
    </p>
    <v-form
      ref="remarksForm"
      v-model="isFormValid"
    >
      <v-card
        id="remarks-card"
        class="py-10 px-8 rounded"
        :class="{ 'border-error-left': showBorderError }"
        flat
      >
        <v-row no-gutters>
          <v-col cols="3">
            <label
              for="remarks-textarea"
              class="generic-label side-label"
              :class="{ 'error-text': showBorderError }"
            >
              {{ content.sideLabel }}
            </label>
          </v-col>
          <v-col cols="9">
            <v-textarea
              id="remarks-textarea"
              v-model.trim="remarks"
              variant="filled"
              color="primary"
              :rules="remarksRules"
              name="name"
              :counter="remarksMaxLength"
              :label="isRequired ? 'Remarks' : 'Remarks (Optional)'"
              data-test-id="remarks-textarea"
            />

            <v-checkbox
              v-if="showAdditionalRemarksCheckbox"
              v-model="hasAdditionalRemarks"
              class="py-0 pr-0 ma-0"
              :label="content.checkboxLabel"
              hide-details
              data-test-id="additional-remarks-checkbox"
            >
              <template #label>
                <div class="pt-5">
                  <span>
                    {{ content.checkboxLabel }}
                  </span>
                </div>
              </template>
            </v-checkbox>
          </v-col>
        </v-row>
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { useInputRules } from '@/composables'
import type { ContentIF, FormIF } from '@/interfaces'
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'

export default defineComponent({
  name: 'Remarks',
  props: {
    unitNoteRemarks: {
      type: String,
      required: true
    },
    additionalRemarks: {
      type: String,
      default: ''
    },
    sectionNumber: {
      type: Number,
      default: null
    },
    content: {
      type: Object as () => ContentIF,
      default: () => {}
    },
    isRequired: {
      type: Boolean,
      required: false
    },
    validate: {
      type: Boolean,
      default: false
    },
    showAdditionalRemarksCheckbox: {
      type: Boolean,
      default: false
    }
  },
  emits: ['isValid', 'setStoreProperty'],
  setup (props, { emit }) {
    const remarksForm = ref(null) as FormIF

    const { maxLength, required, customRules } = useInputRules()

    const localState = reactive({
      isFormValid: false,
      remarks: props.unitNoteRemarks,
      hasAdditionalRemarks: !!props.additionalRemarks,
      remarksMaxLength: computed((): number =>
        props.showAdditionalRemarksCheckbox ? 420 - props.content.checkboxLabel.length : 420),
      showBorderError: computed(() => props.validate && !localState.isFormValid),
      remarksRules: computed(() => {
        return props.isRequired
          ? customRules(maxLength(localState.remarksMaxLength), required('This field is required'))
          : maxLength(localState.remarksMaxLength)
      }
      )
    })

    watch(
      () => localState.remarks,
      (val: string) => {
        emit('setStoreProperty', { key: 'remarks', value: val })
      }
    )

    watch(
      () => localState.hasAdditionalRemarks,
      (val: boolean) => {
        emit('setStoreProperty', { key: 'additionalRemarks', value: val ? props.content.checkboxLabel + '.' : '' })
      }
    )

    watch(() => localState.isFormValid, (val: boolean) => {
      emit('isValid', val)
    })

    watch(() => props.validate, async (val) => {
      if (val) remarksForm.value?.validate()
    })

    return {
      remarksForm,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
