<template>
  <v-card
    id="securities-act-notices-panels"
    flat
  >
    <v-row
      noGutters
      justify="center"
      class="securities-act-notices-panel-row"
    >
      <v-expansion-panels
        v-if="getSecuritiesActNotices.length"
        v-model="activePanels"
        multiple
      >
        <NoticePanel
          v-for="(item, index) in displayNotices"
          :key="index"
          :disabled="false"
          :notice="item"
          :noticeIndex="index"
          :isActivePanel="activePanels.includes(index)"
          :disableActions="!!activePanels.length || isAddingNotice"
          :closeOrders="activeOrderPanel !== index"
          :isSummary="isSummary"
          :isAmendment="isAmendment"
          :class="{ 'px-2': isSummary }"
          @togglePanel="togglePanel"
          @activeOrderIndex="activeOrderPanel = $event"
        />
      </v-expansion-panels>
      <v-col
        v-else
        class="empty-notices-msg text-center py-8"
      >
        <p class="gray7 fs-14">
          No Notices added yet
        </p>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed, ref, watch } from 'vue'
import { useStore } from '@/store/store'
import NoticePanel from './NoticePanel.vue'
import { AddEditSaNoticeIF } from '@/interfaces'

/** Composables **/
const { getSecuritiesActNotices } = storeToRefs(useStore())

/** Emits **/
const emits = defineEmits<{
  hasActivePanel: [value: boolean]
}>()

/** Props **/
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  isAddingNotice?: boolean,
  isSummary?: boolean,
  isAmendment?: boolean
}>(), {
  isAddingNotice: false,
  isSummary: false,
  isAmendment: false
})

/** Local Properties **/
const activePanels = ref([])
const activeOrderPanel = ref(null)
const displayNotices = computed((): Array<AddEditSaNoticeIF> => {
  return (props.isSummary && props.isAmendment)
    ? getSecuritiesActNotices.value.filter((notice: AddEditSaNoticeIF) => !!notice.action ||
      notice.securitiesActOrders.some(order => !!order?.action))
    : getSecuritiesActNotices.value
})

/** Local Functions **/
/** Open or close panel by index **/
const togglePanel = (panelIndex: number) => {
  activePanels.value?.includes(panelIndex)
    ? activePanels.value = activePanels.value.filter(panel => panel !== panelIndex) // Close active panel
    : activePanels.value = [ ...activePanels.value, panelIndex] // Open panel
}


/** Inform parent of active panel and ensure only 1 panel is open at a time **/
watch(() => activePanels.value, () => {
  emits('hasActivePanel', activePanels.value.length > 0)
  if (activePanels.value.length > 1) activePanels.value.shift()
  scrollToActivePanel(activePanels.value[0])
})

/** Scroll active panel into view **/
const scrollToActivePanel = (activeIndex: number) => {
  setTimeout(() => {
    activeIndex
      ? document.getElementsByClassName('notice-panel')[activeIndex]?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      })
      : document.getElementById('securities-act-notices')?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      })
  }, 200)
}

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
.securities-act-notices-panel-row {
  background: $gray1;
  overflow-y: auto;
}
.empty-notices-msg {
  background: white;
}
:deep(.theme--light.v-btn.v-btn--disabled) {
  color: $primary-blue !important;
}
:deep(.v-expansion-panel--active:not(:first-child)), :deep(.v-expansion-panel--active+.v-expansion-panel) {
  margin-top: 3px;
}
</style>
