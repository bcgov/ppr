<template>
  <div id="document-id-container">
    <h2 v-if="content.title">
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${content.title}`}}
    </h2>
    <p class="mb-6">{{ content.description }}</p>
    <v-form ref="documentIdForm" v-model="isDocumentIdFormValid">
      <v-card
        id="document-id-card"
        class="pt-10 pl-8 pb-3 pr-6"
        :class="[{ 'border-error-left': showBorderError }, { 'pb-8': content.hintText }]"
        flat
      >
        <v-row no-gutters>
          <v-col cols="12" sm="3">
            <label
              class="generic-label"
              :class="{ 'error-text': showBorderError }"
              for="doc-id-field"
            >
            {{ content.sideLabel }}
          </label>
          </v-col>
          <v-col cols="12" sm="9">
            <v-text-field
              filled
              id="doc-id-field"
              class="pr-2"
              maxlength="8"
              label="Document ID Number"
              v-model="documentIdModel"
              :rules="documentIdRules"
              :error="!isUniqueDocId && validate"
              :error-messages="uniqueDocIdError"
              :hint="content.hintText"
              :persistent-hint="!!content.hintText"
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
import { computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from 'vue'
import { validateDocumentID } from '@/utils'
import { ContentIF, FormIF, MhrDocIdResponseIF } from '@/interfaces'
import { useInputRules } from '@/composables'

export default defineComponent({
  name: 'DocumentId',
  props: {
    documentId: {
      type: String,
      required: true
    },
    sectionNumber: {
      type: Number,
      required: false
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
  emits: ['isValid', 'setStoreProperty'],
  setup (props, { emit }) {
    const { customRules, isNumber, maxLength, minLength, required } = useInputRules()

    const documentIdForm = ref(null) as FormIF

    const localState = reactive({
      isDocumentIdFormValid: false,
      documentIdModel: props.documentId,
      loadingDocId: false,
      isUniqueDocId: false,
      displayDocIdError: false,
      showBorderError: computed(() => props.validate && !localState.isVerifiedDocId),
      isVerifiedDocId: computed(() => {
        return localState.isDocumentIdFormValid && localState.isUniqueDocId
      }),
      uniqueDocIdError: computed(() => {
        // Manual error handling for Unique DocId Lookup
        return localState.displayDocIdError ? ['Must be unique number'] : ''
      }),
      documentIdRules: computed(() => {
        return props.validate
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

          emit('isValid', false)
        }

        localState.loadingDocId = false
        emit('setStoreProperty', val)
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
