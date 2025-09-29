import type { ReviewIF, DateRangeFilter } from "@/composables/analystQueue/interfaces"
import { queueTableColumns } from "@/composables/analystQueue/resources"
import { getReviews } from "@/utils/mhr-api-helper"


export const useAnalystQueueStore = defineStore('mhr/queue', () => {
  const queueTableData = ref<Array<ReviewIF>>([])
  const isQueueTableDataLoading = ref<boolean>(false)
  const columnsToShow = ref(queueTableColumns)
  const columnFilters = ref({})

 const getQueueTabledata = async () => {
  isQueueTableDataLoading.value = true
  queueTableData.value = await getReviews()
  isQueueTableDataLoading.value = false
 }

 const filteredQueueReviews = computed(() => {
  return queueTableData.value.length ? queueTableData.value.filter(row =>
    Object.entries(columnFilters.value).every(([key, value]) => {
      if (value === null || value === undefined || value === '') return true // skip empty filters

      const cell = row[key]

      if (value && typeof value === 'object' && 'start' in value && 'end' in value) {
        const dateRangeValue = value as DateRangeFilter
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
  return queueTableData.value.length > filteredQueueReviews.value.length
})

const assignees = computed(() => {
  return filteredQueueReviews.value.filter(review => review.assigneeName)
    .map(review => ({
      label: review.assigneeName,
      value: review.assigneeName
    }))
})

 const toggleColumnsVisibility = (selected: Array<any>) => {
  columnsToShow.value = queueTableColumns.filter(column => {
    return column.isFixed || selected.includes(column.id)
  })
 }

 return {
    assignees,
    queueTableData,
    columnsToShow,
    filteredQueueReviews,
    columnFilters,
    showClearFilterButton,
    getQueueTabledata,
    toggleColumnsVisibility
  }
})
