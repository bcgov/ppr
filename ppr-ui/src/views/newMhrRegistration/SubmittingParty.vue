<template>
  <div id="mhr-submitting-party">
    <section>
      <DocumentId
        id="mhr-submitting-party-doc-id"
        class="mt-10"
        :documentId="documentId || ''"
        :content="{
          title: '1. Document ID',
          description: 'Enter the 8-digit Document ID number.',
          sideLabel: 'Document ID',
          hintText: 'Enter the 8-digit Document ID number'
        }"
        :validate="validateDocId"
        @setStoreProperty="documentId = $event"
        @isValid="setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID, $event)"
      />
    </section>

    <section
      id="mhr-add-submitting-party"
      class="mt-10"
    >
      <ContactInformation
        :contactInfo="getMhrRegistrationSubmittingParty"
        :content="submittingPartyRegistrationContent"
        :validate="validateSubmitter"
        :sectionNumber="2"
        @setStoreProperty="setMhrRegistrationSubmittingParty"
        @isValid="setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.SUBMITTER_VALID, $event)"
      />
    </section>

    <section
      id="mhr-submitting-party-reference"
      class="mt-10"
    >
      <Attention
        sectionId="mhr-attention"
        hasWiderInput
        :initialValue="getMhrAttentionReference"
        :sectionNumber="3"
        :validate="validateRefNum"
        @isAttentionValid="setAttentionValidation"
        @setStoreProperty="setMhrAttentionReference"
      />
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { Attention, ContactInformation, DocumentId } from '@/components/common'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'
import { useStore } from '@/store/store'
import { useInputRules } from '@/composables'
import { validateDocumentID } from '@/utils'
import { MhrDocIdResponseIF, FormIF } from '@/interfaces'
import { storeToRefs } from 'pinia'
import { submittingPartyRegistrationContent } from '@/resources'

export default defineComponent({
  name: 'SubmittingParty',
  components: {
    DocumentId,
    Attention,
    ContactInformation
  },
  setup () {
    const {
      // Actions
      setMhrRegistrationDocumentId,
      setMhrRegistrationSubmittingParty,
      setMhrAttentionReference
    } = useStore()
    const {
      // Getters
      getMhrAttentionReference,
      getMhrRegistrationDocumentId,
      getMhrRegistrationValidationModel,
      getMhrRegistrationSubmittingParty
    } = storeToRefs(useStore())
    const { maxLength } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      hasError,
      setValidation,
      getSectionValidation,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const documentIdForm = ref(null) as FormIF

    const localState = reactive({
      documentId: getMhrRegistrationDocumentId.value || '',
      isRefNumValid: false,
      loadingDocId: false,
      validateSubmitter: computed((): boolean => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.SUBMITTER_VALID)
      }),
      validateDocId: computed((): boolean => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID)
      }),
      validateRefNum: computed((): boolean => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.REF_NUM_VALID)
      })
    })

    watch(() => localState.documentId, async (val: string) => {
      localState.loadingDocId = false
      setMhrRegistrationDocumentId(val)
    }, { immediate: true }
    )

    watch(() => localState.validateDocId, () => {
      documentIdForm.value?.validate()
    })

    const setAttentionValidation = (val: boolean) => {
      setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.REF_NUM_VALID, val)
    }

    const scrollOnValidationUpdates = () => {
      scrollToInvalid(MhrSectVal.SUBMITTING_PARTY_VALID, 'mhr-submitting-party')
    }

    watch(() => localState.validateSubmitter, () => {
      setTimeout(scrollOnValidationUpdates, 300)
    }, { deep: true })

    return {
      documentIdForm,
      MhrCompVal,
      MhrSectVal,
      getMhrRegistrationSubmittingParty,
      setMhrRegistrationSubmittingParty,
      setValidation,
      submittingPartyRegistrationContent,
      maxLength,
      hasError,
      getMhrAttentionReference,
      getSectionValidation,
      setMhrAttentionReference,
      setAttentionValidation,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
