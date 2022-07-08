<template>
  <div id="mhr-review-confirm">
    <!-- Review and Confirm -->
    <section class="mt-10">
      <article>
        <h2>Review and Confirm</h2>
        <p class="mt-4">
          Review the information in your registration and complete the additional information below. If you need to
          change anything, return to the previous step to make the necessary change.
        </p>
      </article>

      <!-- Your Home Summary -->
      <YourHomeReview />

      <!-- Submitting Party Review -->
      <SubmittingPartyReview />
    </section>

    <!-- Transactional Folio Number -->
    <section id="folio-number-section" class="mt-10" v-if="false">
      <article>
        <h2>Folio or Reference Number</h2>
        <p class="mt-4">
          Enter the folio or reference number you want to use for this filing for your own tracking
          purposes. The Business Folio or Reference Number is displayed below (if available).
          Entering a different value below will not change the Business Folio or Reference Number.
          Only the number below will appear on the transaction report and receipt for this filing.
        </p>
      </article>

      <v-card flat class="mt-6">
       <!-- Folio Number Placeholder -->
      </v-card>
    </section>

    <!-- Certify -->
    <section id="certify-section" class="mt-10" v-if="false">
      <article>
        <h2>Certify</h2>
        <p class="mt-4">
          Confirm the legal name of the person authorized to complete and submit this dissolution.
        </p>
      </article>

      <v-card flat class="mt-6">
        <!-- Certify Placeholder -->
      </v-card>
    </section>

    <!-- Staff Payment -->
    <section id="staff-payment-section" class="mt-10" v-if="false">
      <article>
        <h2>Staff Payment</h2>
        <p class="mt-4"></p>
      </article>

      <v-card flat class="mt-6">
        <!-- Staff Payment Piece -->
      </v-card>
    </section>
  </div>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { Component, Vue } from 'vue-property-decorator'
import { SubmittingPartyReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
/* eslint-enable no-unused-vars */

@Component({
  components: {
    YourHomeReview,
    SubmittingPartyReview
  }
})
export default class MhrReviewConfirm extends Vue {
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
