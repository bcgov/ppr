<template>
  <div id="document-id-container">
    <h2 v-if="content.title">
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${content.title}` }}
    </h2>
    <p
      v-if="content.description"
      class="mb-6"
    >
      {{ content.description }}
    </p>
    <v-form
      ref="documentIdForm"
      v-model="isDocumentIdFormValid"
    >
      <v-card
        id="document-id-card"
        class="pt-10 pl-8 pb-3 pr-8"
        :class="[{ 'border-error-left': showBorderError }, { 'pb-8': content.hintText }]"
        flat
      >
        <v-row noGutters>
          <v-col
            cols="12"
            sm="3"
          >
            <label
              class="generic-label"
              :class="{ 'error-text': showBorderError }"
              for="doc-id-field"
            >
              {{ content.sideLabel }}
            </label>
          </v-col>
          <v-col
            cols="12"
            sm="9"
          >
            <v-text-field
              id="doc-id-field"
              v-model="documentIdModel"
              variant="filled"
              color="primary"
              maxlength="8"
              label="Document ID Number"
              :disabled="generateDocumentId"
              :rules="documentIdRules"
              :error="!isUniqueDocId && validate && !generateDocumentId"
              :errorMessages="uniqueDocIdError"
              :hint="content.hintText"
              :persistentHint="Boolean(content.hintText)"
            >
              <template #append-inner>
                <v-progress-circular
                  v-if="loadingDocId"
                  indeterminate
                  color="primary"
                  class="my-0"
                  :size="25"
                  :width="3"
                />
                <v-icon
                  v-if="!loadingDocId && isVerifiedDocId && !generateDocumentId"
                  color="green-darken-2"
                >
                  mdi-check
                </v-icon>
              </template>
            </v-text-field>

            <v-checkbox
              v-if="hasDrsEnabled"
              v-model="generateDocumentId"
              color="primary"
              class="mt-2 ml-n2 pb-0 mb-n6"
            >
              <template #label>
                <p>Generate a Document ID Number upon filing.</p>
                <v-tooltip
                  location="top"
                  contentClass="top-tooltip"
                  transition="fade-transition"
                >
                  <template #activator="{ props }">
                    <v-icon
                      class="ml-1"
                      color="primary"
                      size="20"
                      v-bind="props"
                    >
                      mdi-information-outline
                    </v-icon>
                  </template>
                  <div>
                    Upon registration, a Document ID will be generated, and a corresponding document record will be
                    created
                  </div>
                </v-tooltip>
              </template>
            </v-checkbox>
          </v-col>
        </v-row>
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from 'vue'
import { validateDocumentID } from '@/utils'
import { ContentIF, FormIF, MhrDocIdResponseIF } from '@/interfaces'
import { useInputRules } from '@/composables'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'

export default defineComponent({
  name: 'DocumentId',
  props: {
    documentId: {
      type: String,
      required: true
    },
    sectionNumber: {
      type: Number,
      required: false,
      default: null
    },
    content: {
      type: Object as () => ContentIF,
      default: () => {}
    },
    validate: {
      type: Boolean,
      default: false
    }
  },
  emits: ['isValid', 'setStoreProperty', 'setGenerateDocId'],
  setup (props, { emit }) {
    const { setMhrGenerateDocId } = useStore()
    const { hasDrsEnabled, getMhrGenerateDocId } = storeToRefs(useStore())
    const { customRules, isNumber, maxLength, minLength, required } = useInputRules()

    const documentIdForm = ref(null) as FormIF

    const localState = reactive({
      isDocumentIdFormValid: false,
      documentIdModel: props.documentId,
      loadingDocId: false,
      isUniqueDocId: false,
      displayDocIdError: false,
      generateDocumentId: getMhrGenerateDocId.value,
      showBorderError: computed(() => props.validate && !localState.isVerifiedDocId),
      isVerifiedDocId: computed(() => {
        return (localState.isDocumentIdFormValid && localState.isUniqueDocId) || localState.generateDocumentId
      }),
      uniqueDocIdError: computed(() => {
        // Manual error handling for Unique DocId Lookup
        return localState.displayDocIdError ? ['Must be unique number'] : ''
      }),
      documentIdRules: computed(() => {
        return props.validate
          ? customRules(
            required('Enter a Document ID'),
            isNumber(),
            maxLength(8, true),
            minLength(8, true),
          )
          : customRules(
            required('Enter a Document ID'),
            isNumber(),
            maxLength(8, true),
          )
      })
    })

    watch(() => props.validate, async (val) => {
      if (val) documentIdForm.value?.validate()
    }, { immediate: true })

    watch(
      () => localState.documentIdModel,
      async (val: string) => {
        if (localState.documentIdModel?.length === 8) {
          localState.loadingDocId = true
          const validateDocId: MhrDocIdResponseIF = await validateDocumentID(localState.documentIdModel)
          localState.isUniqueDocId = !validateDocId.exists && validateDocId.valid
          localState.displayDocIdError = !localState.isUniqueDocId
          await nextTick()
          emit('isValid', localState.isVerifiedDocId)
        } else {
          localState.isUniqueDocId = false
          localState.displayDocIdError = false

          emit('isValid', localState.generateDocumentId)
        }

        localState.loadingDocId = false
        emit('setStoreProperty', val)
      },
      { immediate: true }
    )

    watch(() => props.documentId, (val: string) => {
      localState.documentIdModel = val
    })

    watch(() => localState.generateDocumentId, (val: boolean) => {
      localState.documentIdModel = ''
      localState.loadingDocId = false
      setMhrGenerateDocId(val)
      emit('isValid', val)
      if(!val) emit('setStoreProperty', '')
    })

    return {
      hasDrsEnabled,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
:deep(.v-field--disabled .v-label.v-field-label, .v-field--focused .v-label.v-field-label) {
  opacity: .4;
}
</style>
