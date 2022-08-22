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
                label="Document ID Number"
                v-model="documentId"
                :rules="documentIdRules"
              />
            </v-col>
          </v-row>
        </v-card>
      </v-form>
    </section>

    <section id="mhr-submitting-party-reference" class="mt-10">
      <h2>Attention or Reference Number</h2>
      <p class="mt-2">
        Add an optional Attention or Reference Number information for this transaction. If entered, it will appear on
        the Verification of Service document.
      </p>

      <!-- Insert Attention or Reference Number here -->
      <v-form ref="reference-number-form" v-model="isRefNumValid">
        <v-card
          flat
          rounded
          id="attention-or-reference-number-card"
          class="mt-8 pa-8 pr-6 pb-3"
          :class="{ 'border-error-left': validateRefNum }"
        >
          <v-row no-gutters class="pt-3">
            <v-col cols="12" sm="2">
              <label class="generic-label" :class="{ 'error-text': validateRefNum }">
                Attention or Reference Number
              </label>
            </v-col>
            <v-col cols="12" sm="10" class="px-1">
              <v-text-field
                filled
                id="attention-or-reference-number"
                class="pr-2"
                label="Attention or Reference Number (Optional)"
                v-model="attentionReferenceNum"
                :rules="maxLength(40)"
              />
            </v-col>
          </v-row>
        </v-card>
      </v-form>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { MhrSubmittingParty } from '@/components/mhrRegistration/SubmittingParty'
import { PartySearch } from '@/components/parties/party'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { useInputRules } from '@/composables'

export default defineComponent({
  name: 'SubmittingParty',
  components: {
    PartySearch,
    MhrSubmittingParty
  },
  props: {},
  setup (props, context) {
    const {
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getMhrRegistrationValidationModel'
    ])

    const {
      setMhrRegistrationDocumentId,
      setMhrAttentionReferenceNum
    } = useActions<any>([
      'setMhrRegistrationDocumentId',
      'setMhrAttentionReferenceNum'
    ])

    const { customRules, required, maxLength, isNumber } = useInputRules()

    const {
      MhrCompVal,
      MhrSectVal,
      hasError,
      setValidation,
      getSectionValidation,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      attentionReferenceNum: '',
      documentId: '',
      isDocumentIdValid: false,
      isRefNumValid: false,
      documentIdRules: computed(() => customRules(required('Enter a Document ID'), maxLength(8, true), isNumber())),
      validateSubmitter: computed(() => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.SUBMITTER_VALID)
      }),
      validateDocId: computed(() => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID)
      }),
      validateRefNum: computed(() => {
        return getSectionValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.REF_NUM_VALID)
      })
    })

    watch(
      () => localState.documentId,
      (val: string) => {
        if (localState.documentId.length === 8) {
          console.log('Looking up Document ID...')
          // TODO: Implement Document ID look up
        }
        setMhrRegistrationDocumentId(val)
      }
    )

    watch(() => localState.isDocumentIdValid, (val: boolean) => {
      setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.DOC_ID_VALID, val)
    })

    watch(() => localState.validateDocId, async () => {
      // @ts-ignore - function exists
      await context.refs.documentIdForm.validate()
    })

    watch(() => localState.attentionReferenceNum, (val: string) => {
      setMhrAttentionReferenceNum(val)
    })

    watch(() => localState.isRefNumValid, (val: boolean) => {
      setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.REF_NUM_VALID, val)
    })

    const scrollOnValidationUpdates = () => {
      scrollToInvalid(MhrSectVal.SUBMITTING_PARTY_VALID, 'mhr-submitting-party')
    }

    watch(() => localState.validateSubmitter, () => {
      setTimeout(scrollOnValidationUpdates, 300)
    }, { deep: true })

    return {
      MhrCompVal,
      MhrSectVal,
      maxLength,
      hasError,
      getSectionValidation,
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
