import type { 
  DateRangeFilterIF,
  QueueDetailIF,
  QueueSummaryIF,
  QueueReviewUpdatePayloadIF,
  QueueReviewStepIF
} from "@/composables/analystQueue/interfaces"
import { queueTableColumns, ReviewStatusTypes } from "@/composables"
import { getQueuedTransfer, getReviews } from "@/utils/mhr-api-helper"
import { computed, ref } from 'vue'


export const useAnalystQueueStore = defineStore('mhr/queue', () => {
  // queueTable
  const queueTableData = ref<Array<QueueSummaryIF>>([])
  const isQueueTableDataLoading = ref<boolean>(false)
  const columnsToShow = ref(queueTableColumns)
  const columnFilters = ref({})
  // Review
  const queueTransfer = ref<QueueDetailIF>(null)
  const reviewId = ref<string>(null)

  const queueTransferStatus = computed(() => {
    return queueTransfer.value?.status ?? (queueTransfer.value as any)?.statusType
  })
  
  // Review Decision State
  const reviewDecision = ref<QueueReviewUpdatePayloadIF>({})

  const shouldShowReviewDecision = computed(() => {
    return [ReviewStatusTypes.IN_REVIEW, ReviewStatusTypes.APPROVED, ReviewStatusTypes.DECLINED].includes(queueTransferStatus.value)
  })
  
  // Error state for validation messages
  const validationErrors = ref({
    declineReasonType: '',
    general: ''
  })
  
 const getQueueTabledata = async () => {
  isQueueTableDataLoading.value = true
  queueTableData.value = await getReviews()
  isQueueTableDataLoading.value = false
 }

 /**
  * Hydrates the local `reviewDecision` draft from the current `queueTransfer` record.
  *
  * - Uses the latest item in `queueTransfer.reviewSteps` when present, otherwise falls back
  *   to the top-level `queueTransferStatus`.
  * - Copies the notes fields so the decision component can show/edit them.
  * - Only sets `declinedReasonType` when the latest decision is `DECLINED` to avoid carrying
  *   stale decline reasons when a review is `NEW`, `IN_REVIEW`, or `APPROVED`.
  */
 const hydrateReviewDecisionFromQueueTransfer = () => {
  const steps = (queueTransfer.value?.reviewSteps || []) as QueueReviewStepIF[]
  const latestStep = steps.length ? steps[steps.length - 1] : undefined
  const statusType = latestStep?.statusType || queueTransferStatus.value

  const nextDecision: QueueReviewUpdatePayloadIF = {
    statusType,
    staffNote: latestStep?.staffNote || '',
    clientNote: latestStep?.clientNote || '',
    changeNote: latestStep?.changeNote || '',
  }

  if (statusType === ReviewStatusTypes.DECLINED && latestStep?.declinedReasonType) {
    nextDecision.declinedReasonType = latestStep.declinedReasonType
  }

  reviewDecision.value = nextDecision
 }

 const loadQueueTransfer = async (id: string) => {
  reviewId.value = id
  queueTransfer.value = await getQueuedTransfer(id)
  hydrateReviewDecisionFromQueueTransfer()
  return queueTransfer.value
 }

 const filteredQueueReviews = computed(() => {
  return queueTableData.value.length ? queueTableData.value.filter(row =>
    Object.entries(columnFilters.value).every(([key, value]) => {
      if (value === null || value === undefined || value === '') return true // skip empty filters

      const cell = row[key]

      if (value && typeof value === 'object' && 'start' in value && 'end' in value) {
        const dateRangeValue = value as DateRangeFilterIF
        // Convert the date range to comparable format
        const filterStartDate = new Date(
          dateRangeValue.start.year,
          dateRangeValue.start.month - 1,
          dateRangeValue.start.day
        )
        const filterEndDate = new Date(
          dateRangeValue.end.year,
          dateRangeValue.end.month - 1,
          dateRangeValue.end.day
        )
        
        let cellDate: Date
        if (typeof cell === 'string') {
          cellDate = new Date(cell)
        } else if (cell instanceof Date) {
          cellDate = cell
        } else {
          return false
        }

        return cellDate >= filterStartDate && cellDate <= filterEndDate
      }

      // If both are strings → partial match
      if (typeof cell === 'string' && typeof value === 'string') {
        return cell.toLowerCase().includes(value.toLowerCase())
      }

      // Otherwise → strict equality
      return cell === value
    })
  ) : []
})

const showClearFilterButton = computed(() => {
  return Object.values(columnFilters.value).some(value => {
    if (value === null || value === undefined || value === '') return false
    
    // Check if it's a date range filter
    if (value && typeof value === 'object' && 'start' in value && 'end' in value) {
      const dateRangeValue = value as DateRangeFilterIF
      return dateRangeValue.start && dateRangeValue.end
    }
    
    return true
  })
})

// Allow assigning/unassigning while NEW or IN_REVIEW.
const isAssignable = computed(() => {
  return [ReviewStatusTypes.NEW, ReviewStatusTypes.IN_REVIEW].includes(queueTransferStatus.value)
})

// Allow review decision + submit only while IN_REVIEW.
const isInReview = computed(() => {
  return queueTransferStatus.value === ReviewStatusTypes.IN_REVIEW
})


const assignees = computed(() => {
  const uniqueAssignees = new Set()

  return queueTableData.value
    .filter(review => review.assigneeName && review.assigneeName.trim() !== '')
    .map(review => ({
      label: review.assigneeName,
      value: review.assigneeName
    }))
    .filter(assignee => {
      if (uniqueAssignees.has(assignee.value)) {
        return false
      }
      uniqueAssignees.add(assignee.value)
      return true
    })
})

 const toggleColumnsVisibility = (selected: Array<any>) => {
  columnsToShow.value = queueTableColumns.filter(column => {
    return column.isFixed || selected.includes(column.id)
  })
 }

  // Real-time validation function
  const validateReviewDecision = () => {
    // Clear previous errors
    validationErrors.value.declineReasonType = ''
    validationErrors.value.general = ''
    
    // Check if no decision is made
    if (!reviewDecision.value.statusType) {
      validationErrors.value.general = 'Please select a decision (Approve or Decline)'
      return false
    }

    if (reviewDecision.value.statusType === ReviewStatusTypes.APPROVED) {
      return true
    }
    
    // If declined, must have a reason
    if (reviewDecision.value.statusType === ReviewStatusTypes.DECLINED) {
      if (reviewDecision.value.declinedReasonType) {
        return true
      } else {
        validationErrors.value.declineReasonType = 'Please select a reason for declining'
        return false
      }
    }
    
    return false
  }


 return {
    assignees,
    queueTableData,
    columnsToShow,
    filteredQueueReviews,
    columnFilters,
    showClearFilterButton,
    isAssignable,
    isInReview,
    shouldShowReviewDecision,
    queueTransfer,
    reviewId,
    reviewDecision,
    validationErrors,
    getQueueTabledata,
    loadQueueTransfer,
    toggleColumnsVisibility,
    validateReviewDecision
  }
})
