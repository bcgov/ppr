<script setup lang="ts">
import { HomeOwners } from '@/pages'
import { getFeatureFlag, parseSubmittingPartyToAccountInfo } from '@/utils'
import AccountInfo from '@/components/common/AccountInfo.vue'
import { getQueuedTransfer } from '@/utils/mhr-api-helper'
import type { MhrTransferApiIF } from '@/interfaces'

const { goToDash } = useNavigation()
const { initDraftMhrInformation } = useMhrInformation()
const {
  getMhrInformation, isRoleStaffReg, getMhrTransferCurrentHomeOwnerGroups, getMhrAccountSubmittingParty
} = storeToRefs(useStore())

const isLoading = ref(false)
const queueTransfer = ref(null)

onMounted(async () => {
  isLoading.value = true
  // On Mounted: route to dashboard if the feature flag is false, no reviewId, or not staff
  if (!getFeatureFlag('enable-analyst-queue') || !getMhrInformation.value?.reviewId || !isRoleStaffReg.value) {
   goToDash()
  }

  // Fetch the queued transfer details and initialize the draft
  queueTransfer.value = await getQueuedTransfer(getMhrInformation.value?.reviewId)
  await initDraftMhrInformation(queueTransfer.value as MhrTransferApiIF)
  isLoading.value = false

})
</script>
<template>
  <div class="mx-auto pb-4">
    <template v-if="isLoading">
      <div class="fixed left-0 top-0 h-full w-full z-50 bg-gray-300 opacity-45" />
      <UIcon
        name="i-mdi-loading"
        class="animate-spin text-[50px] text-blue-500 absolute top-40 left-[50%]"
      />
    </template>

    <div v-else class="grid grid-cols-1 lg:grid-cols-12">
      <!-- Main column -->
      <main class="lg:col-span-9 pr-2">
        <!-- Review Header -->
        <header class="review-header mt-10 rounded-top">
          <v-icon
            class="ml-2"
            color="darkBlue"
          >
            mdi-file-document-multiple
          </v-icon>
          <h3 class="fs-16 lh-24 ml-2">
            Ownership Transfer or Change
          </h3>
        </header>

        <section
          id="owners-review"
          class="mt-9"
        >
          <HomeOwners
            is-mhr-transfer
            is-readonly-table
            :current-home-owners="getMhrTransferCurrentHomeOwnerGroups"
          />
        </section>

        <section>
          <TransferDetailsReview class="py-6 pt-4 px-8" />
        </section>

        <section
          id="transfer-submitting-party"
          class="submitting-party mt-9"
        >
          <AccountInfo
            title="Submitting Party for this Change"
            tooltip-content="The default Submitting Party is based on your BC Registries
                       user account information. This information can be updated within your account settings."
            is-queue-transfer
            :account-info="parseSubmittingPartyToAccountInfo(getMhrAccountSubmittingParty)"

          />
        </section>

        <section class="my-9">
          <UploadedDocuments :document-list="queueTransfer?.documents" />
        </section>
      </main>
    </div>
  </div>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
