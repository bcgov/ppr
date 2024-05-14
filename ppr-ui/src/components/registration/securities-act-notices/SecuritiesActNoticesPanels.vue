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
          v-for="(item, index) in getSecuritiesActNotices"
          :key="index"
          :disabled="false"
          :notice="item"
          :noticeIndex="index"
          :isActivePanel="activePanels.includes(index) || isAddingNotice"
          @togglePanel="togglePanel"
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
import { ref, watch } from 'vue'
import { useStore } from '@/store/store'
import NoticePanel from './NoticePanel.vue'

/** Composables **/
const { getSecuritiesActNotices } = storeToRefs(useStore())

/** Emits **/
const emits = defineEmits<{
  hasActivePanel: [value: boolean]
}>()

/** Props **/
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  isAddingNotice: boolean
}>(), {
  isAddingNotice: false
})

/** Local Properties **/
const activePanels = ref([])

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
})

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
</style>
