<template>
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
          >Return to this step to complete it.</router-link>
        </span>
      </section>

      <!-- Manufacturer Make Model -->
      <section class="py-6">
        <v-row no-gutters class="px-6">
          <v-col cols="3">
            <h3>Manufacturer's Name</h3>
          </v-col>
          <v-col cols="9">
            <p>{{ getMhrRegistrationHomeDescription.manufacturer || '(Not Entered)' }}</p>
          </v-col>
        </v-row>
        <v-row no-gutters class="pt-3 px-6">
          <v-col cols="3">
            <h3>Year of Manufacture</h3>
          </v-col>
          <v-col cols="9">
            <p>{{ getMhrRegistrationHomeDescription.baseInformation.year || '(Not Entered)' }}</p>
          </v-col>
        </v-row>
        <v-row no-gutters class="pt-3 px-6">
          <v-col cols="3">
            <h3>Make</h3>
          </v-col>
          <v-col cols="9">
            <p>{{ getMhrRegistrationHomeDescription.baseInformation.make || '(Not Entered)'  }}</p>
          </v-col>
        </v-row>
        <v-row no-gutters class="pt-3 px-6">
          <v-col cols="3">
            <h3>Model</h3>
          </v-col>
          <v-col cols="9">
            <p>{{ getMhrRegistrationHomeDescription.baseInformation.model || '(Not Entered)'  }}</p>
          </v-col>
        </v-row>
      </section>

      <!-- divider -->
      <div class="px-4">
        <v-divider />
      </div>

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
              <h3>Date of Engineer's Report</h3>
            </v-col>
            <v-col cols="9" class="pt-1">
              <p>{{ engineerDisplayDate || '(Not Entered)' }}</p>
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
        <section class="pt-6" id="review-home-sections">
          <h3 class="px-6">Home Sections</h3>
          <HomeSections class="mt-n4 px-6 py-0" :isReviewMode="true" />
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
          <p v-html="formatAsHtml(getMhrRegistrationHomeDescription.rebuiltRemarks) || '(Not Entered)'"></p>
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
          <p v-html="formatAsHtml(getMhrRegistrationOtherInfo) || '(Not Entered)'"></p>
        </v-col>
      </v-row>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { HomeCertificationOptions, RouteNames } from '@/enums'
import { yyyyMmDdToPacificDate, formatAsHtml } from '@/utils'
import { HomeSections } from '@/components/mhrRegistration'

export default defineComponent({
  name: 'YourHomeReview',
  components: {
    HomeSections
  },
  props: {},
  setup () {
    const { getMhrRegistrationHomeDescription, getMhrRegistrationOtherInfo } = useGetters<any>([
      'getMhrRegistrationOtherInfo',
      'getMhrRegistrationHomeDescription'
    ])
    const localState = reactive({
      isCSA: computed((): boolean => {
        return getMhrRegistrationHomeDescription.value?.certificationOption === HomeCertificationOptions.CSA
      }),
      isEngineerInspection: computed((): boolean => {
        return getMhrRegistrationHomeDescription.value?.certificationOption ===
          HomeCertificationOptions.ENGINEER_INSPECTION
      }),
      engineerDisplayDate: computed((): string => {
        return yyyyMmDdToPacificDate(getMhrRegistrationHomeDescription.value?.engineerReportDate, true)
      })
    })

    return {
      formatAsHtml,
      RouteNames,
      getMhrRegistrationOtherInfo,
      getMhrRegistrationHomeDescription,
      ...toRefs(localState)
    }
  }
})
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

.error-text {
  font-size: 16px;
}

#review-home-sections {
  ::v-deep {
    .theme--light.v-data-table > .v-data-table__wrapper > table > thead > tr:last-child > th:first-child {
      padding-left: 0 !important;
    }
  }
}
</style>
