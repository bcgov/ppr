<script setup lang="ts">
import { ReviewStatusTypes } from '@/composables';
import { useAnalystQueueStore } from '@/store/analystQueue';
import { updateQueuedTransfer } from '@/utils/mhr-api-helper'
import type { QueueReviewUpdatePayloadIF } from '@/composables/analystQueue/interfaces'

const { queueTransfer, reviewId, isAssignable, isInReview, reviewDecision, validationErrors } = storeToRefs(useAnalystQueueStore())
const { validateReviewDecision } = useAnalystQueueStore()

const isAssigned = computed(() => {
  return !!queueTransfer.value?.assigneeName
})
const assigneeName = computed(() => {
  return isAssigned.value ? queueTransfer.value?.assigneeName : 'None' 
})

const updateAssignee = async () => {
  if (isAssigned.value) {
    queueTransfer.value = await updateQueuedTransfer(
      reviewId.value, 
      { statusType: ReviewStatusTypes.NEW }
    )
  } else {
    queueTransfer.value = await updateQueuedTransfer(
      reviewId.value, 
      { statusType: ReviewStatusTypes.IN_REVIEW }
    )
  }
}

const submitReview = async () => {
  if (!validateReviewDecision()) {
    return
  }

  const statusType = reviewDecision.value?.statusType
  const payload: QueueReviewUpdatePayloadIF = { statusType }

  // Per workflow: only include staff note + decline reason when Declined.
  if (statusType === ReviewStatusTypes.DECLINED) {
    payload.staffNote = reviewDecision.value?.staffNote
    payload.declinedReasonType = reviewDecision.value?.declinedReasonType
  }

  try {
    const updated = await updateQueuedTransfer(
      reviewId.value,
      payload
    )

    if (!updated) {
      validationErrors.value.general = 'Unable to submit review decision.'
      return
    }

    // Keep local state in sync so UI updates immediately.
    queueTransfer.value = updated

    // Navigate to dashboard after successful submission.
    emit('go-to-dash')
  } catch (e: any) {
    validationErrors.value.general = e?.message || 'Unable to submit review decision.'
  }
}

const emit = defineEmits(['go-to-dash']) 
</script>

<template>
  <div class="absolute bottom-0 left-0 right-0 w-full bg-white border-t border-gray-200 shadow-lg">
    <div class="container mx-auto pt-8 pb-15">
      <div class="grid grid-cols-1 lg:grid-cols-12">
        <div class="lg:col-span-9 pr-2">
            <div class="flex space-x-3 justify-start items-center text-gray-700">
              <UIcon name="i-mdi-account-circle-outline" class="w-6 h-6" />
               <div>
                <strong>Assignee:</strong> {{ assigneeName }}
               </div>
              <UButton
                v-if="isAssignable"
                variant="outline"
                color="primary"
                size="md"
                class="rounded-sm"
                @click="updateAssignee"
              >
                {{ isAssigned ? 'Unassign' : 'Assign to Me'}}
              </UButton>
            </div>
        </div>
        <div class="lg:col-span-3 flex justify-end space-x-3">
          <UButton
            v-if="isInReview"
            color="primary"
            size="md"
            class="rounded-sm"
            @click="submitReview"
          >
            Submit
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

