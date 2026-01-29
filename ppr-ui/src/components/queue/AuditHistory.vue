<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { enumToLabel } from '@/utils/format-helper'
import { ReviewStatusTypes } from '@/composables/analystQueue/enums'
import { pacificDate } from '@/utils'
import type { QueueReviewStepIF } from '@/composables/analystQueue/interfaces'

const props = withDefaults(defineProps<{
  count?: number
  expanded?: boolean
  title?: string
  steps?: QueueReviewStepIF[]
}>(), {
  count: 0,
  expanded: false,
  title: 'Audit History',
  steps: () => []
})

const emit = defineEmits<{
  (e: 'toggle', expanded: boolean): void
}>()

const isExpanded = ref(props.expanded)

watch(() => props.expanded, (val) => {
  isExpanded.value = val
})

const label = computed(() => `View History (${props.count})`)

const sortedSteps = computed(() => {
  return [...props.steps].sort((a, b) => {
    const aTime = a?.createDateTime ? new Date(a.createDateTime).getTime() : 0
    const bTime = b?.createDateTime ? new Date(b.createDateTime).getTime() : 0
    return bTime - aTime
  })
})

const formatDateTimeParts = (dateTime?: string) => {
  if (!dateTime) return { date: '', time: '' }
  const pacific = pacificDate(dateTime, true).replace(' Pacific time', '')
  const parts = pacific.split(' at ')
  return {
    date: parts[0] || '',
    time: parts[1] || ''
  }
}

const getStatusLabel = (statusType: ReviewStatusTypes) => {
  if (statusType === ReviewStatusTypes.DECLINED) return 'Rejected'
  return enumToLabel(statusType)
}

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
  emit('toggle', isExpanded.value)
}
</script>

<template>
  <div id="audit-history">
    <div class="font-bold text-gray-900 bg-bcGovColor-gray2 px-[1.4rem] py-[12px] rounded-t">
      <div class="flex justify-between">
        <div class="flex items-center">
          <UIcon name="i-mdi-history" class="w-6 h-6 text-blue-350" />
          <div class="ml-2">{{ title }}</div>
        </div>
      </div>
    </div>

    <div class="w-full border-t bg-white pa-6">
      <button
        type="button"
        class="text-blue-600 hover:text-blue-700 flex items-center gap-1"
        :aria-expanded=isExpanded
        aria-controls="audit-history-content"
        @click="toggleExpanded"
      >
        <span>{{ label }}</span>
        <UIcon :name="isExpanded ? 'i-mdi-chevron-up' : 'i-mdi-chevron-down'" class="w-5 h-5" />
      </button>

      <div v-if="isExpanded" id="audit-history-content" class="mt-4">
          <div class="space-y-4">
            <div
              v-for="(step, index) in sortedSteps"
              :key="`${step.createDateTime}-${index}`"
              class="border-b border-bcGovGray-200 pb-4"
            >
              <v-row no-gutters>
                <v-col cols="12" sm="2" class="text-normal gray7 whitespace-nowrap">
                  {{ formatDateTimeParts(step.createDateTime).date }}
                </v-col>
                <v-col cols="12" sm="1" class="text-normal gray7 whitespace-nowrap">
                  {{ formatDateTimeParts(step.createDateTime).time }}
                </v-col>
                <v-col cols="12" sm="7" class="space-y-2">
                  <div class="font-bold text-gray-900">
                    Registration {{ getStatusLabel(step.statusType) }}
                    <span v-if="step.username" class="font-normal gray7">
                      (by {{ step.username }})
                    </span>
                  </div>
                  <div v-if="step.statusType === ReviewStatusTypes.DECLINED" class="space-y-2">
                    <div class="gray7">
                      Rejected reason: {{ step.declinedReasonType ? enumToLabel(step.declinedReasonType) : '—' }}
                    </div>
                    <div class="gray7">
                      Staff note: {{ step.staffNote || '—' }}
                    </div>
                  </div>
                </v-col>
              </v-row>
            </div>
          </div>
      </div>
    </div>
  </div>
</template>
