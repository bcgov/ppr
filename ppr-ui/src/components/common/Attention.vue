<template>
  <div>
    <h3
      class="fs-18"
      :data-test-id="`${sectionId}-title`"
    >
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${config.title}` }}
    </h3>
    <p
      class="mt-2"
      :data-test-id="`${sectionId}-description`"
    >
      {{ config.description }}
    </p>

    <v-form
      ref="attentionForm"
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
          :input-title="config.inputTitle"
          :input-label="config.inputLabel"
          :input-col-width="hasWiderInput ? 9 : undefined"
          :label-col-width="hasWiderInput ? 3 : undefined"
          :rules="maxLength(40)"
          :show-errors="setShowErrors"
          @update-value="$emit('setStoreProperty', $event)"
        />
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { defineComponent, toRefs, computed, reactive, ref, watch } from 'vue'
import { useInputRules } from '@/composables'
import { FormField } from '@/components/common'
import { attentionConfigManufacturer, attentionConfig } from '@/resources/attnRefConfigs'
import type { AttnRefConfigIF } from '@/interfaces'

export default defineComponent({
  name: 'Attention',
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
      default: null,
      required: false
    },
    validate: {
      type: Boolean,
      default: false
    },
    configOverride: {
      type: Object as () => AttnRefConfigIF,
      default: () => null
    }
  },
  emits: ['isAttentionValid', 'setStoreProperty'],
  setup (props, { emit }) {
    const attentionForm = ref(null)
    const { isRoleManufacturer } = storeToRefs(useStore())
    const { maxLength } = useInputRules()

    const localState = reactive({
      config: props.configOverride || isRoleManufacturer.value ? attentionConfigManufacturer : attentionConfig,
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
@use '@/assets/styles/theme.scss' as *;
</style>
