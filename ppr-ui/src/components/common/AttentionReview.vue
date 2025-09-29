<script setup lang="ts">
/** Props for the uploaded documents list **/
const props = defineProps({
  attentionReview: {
    type: () => {},
    default: () => {},
    required: false
  }
})
</script>
<template>
  <div>
    <div :class="'font-bold text-gray-900 bg-bcGovColor-gray2 px-[1.4rem] py-[12px] rounded-t'">
      <div class="flex justify-between">
        <div class="flex">
          <UIcon name="i-mdi-information-outline" class="w-6 h-6 text-blue-350" />
          <div class="ml-2">Attention</div>
        </div>
      </div>
    </div>

    <!-- List of Uploaded Documents -->
    <div class="w-full border-t bg-white p-6">
      <div class="flex items-center">
        <span class="w-3/12 text-[16px] font-bold ml-1">Name</span>
        <span class="w-9/12 ml-2 text-[16px]">{{ attentionReview?.name || 'Not entered' }}</span>
      </div>
      <div class="flex items-center">
        <span class="w-3/12 text-[16px] font-bold ml-1">Folio Number</span>
        <span class="w-9/12 ml-2 text-[16px]">{{ attentionReview?.folio || 'Not entered' }}</span>
      </div>
    </div>
  </div>
</template>
