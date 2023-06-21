<template>
  <FieldForm
    sectionId="mhr-attention"
    :description="config.description"
    :initialValue="getMhrAttentionReference"
    :inputTitle="config.inputTitle"
    :inputLabel="config.inputLabel"
    @isValid="setAttenionValidation"
    :rules="maxLength(40)"
    :setValue="setMhrAttentionReference"
    :title="`${sectionNumber ? sectionNumber + '.' : ''} ${config.title}`"
    :validate="validate"
  />
</template>

<script lang="ts">
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { defineComponent, toRefs, PropType, computed, reactive } from 'vue-demi'
import { useInputRules, useMhrValidations } from '@/composables'
import { FieldForm } from '@/components/common'
import { attentionConfig, attentionConfigManufacturer } from '@/resources/attnRefConfigs'
import { MhrSectVal } from '@/composables/mhrRegistration/enums'

export default defineComponent({
  name: 'Attention',
  components: { FieldForm },
  props: {
    mhrSect: {
      type: String as PropType<MhrSectVal>,
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
  setup (props) {
    const { setMhrAttentionReference } = useStore()
    const { getMhrAttentionReference, getMhrRegistrationValidationModel, isRoleManufacturer } = storeToRefs(useStore())
    const { MhrCompVal, setValidation } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { maxLength } = useInputRules()
    const setAttenionValidation = (isValid: boolean) => {
      setValidation(props.mhrSect, MhrCompVal.ATTENTION_VALID, isValid)
    }

    const localState = reactive({
      config: computed(() => isRoleManufacturer.value ? attentionConfigManufacturer : attentionConfig)
    })

    return {
      getMhrAttentionReference,
      maxLength,
      setAttenionValidation,
      setMhrAttentionReference,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
