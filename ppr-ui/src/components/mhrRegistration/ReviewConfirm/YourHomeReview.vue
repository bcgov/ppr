<template>
  <v-card
    id="mhr-registration-summary"
    flat
    class="mt-10"
  >
    <header class="review-header">
      <v-icon
        class="ml-1"
        color="darkBlue"
      >
        mdi-home
      </v-icon>
      <label class="font-weight-bold pl-2">{{ isTransferReview ? 'Description of Home' : 'Your Home' }}</label>
    </header>

    <div :class="{'border-error-left': showStepError && !isTransferReview }">
      <section
        v-if="showStepError && !isTransferReview"
        class="mx-6 pt-8"
        :class="{ 'pb-8': !hasData}"
      >
        <span>
          <v-icon color="error mt-n1">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link
            :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.YOUR_HOME}` }"
          ><span>Return to this step to complete it.</span></router-link>
        </span>
      </section>

      <template v-if="hasData">
        <!-- Manufacturer Make Model -->
        <section class="py-6">
          <v-row
            noGutters
            class="px-8"
          >
            <v-col cols="3">
              <h3>Manufacturer's Name</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                class="mb-1"
                :baseline="correctionState.manufacturer.baseline"
                :currentState="correctionState.manufacturer.currentState"
              />
            </v-col>
            <v-col cols="9">
              <p>{{ getMhrRegistrationHomeDescription.manufacturer || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
          <v-row
            noGutters
            class="pt-3 px-8"
          >
            <v-col cols="3">
              <h3>Year of Manufacture</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                class="mb-1"
                :baseline="correctionState.manufacturerYear.baseline"
                :currentState="correctionState.manufacturerYear.currentState"
              />
            </v-col>
            <v-col cols="9">
              <p v-if="getMhrRegistrationHomeDescription.baseInformation.year">
                {{ getMhrRegistrationHomeDescription.baseInformation.circa
                  ? 'Circa ' + getMhrRegistrationHomeDescription.baseInformation.year
                  : getMhrRegistrationHomeDescription.baseInformation.year
                }}
              </p>
              <p v-else>
                (Not Entered)
              </p>
            </v-col>
          </v-row>
          <v-row
            noGutters
            class="pt-3 px-8"
          >
            <v-col cols="3">
              <h3>Make</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                class="mb-1"
                :baseline="correctionState.make.baseline"
                :currentState="correctionState.make.currentState"
              />
            </v-col>
            <v-col cols="9">
              <p>{{ getMhrRegistrationHomeDescription.baseInformation.make || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
          <v-row
            noGutters
            class="pt-3 px-8"
          >
            <v-col cols="3">
              <h3>Model</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                class="mb-1"
                :baseline="correctionState.model.baseline"
                :currentState="correctionState.model.currentState"
              />
            </v-col>
            <v-col cols="9">
              <p>{{ getMhrRegistrationHomeDescription.baseInformation.model || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
        </section>

        <v-divider class="mx-8" />

        <!-- Has no home certification is checked -->
        <template v-if="getMhrRegistrationHomeDescription.hasNoCertification">
          <v-row
            noGutters
            class="py-6 px-8"
          >
            <v-col
              cols="3"
              data-test-id="home-certification-header-1"
            >
              <h3>Home Certification</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                :baseline="correctionState.homeCertification.baseline"
                :currentState="correctionState.homeCertification.currentState"
              />
            </v-col>
            <v-col
              cols="9"
              data-test-id="home-certification-content-1"
            >
              <p>There is no certification available for this home.</p>
            </v-col>
          </v-row>
        </template>

        <!-- CSA Review -->
        <template v-else-if="isCSA">
          <v-row
            noGutters
            class="py-6 px-8"
          >
            <v-col
              cols="3"
              class="pt-1"
              data-test-id="home-certification-header-1-csa"
            >
              <h3>CSA Number</h3>
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
              data-test-id="home-certification-content-1-csa"
            >
              <p>{{ getMhrRegistrationHomeDescription.csaNumber || '(Not Entered)' }}</p>
            </v-col>
            <v-col
              cols="3"
              class="pt-1"
              data-test-id="home-certification-header-2-csa"
            >
              <h3>CSA Standard</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                :baseline="correctionState.homeCertification.baseline"
                :currentState="correctionState.homeCertification.currentState"
              />
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
              data-test-id="home-certification-content-2-csa"
            >
              <p>{{ getMhrRegistrationHomeDescription.csaStandard || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
        </template>

        <!-- Engineer Review -->
        <template v-else-if="isEngineerInspection">
          <v-row
            noGutters
            class="py-6 px-8"
          >
            <v-col
              cols="3"
              class="pt-1"
              data-test-id="home-certification-header-1-eng"
            >
              <h3>Engineer's Name</h3>
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
              data-test-id="home-certification-content-1-eng"
            >
              <p>{{ getMhrRegistrationHomeDescription.engineerName || '(Not Entered)' }}</p>
            </v-col>
            <v-col
              cols="3"
              class="pt-1"
              data-test-id="home-certification-header-2-eng"
            >
              <h3>Date of Engineer's Report</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                :baseline="correctionState.homeCertification.baseline"
                :currentState="correctionState.homeCertification.currentState"
              />
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
              data-test-id="home-certification-content-2-eng"
            >
              <p>{{ engineerDisplayDate || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
        </template>

        <!-- No option selected -->
        <template v-else>
          <v-row
            noGutters
            class="py-6 px-8"
          >
            <v-col cols="3">
              <h3>Home Certification</h3>
            </v-col>
            <v-col cols="9">
              <p>(Not Entered)</p>
            </v-col>
          </v-row>
        </template>

        <v-divider class="mx-8" />

        <!-- Home Sections Review -->
        <section
          id="review-home-sections"
          class="py-6"
        >
          <h3 class="px-8">
            Home Sections
          </h3>
          <HomeSections
            class="mt-n4 px-8 py-0"
            :isReviewMode="true"
          />
        </section>

        <template v-if="!isMhrManufacturerRegistration && !isExemption">
          <v-divider class="mx-8" />

          <!-- Rebuilt Status Review -->
          <v-row
            noGutters
            class="py-6 px-8"
          >
            <v-col cols="3">
              <h3>Rebuilt Status</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                :baseline="correctionState.rebuilt.baseline"
                :currentState="correctionState.rebuilt.currentState"
              />
            </v-col>
            <v-col cols="9">
              <p v-html="formatAsHtml(getMhrRegistrationHomeDescription.rebuiltRemarks) || '(Not Entered)'" />
            </v-col>
          </v-row>

          <v-divider class="mx-8" />

          <!-- Other Information Review -->
          <v-row
            noGutters
            class="py-6 px-8"
          >
            <v-col cols="3">
              <h3>Other Information</h3>
              <UpdatedBadge
                v-if="isMhrCorrection"
                :baseline="correctionState.otherRemarks.baseline"
                :currentState="correctionState.otherRemarks.currentState"
              />
            </v-col>
            <v-col cols="9">
              <p v-html="formatAsHtml(getMhrRegistrationOtherInfo) || '(Not Entered)'" />
            </v-col>
          </v-row>
        </template>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { HomeCertificationOptions, RouteNames } from '@/enums'
import { yyyyMmDdToPacificDate, formatAsHtml, hasTruthyValue } from '@/utils'
import { HomeSections } from '@/components/mhrRegistration'
import { useMhrCorrections, useMhrValidations } from '@/composables'
import { storeToRefs } from 'pinia'
import { UpdatedBadge } from '@/components/common'

export default defineComponent({
  name: 'YourHomeReview',
  components: {
    UpdatedBadge,
    HomeSections
  },
  props: {
    isTransferReview: {
      type: Boolean,
      default: false
    },
    isExemption: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const {
      getMhrRegistrationHomeDescription,
      getMhrRegistrationOtherInfo,
      getMhrRegistrationValidationModel,
      isMhrManufacturerRegistration
    } = storeToRefs(useStore())

    const {
      MhrSectVal,
      getStepValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { correctionState, isMhrCorrection } = useMhrCorrections()

    const localState = reactive({
      isCSA: computed((): boolean => {
        return getMhrRegistrationHomeDescription.value?.certificationOption === HomeCertificationOptions.CSA
      }),
      isEngineerInspection: computed((): boolean => {
        return getMhrRegistrationHomeDescription.value?.certificationOption ===
          HomeCertificationOptions.ENGINEER_INSPECTION
      }),
      engineerDisplayDate: computed((): string => {
        const engineersDate = props.isTransferReview
          ? getMhrRegistrationHomeDescription.value?.engineerDate?.split('T')[0]
          : getMhrRegistrationHomeDescription.value?.engineerDate

        return yyyyMmDdToPacificDate(engineersDate, true)
      }),
      showStepError: computed(() => !getStepValidation(MhrSectVal.YOUR_HOME_VALID)),
      hasData: computed(() : boolean => {
        return hasTruthyValue(getMhrRegistrationHomeDescription.value) ||
          (!isMhrManufacturerRegistration.value && !!getMhrRegistrationOtherInfo.value)
      })
    })

    return {
      formatAsHtml,
      RouteNames,
      correctionState,
      isMhrCorrection,
      getMhrRegistrationOtherInfo,
      getMhrRegistrationHomeDescription,
      isMhrManufacturerRegistration,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
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

table {
  th:first-child,
  td:first-child {
    padding-left: 0 !important;
  }
}
</style>
