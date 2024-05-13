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
          @closePanel="closePanel"
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

/** Local Properties **/
const activePanels = ref([])

/** Local Functions **/
const closePanel = (panelIndex: number) => activePanels.value = activePanels.value.filter(panel => panel !== panelIndex)

watch(() => activePanels.value, () => {
  activePanels.value.length > 1 && activePanels.value.shift()
})

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';

.securities-act-notices-panel-row {
  background: $gray1;
  max-height: 750px;
  overflow-y: auto;
}

.empty-notices-msg {
  background: white;
}

:deep(.theme--light.v-btn.v-btn--disabled) {
  color: $primary-blue !important;
}
</style>
