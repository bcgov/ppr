<template>
  <div id="remarks-container">
    <h2>Remarks</h2>
    <p class="mt-2">{{ description }}</p>
    <v-form ref="remarksForm" v-model="isFormValid">
      <v-card
        id="remarks-card"
        class="py-6 px-8 rounded"
        :class="{ 'border-error-left': showErrors }"
        flat
      >
        <v-row>
          <v-col cols="2">
              <label
                for="remarks-textarea"
                class="generic-label"
                :class="{ 'error-text': showErrors }"
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
      isFormValid: false,
      remarks: props.unitNoteRemarks,
      showErrors: computed(() => props.validate && !localState.isFormValid)
    })

    watch(
      () => localState.remarks,
      (val: string) => {
        props.setStoreProperty(val)
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
