<template>
  <div id="securities-act-notices">
    <v-row
      noGutters
      class="pt-10"
    >
      <v-col
        cols="auto"
        class="sub-header"
      >
        <h3 class="lh-22">
          {{ UIRegistrationTypes.SECURITY_ACT_NOTICE }}
        </h3>
      </v-col>
    </v-row>
    <v-row noGutters>
      <v-col class="pt-2 pb-6 sub-header-info">
        <v-btn
          id=""
          class="mt-3"
          variant="outlined"
          width="175"
          height="45"
          :disabled="openAddNotice || disableAddNotice"
          @click="openAddNotice = true"
        >
          <v-icon class="pr-2">
            mdi-plus
          </v-icon>
          Add Notice
        </v-btn>
      </v-col>
    </v-row>

    <v-expand-transition>
      <v-row
        v-if="openAddNotice"
        noGutters
      >
        <v-col class="pt-2 pb-6">
          <AddEditNotice
            :isAmendment="isAmendment"
            @cancel="openAddNotice = false"
            @done="handleAddNotice"
          />
        </v-col>
      </v-row>
    </v-expand-transition>

    <v-row noGutters>
      <v-col class="pt-2 pb-6">
        <SecuritiesActNoticesPanels
          :isAmendment="isAmendment"
          :isAddingNotice="openAddNotice"
          @hasActivePanel="disableAddNotice = $event"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref  } from 'vue'
import { AddEditNotice } from '@/components/registration'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { AddEditSaNoticeIF } from '@/interfaces'
import SecuritiesActNoticesPanels from '@/components/registration/securities-act-notices/SecuritiesActNoticesPanels.vue'
import { UIRegistrationTypes } from '@/enums'

/** Composables **/
const { setSecuritiesActNotices } = useStore()
const { getSecuritiesActNotices } = storeToRefs(useStore())

/** Props **/
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  isAmendment?: boolean
}>(), {
  isAmendment: false
})

/** Local Properties **/
const openAddNotice = ref(false)
const disableAddNotice = ref(false)


/** Local Functions **/
const handleAddNotice = (notice: AddEditSaNoticeIF) => {
  openAddNotice.value = false
  // Set add edit notices
  setSecuritiesActNotices([...getSecuritiesActNotices.value, notice])
}
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
