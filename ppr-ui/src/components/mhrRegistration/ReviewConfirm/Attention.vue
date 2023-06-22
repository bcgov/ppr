<template>
  <section :id="sectionId" class="mt-13">
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
        <FieldForm
          :section-id="sectionId"
          :initial-value="getMhrAttentionReference"
          :input-title="config.inputTitle"
          :input-label="config.inputLabel"
          :rules="maxLength(40)"
          :set-value="setMhrAttentionReference"
          :show-errors="setShowErrors"
        />
      </v-card>
    </v-form>
  </section>
</template>

<script lang="ts">
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { defineComponent, toRefs, computed, reactive, ref, watch } from 'vue-demi'
import { useInputRules } from '@/composables'
import { FieldForm } from '@/components/common'
import { attentionConfig, attentionConfigManufacturer } from '@/resources/attnRefConfigs'

export default defineComponent({
  name: 'Attention',
  components: { FieldForm },
  emits: ['isAttentionValid'],
  props: {
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
    const { setMhrAttentionReference } = useStore()
    const { getMhrAttentionReference, isRoleManufacturer } = storeToRefs(useStore())
    const { maxLength } = useInputRules()

    const localState = reactive({
      config: computed(() => isRoleManufacturer.value ? attentionConfigManufacturer : attentionConfig),
      isFormValid: false,
      setShowErrors: computed(() => props.validate && !localState.isFormValid)
    })

    watch(() => localState.isFormValid, (val: boolean) => {
      emit('isAttentionValid', val)
    })

    watch(() => props.validate, (validate: boolean) => {
      validate && attentionForm.value?.validate()
    })

    return {
      attentionForm,
      getMhrAttentionReference,
      maxLength,
      setMhrAttentionReference,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
