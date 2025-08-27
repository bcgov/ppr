<template>
  <div id="securities-act-notices">
    <v-row
      no-gutters
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
    <v-row no-gutters>
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
        no-gutters
      >
        <v-col class="pt-2 pb-6">
          <AddEditNotice
            :is-amendment="isAmendment"
            @cancel="openAddNotice = false"
            @done="handleAddNotice"
          />
        </v-col>
      </v-row>
    </v-expand-transition>

    <v-row no-gutters>
      <v-col class="pt-2 pb-6">
        <SecuritiesActNoticesPanels
          :is-amendment="isAmendment"
          :is-adding-notice="openAddNotice"
          @has-active-panel="disableAddNotice = $event"
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
import type { AddEditSaNoticeIF } from '@/interfaces'
import SecuritiesActNoticesPanels from '@/components/registration/securities-act-notices/SecuritiesActNoticesPanels.vue'
import { UIRegistrationTypes } from '@/enums'

/** Composables **/
const { setSecuritiesActNotices } = useStore()
const { getSecuritiesActNotices } = storeToRefs(useStore())

/** Props **/

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
@use '@/assets/styles/theme' as *;
</style>
