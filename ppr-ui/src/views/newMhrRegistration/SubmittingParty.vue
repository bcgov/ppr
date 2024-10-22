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
    const { customRules, isNumber, maxLength, minLength, required } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      hasError,
      setValidation,
      getValidation,
      getSectionValidation,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const documentIdForm = ref(null) as FormIF

    const localState = reactive({
      documentId: getMhrRegistrationDocumentId.value || '',
      isRefNumValid: false,
      loadingDocId: false,
      isUniqueDocId: false,
      displayDocIdError: false,
      documentIdRules: computed((): any[] => {
        return getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS)
          ? customRules(
            required('Enter a Document ID'),
            maxLength(8, true),
            minLength(8, true),
            isNumber()
          )
          : customRules(
            required('Enter a Document ID'),
            maxLength(8, true),
            isNumber()
          )
      }),
      validateSubmitter: computed((): boolean => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.SUBMITTER_VALID)
      }),
      validateDocId: computed((): boolean => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID)
      }),
      validateRefNum: computed((): boolean => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.REF_NUM_VALID)
      }),
      uniqueDocIdError: computed((): string[] => {
        // Manual error handling for Unique DocId Lookup
        return localState.displayDocIdError ? ['Must be unique number'] : []
      })
    })

    watch(() => localState.documentId, async (val: string) => {
      if (localState.documentId.length === 8) {
        localState.loadingDocId = true
        const validateDocId: MhrDocIdResponseIF = await validateDocumentID(localState.documentId)
        localState.isUniqueDocId = !validateDocId.exists && validateDocId.valid
        localState.displayDocIdError = !localState.isUniqueDocId
      } else {
        localState.isUniqueDocId = false
        localState.displayDocIdError = false
      }

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
