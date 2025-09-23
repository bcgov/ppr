import type { ReviewIF } from "@/composables/analystQueue/interfaces"


export const useAnalystQueueStore = defineStore('mhr/queue', () => {
  const queueTableData = ref<Array<ReviewIF>>([])
  const isQueueTableDataLoading = ref<boolean>(false)
  const assignees = ref<Array<any>>([])
  const columnsToShow = ref([])


 const  getQueueTabledata = async () => {
  isQueueTableDataLoading.value = true
  queueTableData.value = await getReviews()
  isQueueTableDataLoading.value = false
 }

  return {
    queueTableData,
    getQueueTabledata
  }
})
