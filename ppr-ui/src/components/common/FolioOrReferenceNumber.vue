<template>
  <div>
    <h2 :data-test-id="`${sectionId}-title`">
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${folioOrRefConfig.title}` }}
    </h2>
    <p
      class="mt-2"
      :data-test-id="`${sectionId}-description`"
    >
      {{ folioOrRefConfig.description }}
    </p>

    <v-form
      ref="folioOrRefForm"
      v-model="isFormValid"
      :data-test-id="`${sectionId}-form`"
    >
      <v-card
        flat
        rounded
        class="mt-6 pt-10 px-7 pb-5"
        :class="{ 'border-error-left': setShowErrors }"
        :data-test-id="`${sectionId}-card`"
      >
        <FormField
          :section-id="sectionId"
          :initial-value="initialValue"
          :input-title="folioOrRefConfig.inputTitle"
          :input-label="folioOrRefConfig.inputLabel"
          :input-col-width="hasWiderInput ? 10 : undefined"
          :label-col-width="hasWiderInput ? 2 : undefined"
          :rules="maxLength(30)"
          :show-errors="setShowErrors"
          @updateValue="$emit('setStoreProperty', $event)"
        />
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRefs, ref, computed, reactive, watch } from 'vue'
import { useInputRules } from '@/composables'
import FormField from '@/components/common/FormField.vue'
import { folioOrRefConfig } from '@/resources/attnRefConfigs'

export default defineComponent({
  name: 'FolioOrReferenceNumber',
  components: { FormField },
  props: {
    initialValue: {
      type: String,
      default: ''
    },
    hasWiderInput: {
      type: Boolean,
      default: false
    },
    sectionId: {
      type: String,
      required: true
    },
    sectionNumber: {
      type: Number,
      required: false
    },
    validate: {
      type: Boolean,
      default: false
    }
  },
  emits: ['isFolioOrRefNumValid', 'setStoreProperty'],
  setup (props, { emit }) {
    const { maxLength } = useInputRules()

    const folioOrRefForm = ref(null)

    const localState = reactive({
      isFormValid: false,
      setShowErrors: computed((): boolean => props.validate && !localState.isFormValid)
    })

    watch(() => localState.isFormValid, (val: boolean) => {
      emit('isFolioOrRefNumValid', val)
    })

    watch(() => props.validate, (validate: boolean) => {
      validate && folioOrRefForm.value?.validate()
    })

    return {
      folioOrRefConfig,
      folioOrRefForm,
      maxLength,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
