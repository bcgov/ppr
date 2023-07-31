<template>
  <div id="mhr-submitting-party">
    <section id="mhr-add-submitting-party" class="mt-10">
      <h2>Submitting Party</h2>
      <p class="mt-2">
        Provide the name and contact information for the person or business submitting this registration. You can add
        the submitting party information manually, or, if the submitting party has a Personal Property Registry party
        code, you can look up the party code or name.
      </p>

      <!-- Parties Look Up -->
      <PartySearch isMhrPartySearch />

      <!-- Mhr Submitting Party Form -->
      <MhrSubmittingParty :validate="validateSubmitter" :class="{ 'border-error-left': validateSubmitter }" />
    </section>

    <section id="mhr-submitting-party-doc-id" class="mt-10">
      <h2>Document ID</h2>
      <p class="mt-2">
        Enter the 8-digit Document ID number.
      </p>

      <v-form ref="documentIdForm" v-model="isDocumentIdValid">
        <v-card
          flat
          rounded
          id="submitting-party"
          class="mt-8 pa-8 pr-6 pb-3"
          :class="{ 'border-error-left': validateDocId }"
        >
          <v-row no-gutters class="pt-3">
            <v-col cols="12" sm="2">
              <label class="generic-label" :class="{ 'error-text': validateDocId }">
                Document ID
              </label>
            </v-col>
            <v-col cols="12" sm="10" class="px-1">
              <v-text-field
                filled
                id="doc-id-num"
                class="pr-2"
                maxlength="8"
                label="Document ID Number"
                v-model="documentId"
                :rules="documentIdRules"
                :error-messages="uniqueDocIdError"
              >
                <template v-slot:append>
                  <v-progress-circular
                    v-if="loadingDocId"
                    indeterminate
                    color="primary"
                    class="my-0"
                    :size="25"
                    :width="3"
                  />
                  <v-icon v-if="!loadingDocId && isVerifiedDocId" color="green darken-2">mdi-check</v-icon>
                </template>
              </v-text-field>
            </v-col>
          </v-row>
        </v-card>
      </v-form>
    </section>

    <section id="mhr-submitting-party-reference" class="mt-10">
      <Attention
        sectionId="mhr-attention"
        hasWiderInput
        :intialValue="getMhrAttentionReference"
        :sectionNumber="3"
        :validate="validateRefNum"
        @isAttentionValid="setAttentionValidation"
        @setStoreProperty="setMhrAttentionReference"
      />
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { MhrSubmittingParty } from '@/components/mhrRegistration/SubmittingParty'
import { Attention } from '@/components/common'
import { PartySearch } from '@/components/parties/party'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'
import { useStore } from '@/store/store'
import { useInputRules } from '@/composables'
import { validateDocumentID } from '@/utils'
// eslint-disable-next-line no-unused-vars
import { MhrDocIdResponseIF, FormIF } from '@/interfaces'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'SubmittingParty',
  components: {
    Attention,
    PartySearch,
    MhrSubmittingParty
  },
  setup () {
    const {
      // Actions
      setMhrRegistrationDocumentId,
      setMhrAttentionReference
    } = useStore()
    const {
      // Getters
      getMhrAttentionReference,
      getMhrRegistrationDocumentId,
      getMhrRegistrationValidationModel
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
      isDocumentIdValid: false,
      isRefNumValid: false,
      loadingDocId: false,
      isUniqueDocId: false,
      displayDocIdError: false,
      documentIdRules: computed(() => {
        return getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS)
          ? customRules(
            required('Enter a Document ID'),
            maxLength(8, true),
            minLength(8, true),
            isNumber()
          )
          : customRules(
            maxLength(8, true),
            isNumber()
          )
      }),
      validateSubmitter: computed((): boolean => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.SUBMITTER_VALID)
      }),
      validateDocId: computed(() => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID)
      }),
      validateRefNum: computed(() => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.REF_NUM_VALID)
      }),
      isVerifiedDocId: computed(() => {
        return localState.isDocumentIdValid && localState.isUniqueDocId
      }),
      uniqueDocIdError: computed(() => {
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
        setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID, localState.isVerifiedDocId)
      } else {
        localState.isUniqueDocId = false
        localState.displayDocIdError = false
        setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID, false)
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
#mhr-submitting-party {
  /* Set "header-counter" to 0 */
  counter-reset: header-counter;
}

h2::before {
  /* Increment "header-counter" by 1 */
  counter-increment: header-counter;
  content: counter(header-counter) '. ';
}
</style>
