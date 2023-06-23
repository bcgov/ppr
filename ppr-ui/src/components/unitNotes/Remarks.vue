<template>
  <div id="remarks-container">
    <h2>Remarks</h2>
    <p class="mt-2">{{ description }}</p>
    <v-form ref="remarksForm" v-model="isRemarksFormValid">
      <v-card
        id="remarks-card"
        class="py-6 px-8 rounded"
        :class="{ 'border-error-left': validateRemarks }"
        flat
      >
        <v-row>
          <v-col cols="2">
              <label
                for="remarks-textarea"
                class="generic-label"
                :class="{ 'error-text': validateRemarks }"
              >Add Remarks</label>
            </v-col>
          <v-col cols="10">
            <v-textarea
              id="remarks-textarea"
              v-model.trim="remarks"
              filled
              :rules="maxLength(350)"
              name="name"
              counter="350"
              label="Remarks (Optional)"
              class="pl-1"
              data-test-id="remarks-textarea"
            ></v-textarea>
          </v-col>
        </v-row>
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { useInputRules } from '@/composables'
import { computed, defineComponent, reactive, toRefs, watch } from 'vue-demi'

export default defineComponent({
  name: 'Remarks',
  emits: ['isValid'],
  props: {
    unitNoteRemarks: {
      type: String,
      required: true
    },
    description: {
      type: String
    },
    setStoreProperty: {
      type: Function,
      required: true
    },
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { maxLength } = useInputRules()

    const localState = reactive({
      isRemarksFormValid: false,
      remarks: props.unitNoteRemarks,
      validateRemarks: computed(() => props.validate && !localState.isRemarksFormValid)
    })

    watch(
      () => localState.remarks,
      (val: string) => {
        props.setStoreProperty(val)
      }
    )

    watch(() => localState.isRemarksFormValid, (val: boolean) => {
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
