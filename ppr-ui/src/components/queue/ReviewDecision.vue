<script setup lang="ts">
import { computed, watch } from 'vue';
import { enumToLabel } from '@/utils/format-helper'
import { ReviewDecisionTypes, ReviewStatusTypes } from '@/composables';
import { storeToRefs } from 'pinia';
import { useAnalystQueueStore } from '@/store/analystQueue';

const { reviewDecision, validationErrors, isInReview } = storeToRefs(useAnalystQueueStore())

const isDeclined = computed(() => reviewDecision.value.statusType === ReviewStatusTypes.DECLINED)

// Options for the decline reason select dropdown
const declineReasonItems = computed(() => {

  return Object.values(ReviewDecisionTypes).map((value) => ({
    text: enumToLabel(value),
    value
  }))
})

// Update the review decision status type when a button is clicked
const updateReviewDecision = (statusType: ReviewStatusTypes) => {
  if (!isInReview.value) return
  reviewDecision.value = { ...reviewDecision.value, statusType }
}

// Clear the decline-reason error as soon as a reason is selected.
watch(() => reviewDecision.value?.declinedReasonType, (val) => {
  if (val) validationErrors.value.declineReasonType = ''
})

// Clear the general error once a decision is picked.
watch(() => reviewDecision.value?.statusType, (val) => {
  if (val) validationErrors.value.general = ''

  // If decision is not Declined, ensure decline reason is cleared.
  if (val && val !== ReviewStatusTypes.DECLINED && reviewDecision.value?.declinedReasonType) {
    const { declinedReasonType, ...rest } = reviewDecision.value as any
    reviewDecision.value = rest
  }
})

</script>

<template>
    <div
  :class="validationErrors.general || validationErrors.declineReasonType ? 'border-error-left' : ''">
      <div :class="'font-bold text-gray-900 bg-bcGovColor-gray2 px-[1.4rem] py-[12px] rounded-t'">
        <div class="flex justify-between">
            <div class="flex">
                <UIcon name="i-mdi-stamper" class="w-6 h-6 text-blue-350" />
                <div class="ml-2">Review Decision</div>
            </div>
        </div>
      </div>
      <div class="w-full border-t bg-white pa-6">
        <div class="grid grid-cols-12 gap-4">
          <div class="col-span-3 flex">
            <span class="text-gray-700 font-bold">Review Decision</span>
          </div>
          
          <div class="col-span-9">
            <div class="flex gap-[10px]">
              <UButton
                size="md"
                color="error"
                :class="[
                  'rounded-sm flex-1 h-[44px] justify-center',
                  reviewDecision.statusType === ReviewStatusTypes.DECLINED ? 'bg-error/10' : ''
                ]"
                variant="outline"
                icon="i-mdi-close"
                @click="updateReviewDecision(ReviewStatusTypes.DECLINED)"
              >
                Decline
              </UButton>
              <UButton
                color="success"
                size="md"
                :class="[
                  'rounded-sm flex-1 h-[44px] justify-center text-bcGovGray-900',
                  reviewDecision.statusType === ReviewStatusTypes.APPROVED ? 'bg-success/10' : ''
                ]"
                variant="outline"
                icon="i-mdi-check"
                @click="updateReviewDecision(ReviewStatusTypes.APPROVED)"
              >
                Approve
              </UButton>
            </div>
              
            <div v-if="validationErrors.general" class="text-red-600 text-sm mt-2">
              {{ validationErrors.general }}
            </div>
            
            <div v-if="isDeclined" class="mt-4 rounded animate-slide-down">
              <div class="space-y-4">
                <USelect
                  v-model="reviewDecision.declinedReasonType"
                  :items="declineReasonItems"
                  label-key="text"
                  value-key="value"
                  placeholder="Reason for decline (will be included in client email)"
                  size="lg"
                  :ui="{ 
                      base: [
                          'border-b-[1px] w-full h-[60px] focus:shadow-none data-[state=open]:shadow-none',
                          'data-[state=open]:border-blue-350',
                          validationErrors.declineReasonType ? 'border-error' : ''
                      ],
                      item: 'hover:text-blue-500 hover:bg-bcGovGray-100', 
                      placeholder: validationErrors.declineReasonType ? 'text-error' : 'text-bcGovGray-700'
                  }"
                />
                <div v-if="validationErrors.declineReasonType" class="text-red-600 text-sm mt-1">
                  {{ validationErrors.declineReasonType }}
                </div>

                <UTextarea
                  v-model="reviewDecision.staffNote"
                  placeholder="Staff note (internal)"
                  size="lg"
                  :rows="4"
                  :maxlength="2000"
                  class="w-full"
                  :ui="{ 
                      slots:{
                          base: [
                            'border-bcGovGray-700 focus:shadow-none',
                            'focus:border-blue-350 placeholder:text-bcGovGray-700'
                          ],
                      },
                      base: 'border-b-1 placeholder:text-bcGovGray-700'
                  }"
                />
                <div class="text-xs text-gray-500 mt-1 text-end">
                  {{ reviewDecision.staffNote?.length }} / 2000
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

