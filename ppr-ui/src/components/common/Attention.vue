<template>
  <div>
    <h2 :data-test-id="`${sectionId}-title`">
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${config.title}`}}
    </h2>
    <p class="mt-2" :data-test-id="`${sectionId}-description`">
      {{ config.description }}
    </p>

    <v-form ref="attentionForm" v-model="isFormValid" :data-test-id="`${sectionId}-form`">
      <v-card
        flat
        rounded
        class="mt-6 pt-10 px-7 pb-5"
        :class="{ 'border-error-left': setShowErrors }"
        :data-test-id="`${sectionId}-card`"
      >
        <FormField
          :sectionId="sectionId"
          :initialValue="initialValue"
          :inputTitle="config.inputTitle"
          :inputLabel="config.inputLabel"
          :inputColWidth="hasWiderInput ? 10 : 9"
          :labelColWidth="hasWiderInput ? 2 : 3"
          :rules="maxLength(40)"
          :showErrors="setShowErrors"
          @updateValue="$emit('setStoreProperty', $event)"
        />
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRefs, computed, reactive, ref, watch } from 'vue-demi'
import { useInputRules } from '@/composables'
import { FormField } from '@/components/common'
import { attentionConfigManufacturer, attentionConfig } from '@/resources/attnRefConfigs'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'Attention',
  components: { FormField },
  emits: ['isAttentionValid', 'setStoreProperty'],
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
  setup (props, { emit }) {
    const attentionForm = ref(null)
    const { isRoleManufacturer } = storeToRefs(useStore())
    const { maxLength } = useInputRules()

    const localState = reactive({
      config: isRoleManufacturer.value ? attentionConfigManufacturer : attentionConfig,
      isFormValid: false,
      setShowErrors: computed((): boolean => props.validate && !localState.isFormValid)
    })

    watch(() => localState.isFormValid, (val: boolean) => {
      emit('isAttentionValid', val)
    })

    watch(() => props.validate, (validate: boolean) => {
      validate && attentionForm.value?.validate()
    })

    return {
      attentionForm,
      maxLength,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
