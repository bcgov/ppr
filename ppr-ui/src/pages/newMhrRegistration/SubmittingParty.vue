<template>
  <div id="mhr-submitting-party">
    <section>
      <DocumentId
        id="mhr-submitting-party-doc-id"
        class="mt-10"
        :document-id="documentId || ''"
        :content="{
          title: '1. Document ID',
          description: 'Enter the 8-digit Document ID number.',
          sideLabel: 'Document ID',
          hintText: 'Enter the 8-digit Document ID number'
        }"
        :validate="validateDocId"
        @set-store-property="documentId = $event"
        @is-valid="setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID, $event)"
      />
    </section>

    <section
      id="mhr-add-submitting-party"
      class="mt-10"
    >
      <ContactInformation
        :contact-info="getMhrRegistrationSubmittingParty"
        :content="isRoleStaffReg ? submittingPartyContentStaff : submittingPartyRegistrationContent"
        :validate="validateSubmitter"
        :section-number="2"
        @set-store-property="setMhrRegistrationSubmittingParty"
        @is-valid="setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.SUBMITTER_VALID, $event)"
      />
    </section>

    <section
      id="mhr-submitting-party-reference"
      class="mt-10"
    >
      <Attention
        section-id="mhr-attention"
        has-wider-input
        :initial-value="getMhrAttentionReference"
        :section-number="3"
        :validate="validateRefNum"
        @is-attention-valid="setAttentionValidation"
        @set-store-property="setMhrAttentionReference"
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
import type { FormIF } from '@/interfaces'
import { storeToRefs } from 'pinia'
import { submittingPartyRegistrationContent, submittingPartyContentStaff } from '@/resources'

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
      isRoleStaffReg,
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
      isRoleStaffReg,
      documentIdForm,
      MhrCompVal,
      MhrSectVal,
      getMhrRegistrationSubmittingParty,
      setMhrRegistrationSubmittingParty,
      setValidation,
      submittingPartyContentStaff,
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
@use '@/assets/styles/theme' as *;
</style>
