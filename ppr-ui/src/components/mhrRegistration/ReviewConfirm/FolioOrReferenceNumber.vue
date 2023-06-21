<template>
  <FieldForm
    sectionId="mhr-folio-or-reference-number"
    :description="folioOrRefConfig.description"
    :initialValue="getFolioOrReferenceNumber"
    :inputTitle="folioOrRefConfig.inputTitle"
    :inputLabel="folioOrRefConfig.inputLabel"
    @isValid="setRefNumValidation"
    :rules="maxLength(30)"
    :setValue="setFolioOrReferenceNumber"
    :validate="validate"
    :title="`${sectionNumber ? sectionNumber + '.' : ''} ${folioOrRefConfig.title}`"
  />
 </template>

<script lang="ts">
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { defineComponent, toRefs, PropType } from 'vue-demi'
import { useInputRules, useMhrValidations } from '@/composables'
import { FieldForm } from '@/components/common'
import { folioOrRefConfig } from '@/resources/attnRefConfigs'
import { MhrSectVal } from '@/composables/mhrRegistration/enums'

export default defineComponent({
  name: 'FolioOrReferenceNumber',
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
    const { setFolioOrReferenceNumber } = useStore()
    const { getFolioOrReferenceNumber, getMhrRegistrationValidationModel } = storeToRefs(useStore())
    const { MhrCompVal, setValidation } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { maxLength } = useInputRules()
    const setRefNumValidation = (isValid: boolean) => {
      setValidation(props.mhrSect, MhrCompVal.REF_NUM_VALID, isValid)
    }

    return {
      folioOrRefConfig,
      getFolioOrReferenceNumber,
      maxLength,
      setRefNumValidation,
      setFolioOrReferenceNumber
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
