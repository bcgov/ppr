<template>
  <div id="document-id-container">
    <h2>Document ID</h2>
    <p class="mt-2">Enter the 8-digit Document ID number.</p>
    <v-form ref="documentIdForm" v-model="isDocumentIdFormValid">
      <v-card
        id="document-id-card"
        class="mt-8 pa-8 pr-6 pb-3"
        :class="{ 'border-error-left': validateDocId }"
        flat
      >
        <v-row no-gutters>
          <v-col cols="12" sm="2">
            <label
              class="generic-label"
              :class="{ 'error-text': validateDocId }"
              for="doc-id-field"
            >
            Document ID
          </label>
          </v-col>
          <v-col cols="12" sm="10" class="px-1">
            <v-text-field
              filled
              id="doc-id-field"
              class="pr-2"
              maxlength="8"
              label="Document ID Number"
              v-model="documentIdModel"
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
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { validateDocumentID } from '@/utils'
import { FormIF, MhrDocIdResponseIF } from '@/interfaces'
import { useInputRules } from '@/composables'

export default defineComponent({
  name: 'DocumentId',
  props: {
    documentId: {
      type: String,
      required: true
    },
    setStoreProperty: {
      type: Function,
      required: true
    },
    validate: {
      type: Boolean,
      default: false
    }
  },
  emits: ['isValid'],
  setup (props, { emit }) {
    const { customRules, isNumber, maxLength } = useInputRules()

    const documentIdForm = ref(null) as FormIF

    const localState = reactive({
      isDocumentIdFormValid: false,
      documentIdModel: props.documentId,
      loadingDocId: false,
      isUniqueDocId: false,
      displayDocIdError: false,
      validateDocId: computed(() => props.validate && !localState.isVerifiedDocId),
      isVerifiedDocId: computed(() => {
        return localState.isDocumentIdFormValid && localState.isUniqueDocId
      }),
      uniqueDocIdError: computed(() => {
        // Manual error handling for Unique DocId Lookup
        return localState.displayDocIdError ? ['Must be unique number'] : []
      }),
      documentIdRules: computed(() => {
        return customRules(maxLength(8, true), isNumber())
      })
    })

    watch(() => props.validate, async () => {
      documentIdForm.value?.validate()
    })

    watch(
      () => localState.documentIdModel,
      async (val: string) => {
        if (localState.documentIdModel.length === 8) {
          localState.loadingDocId = true
          const validateDocId: MhrDocIdResponseIF = await validateDocumentID(localState.documentIdModel)
          localState.isUniqueDocId = !validateDocId.exists && validateDocId.valid
          localState.displayDocIdError = !localState.isUniqueDocId
          localState.isUnitNoteValid = localState.isVerifiedDocId

          emit('isValid', localState.isVerifiedDocId)
        } else {
          localState.isUniqueDocId = false
          localState.displayDocIdError = false
          localState.isUnitNoteValid = false

          emit('isValid', false)
        }

        localState.loadingDocId = false
        props.setStoreProperty(val)
      },
      { immediate: true }
    )

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
