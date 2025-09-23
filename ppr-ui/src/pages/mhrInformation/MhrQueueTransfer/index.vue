<script setup lang="ts">
import { HomeOwners } from '@/pages'
import { TransferDetailsReview } from '@/components/mhrTransfers'
import AccountInfo from '@/components/common/AccountInfo.vue'

</script>
<template>
  <div class="mx-auto py-6">

    <div class="grid grid-cols-1 lg:grid-cols-12">
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
            :current-home-owners="null"
          />
        </section>

        <section>
          <TransferDetailsReview class="py-6 pt-4 px-8" />
        </section>

        <section
          id="transfer-submitting-party"
          class="submitting-party mt-2"
        >
          <AccountInfo
            title="Submitting Party for this Change"
            tooltip-content="The default Submitting Party is based on your BC Registries
                       user account information. This information can be updated within your account settings."
            :account-info="null"

          />
        </section>
      </main>
    </div>
  </div>
</template>
<style lang="scss" scoped>
ol {
  list-style-type: revert;
}

</style>
