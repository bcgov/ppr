<script setup lang="ts">
defineProps({
  documentId: {
    type: String,
    required: true,
  }
})

// Future State: Pull in uploaded documents from API or passed via props depending on context
// https://test.api.connect.gov.bc.ca/doc-dev/api/v1/searches/MHR?consumerDocumentId=xxxxxx
// https://test.api.connect.gov.bc.ca/doc-dev/api/v1/searches/MHR?documentServiceId=xxxxx

const showAddDocuments = ref(false)
</script>
<template>
  <div>
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
            @click="showAddDocuments = !showAddDocuments"
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

    <!-- List of Uploaded Documents: Static placeholders - to be dynamic loop of all pulled or provided docs -->
    <div class="w-full border-t bg-white pa-6">
      <div class="flex items-center">
        <UIcon name="i-mdi-file-pdf-outline" class="text-primary size-[20px]" />
        <span class="ml-2 text-[16px] italic text-primary">FileName_One.pdf</span>
      </div>
      <span class="ml-7 text-gray-700 fs-14">123 mb</span>
    </div>

    <div class="w-full border-t bg-white pa-6">
      <div class="flex items-center">
        <UIcon name="i-mdi-file-pdf-outline" class="text-primary size-[20px]" />
        <span class="ml-2 text-[16px] italic text-primary">FileName_Two.pdf</span>
      </div>
      <span class="ml-7 text-gray-700 fs-14">123 mb</span>
    </div>
  </div>
</template>
