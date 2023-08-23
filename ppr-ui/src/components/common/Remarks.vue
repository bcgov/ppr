<template>
  <div id="remarks-container">
    <h2>
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${content.title}`}}
    </h2>
    <p class="mt-2">{{ content.description }}</p>
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
              >
                {{ content.sideLabel }}
              </label>
            </v-col>
          <v-col cols="10">
            <v-textarea
              id="remarks-textarea"
              v-model.trim="remarks"
              filled
              :rules="maxLength(remarksMaxLength)"
              name="name"
              :counter="remarksMaxLength"
              label="Remarks (Optional)"
              class="pl-1"
              data-test-id="remarks-textarea"
            ></v-textarea>

            <v-checkbox
              v-if="showAdditionalRemarksCheckbox"
              id="additional-remarks-checkbox"
              class="py-0 pr-0 pl-2 ma-0"
              v-model="hasAdditionalRemarks"
              :label="content.checkboxLabel"
              :hide-details="true"
            />
          </v-col>
        </v-row>
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { useInputRules } from '@/composables'
import { ContentIF } from '@/interfaces'
import { computed, defineComponent, reactive, toRefs, watch } from 'vue-demi'

export default defineComponent({
  name: 'Remarks',
  emits: ['isValid', 'setStoreProperty'],
  props: {
    unitNoteRemarks: {
      type: String,
      required: true
    },
    additionalRemarks: {
      type: String,
      required: false
    },
    sectionNumber: {
      type: Number,
      required: false
    },
    content: {
      type: Object as () => ContentIF,
      default: () => {}
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
  setup (props, { emit }) {
    const { maxLength } = useInputRules()

    const localState = reactive({
      isFormValid: false,
      remarks: props.unitNoteRemarks,
      hasAdditionalRemarks: !!props.additionalRemarks,
      remarksMaxLength: computed((): number =>
        props.showAdditionalRemarksCheckbox ? 420 - props.content.checkboxLabel.length : 420),
      showBorderError: computed(() => props.validate && !localState.isFormValid)
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
        emit('setStoreProperty', { key: 'additionalRemarks', value: val ? props.content.checkboxLabel + '. ' : '' })
      }
    )

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
