<template>
  <v-container
    v-if="dataLoaded"
    id="mhr-history"
    class="px-0 footer-view-container"
    fluid
  >
    <!-- Loading Overlay -->
    <v-overlay
      v-model="loading"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="30"
        indeterminate
      />
    </v-overlay>

    <!-- View Content -->
    <div class="container pa-0 pt-4">
      <v-row
        id="registration-header"
        noGutters
        class="pt-3 pb-3 soft-corners-top"
      >
        <v-col>
          <h1>Historical Manufactured Home Information</h1>
          <p class="mt-7">
            This is the current information for this registration as of
            <span class="font-weight-bold">{{ pacificDate(new Date()) }}</span>.
          </p>
        </v-col>
      </v-row>

      <!-- Tabbed Mhr History Tables -->
      <TabbedContainer
        :tabConfig="mhHistoryTabConfig"
        class="mt-4"
      >
        <template #tab-0>
          <SimpleTable
            :tableHeaders="homeDescriptionHeaders"
            :tableData="[]"
          />
        </template>
        <template #tab-1>
          <SimpleTable
            :tableHeaders="homeLocationHeaders"
            :tableData="[]"
          />
        </template>
        <template #tab-2>
          <SimpleTable
            :tableHeaders="homeOwnerHeaders"
            :tableData="[]"
          />
        </template>
      </TabbedContainer>
    </div>

    <!-- Footer -->
    <v-footer class="bg-white pt-4 pb-11">
      <v-container>
        <v-row noGutters>
          <v-col cols="12">
            <v-btn
              id="reg-back-btn"
              variant="outlined"
              color="primary"
              class="pr-5 float-right"
              @click="goToDash"
            >
              <v-icon
                color="primary"
                class="pt-1"
              >
                mdi-chevron-left
              </v-icon> Back
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-footer>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getMhrHistory, pacificDate } from '@/utils'
import { useAuth, useNavigation } from '@/composables'
import { getFeatureFlag } from '@/utils'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { TabbedContainer, SimpleTable } from '@/components/common'
import {
  homeDescriptionHeaders,
  homeLocationHeaders,
  homeOwnerHeaders,
  mhHistoryTabConfig
} from '@/resources/mhr-history'

/** Composables **/
const { isAuthenticated } = useAuth()
const { goToDash } = useNavigation()
const { getMhrInformation } = storeToRefs(useStore())

/** Props **/
const props = withDefaults(defineProps<{
  appReady?: boolean
}>(), {
  appReady: false
})

/** Local Properties **/
const dataLoaded = ref(true)
const loading = ref(false)
const mhrHistory = ref({})


onMounted(async (): Promise<void> => {
  // do not proceed if app is not ready
  // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
  if (!props.appReady || !isAuthenticated.value || !getFeatureFlag('mhr-history-enabled')) {
    await goToDash()
    return
  }

  // Fetch Manufactured Home History
  loading.value = true
  mhrHistory.value = await getMhrHistory(getMhrInformation.value?.mhrNumber)
  loading.value = false
})

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
.v-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 140px;
  background-color: #333;
}
</style>
