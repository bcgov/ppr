<script setup lang="ts">
import { ConfirmationDialog } from '@/components/dialogs'
import { confirmCancelDialog } from '@/resources/dialogOptions/confirmationDialogs'
import type { DocumentSummary } from '@/interfaces'

/** Props for the uploaded documents list **/
const props = defineProps({
  documentList: {
    type: Array<DocumentSummary>,
    default: () => [],
    required: false,
  }
})

/** Controls visibility of the add documents section **/
const showAddDocuments = ref(false)
/** Controls visibility of the confirmation cancel dialog **/
const showConfirmCancelDialog = ref(false)

 /** Handles confirmation dialog actions **/
const dialogHandler = (action: string) => {
  if (action) {
    showAddDocuments.value = false
  }
  showConfirmCancelDialog.value = false
}

/** Toggles file upload section and handles cancel confirmation **/
const fileUploadToggle = (action: string) => {
  if (showAddDocuments.value) {
    showConfirmCancelDialog.value = true
    return
  }
  if (action) {
    showAddDocuments.value = !showAddDocuments.value
  }
}

/** Opens a PDF document in a new browser tab **/
const downloadPdf = (url: string) => {
  if (!url) return
  window.open(url, '_blank')
}
</script>
<template>
  <div>
    <ConfirmationDialog
      :set-display="showConfirmCancelDialog"
      :set-options="confirmCancelDialog"
      :set-hide-checkbox="true"
      @proceed="dialogHandler"
    />
    <div
      :class="'font-bold text-gray-900 bg-bcGovColor-gray2 px-[1.4rem] py-[12px] rounded-t'"
    >
      <div class="flex justify-between">
        <div class="flex">
          <UIcon name="i-mdi-text-box" class="w-6 h-6" />
          <div class="ml-2">Supporting Documents</div>
        </div>
        <div>
          <UButton
            class="hover:bg-transparent"
            variant="ghost"
            :icon="showAddDocuments ? 'i-mdi-close' : 'i-mdi-plus'"
            :label="showAddDocuments ? 'Cancel Adding Documents' : 'Add Documents'"
            data-cy="add-documents-button"
            @click="fileUploadToggle"
          />
        </div>
      </div>
    </div>

    <!-- Supporting Documents Component -->
    <div
      v-if="showAddDocuments"
      :class="'bg-white rounded pa-6'"
    >
      <FileUpload />
    </div>

    <!-- List of Uploaded Documents -->
    <div
      v-for="document in props.documentList"
      :key="document.consumerFilename"
      class="w-full border-t bg-white pa-6"
    >
      <div
        class="flex items-center cursor-pointer"
        @click="downloadPdf(document.documentURL)"
      >
        <UIcon name="i-mdi-file-pdf-outline" class="text-primary size-[20px]" />
        <span class="ml-2 text-[16px] italic text-primary">{{document.consumerFilename}}</span>
      </div>
      <span class="ml-7 text-gray-700 fs-14">{{document?.fileSize || '' }}</span>
    </div>
  </div>
</template>
