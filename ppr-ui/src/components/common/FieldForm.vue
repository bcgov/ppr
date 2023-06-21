<template>
  <section :id="sectionId" class="mt-13">
    <h2 :data-test-id="`${sectionId}-title`">
      {{ title }}
    </h2>
    <p class="mt-2" :data-test-id="`${sectionId}-description`">
      {{ description }}
    </p>

    <v-form ref="form" v-model="isFormValid" :data-test-id="`${sectionId}-form`">
      <v-card flat rounded class="mt-6 pt-10 px-7 pb-5" :data-test-id="`${sectionId}-card`"
        :class="{ 'border-error-left': setShowErrors }">
        <v-row no-gutters>
          <v-col cols="3">
            <label
              class="generic-label"
              :class="{ 'error-text': setShowErrors }"
              :data-test-id="`${sectionId}-label`"
            >
              {{ inputTitle }}
            </label>
          </v-col>
          <v-col cols="9">
            <v-text-field
              filled
              :label="inputLabel"
              v-model="inputModel"
              :rules="rules"
              :data-test-id="`${sectionId}-text-field`"
            />
          </v-col>
        </v-row>
      </v-card>
    </v-form>
  </section>
</template>

<script lang="ts">
import { FormIF } from '@bcrs-shared-components/interfaces'
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  watch
} from 'vue-demi'

export default defineComponent({
  name: 'FieldForm',
  emits: ['isValid'],
  props: {
    description: {
      type: String,
      required: true
    },
    initialValue: {
      type: String,
      required: false
    },
    inputTitle: {
      type: String,
      required: true
    },
    inputLabel: {
      type: String,
      required: true
    },
    rules: {
      type: Array,
      required: true
    },
    sectionId: {
      type: String,
      required: true
    },
    setValue: {
      type: Function,
      required: true
    },
    validate: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      required: true
    }
  },
  setup (props, { emit }) {
    const form = ref(null) as FormIF
    const localState = reactive({
      isFormValid: false,
      inputModel: props.initialValue || '',
      setShowErrors: computed(() => props.validate && !form.value?.validate())
    })

    watch(() => localState.inputModel, (val: string) => {
      props.setValue(val)
    })

    watch(() => localState.isFormValid, (val: boolean) => {
      emit('isValid', val)
    })

    return {
      form,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
