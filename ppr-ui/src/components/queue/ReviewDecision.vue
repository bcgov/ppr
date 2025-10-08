<script setup lang="ts">
import { ReviewDecisionTypes, ReviewStatusTypes } from '@/composables';
import { computed } from 'vue';
import { useAnalystQueueStore } from '@/store/analystQueue';
import { storeToRefs } from 'pinia';

const { reviewDecision, validationErrors, isValidate } = storeToRefs(useAnalystQueueStore())
const { validateReviewDecision } = useAnalystQueueStore()

const showHiddenComponent = computed(() => 
  reviewDecision.value.statusType === ReviewStatusTypes.DECLINED 
  || reviewDecision.value.statusType === ReviewStatusTypes.APPROVED
)

const updateReviewDecision = (statusType: ReviewStatusTypes) => {
  reviewDecision.value = { statusType: statusType }
}

watch([isValidate, reviewDecision], () => {
  if (isValidate.value) {
    validateReviewDecision()
  }
}, { deep: true })

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
           
           <div v-if="showHiddenComponent" class="mt-4 rounded animate-slide-down">
             
             <div class="space-y-4">
               <div v-if="reviewDecision.statusType === ReviewStatusTypes.DECLINED">
                 <USelect
                   v-model="reviewDecision.declineReasonType"
                   :items="Object.values(ReviewDecisionTypes)"
                   item-title="text"
                   item-value="value"
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
               </div>
               
               <div>
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
    </div>
</template>

