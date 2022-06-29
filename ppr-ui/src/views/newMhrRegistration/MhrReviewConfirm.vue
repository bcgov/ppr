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
      <v-card flat id="mhr-registration-summary" class="mt-6">
        <header class="review-header">
          <v-icon class="ml-2" color="darkBlue">mdi-home</v-icon>
          <label class="font-weight-bold pl-2">Your Home</label>
        </header>

        <div :class="{ 'invalid-section': false }">
          <section class="mx-6 pt-8" v-if="true">
            <span>
              <v-icon color="error">mdi-information-outline</v-icon>
              <span class="error-text mx-1">This step is unfinished.</span>
              <router-link
                :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.YOUR_HOME}` }"
              >Return to this step to finish it</router-link>
            </span>
          </section>

          <!-- CSA Review -->
          <template v-if="isCSA || isEngineerInspection">
            <template v-if="isCSA">
              <v-row no-gutters class="pa-6">
                <v-col cols="3" class="pt-1">
                  <h3>CSA Number</h3>
                </v-col>
                <v-col cols="9" class="pt-1">
                  <p>{{ getMhrRegistrationHomeDescription.csaNumber || '(Not Entered)' }}</p>
                </v-col>
                <v-col cols="3" class="pt-1">
                  <h3>CSA Standard</h3>
                </v-col>
                <v-col cols="9" class="pt-1">
                  <p>{{ getMhrRegistrationHomeDescription.csaStandard || '(Not Entered)' }}</p>
                </v-col>
              </v-row>
            </template>

            <!-- Engineer Review -->
            <template v-if="isEngineerInspection">
              <v-row no-gutters class="pa-6">
                <v-col cols="3" class="pt-1">
                  <h3>Engineer's Name</h3>
                </v-col>
                <v-col cols="9" class="pt-1">
                  <p>{{ getMhrRegistrationHomeDescription.engineerName || '(Not Entered)' }}</p>
                </v-col>
                <v-col cols="3" class="pt-1">
                  <h3>Date of Engineer's<br>Report</h3>
                </v-col>
                <v-col cols="9" class="pt-1">
                  <p>{{ getMhrRegistrationHomeDescription.engineerReportDate || '(Not Entered)' }}</p>
                </v-col>
              </v-row>
            </template>
          </template>

          <!-- Default no Home Certification option is selected -->
          <template v-else>
            <v-row no-gutters class="pa-6">
              <v-col cols="3">
                <h3>Home Certification</h3>
              </v-col>
              <v-col cols="9">
                <p>(Not Entered)</p>
              </v-col>
            </v-row>
          </template>

          <!-- divider -->
          <div class="px-4">
            <v-divider />
          </div>

          <!-- Home Sections Review -->
          <template>
            <section class="py-6" id="review-home-sections">
              <h3 class="px-7">Home Sections</h3>
              <HomeSections class=" mt-n4 px-7 py-0" :isReviewMode="true" />
            </section>
          </template>

          <div class="px-4">
            <v-divider />
          </div>

          <!-- Rebuilt Status Review -->
          <v-row no-gutters class="pa-6">
            <v-col cols="3">
              <h3>Rebuilt Status</h3>
            </v-col>
            <v-col cols="9">
              <p>{{ getMhrRegistrationHomeDescription.rebuiltRemarks || '(Not Entered)' }}</p>
            </v-col>
          </v-row>

          <div class="px-4">
            <v-divider />
          </div>

          <!-- Other Information Review -->
          <v-row no-gutters class="pa-6">
            <v-col cols="3">
              <h3>Other Information</h3>
            </v-col>
            <v-col cols="9">
              <p>{{ getMhrRegistrationOtherInfo || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
        </div>
      </v-card>
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
import { HomeSections } from '@/components/mhrRegistration/YourHome'
import { HomeCertificationOptions, RouteNames } from '@/enums'
import { Getter } from 'vuex-class'
import { MhrRegistrationDescriptionIF } from '@/interfaces'
/* eslint-enable no-unused-vars */

@Component({
  components: {
    HomeSections
  }
})
export default class MhrReviewConfirm extends Vue {
  @Getter getMhrRegistrationOtherInfo!: string
  @Getter getMhrRegistrationHomeDescription!: MhrRegistrationDescriptionIF

  private HomeCertificationOptions = HomeCertificationOptions
  private RouteNames = RouteNames

  private get isCSA (): boolean {
    return this.getMhrRegistrationHomeDescription?.certificationOption === HomeCertificationOptions.CSA
  }

  private get isEngineerInspection (): boolean {
    return this.getMhrRegistrationHomeDescription?.certificationOption === HomeCertificationOptions.ENGINEER_INSPECTION
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.review-header {
  display: flex; // to align icons
  background-color: $BCgovBlue5O;
  padding: 1.25rem;
  color: $gray9;
}

#mhr-registration-summary {
  h3 {
    line-height: unset;
  }

  p {
    margin-bottom: unset;
    line-height: 24px;
    color: $gray7;
  }
}

#review-home-sections {
  ::v-deep {
    .theme--light.v-data-table > .v-data-table__wrapper > table > thead > tr:last-child > th:first-child {
      padding-left: 0 !important;
    }
  }
}
</style>
