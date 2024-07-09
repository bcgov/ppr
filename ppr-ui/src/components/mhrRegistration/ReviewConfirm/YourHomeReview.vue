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
      <h3 class="fs-16 lh-24 ml-2">
        Description of Home
      </h3>
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
          <dl>
            <v-row
              noGutters
              class="px-8 key-value-pair"
            >
              <v-col cols="3">
                <dt>
                  Manufacturer's Name
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    class="mb-1"
                    :action="correctionState.action"
                    :baseline="correctionState.manufacturer.baseline"
                    :currentState="correctionState.manufacturer.currentState"
                  />
                </dt>
              </v-col>
              <v-col cols="9">
                <dd>{{ getMhrRegistrationHomeDescription.manufacturer || '(Not Entered)' }}</dd>
              </v-col>
            </v-row>
            <v-row
              noGutters
              class="pt-3 px-8 key-value-pair"
            >
              <v-col cols="3">
                <dt>
                  Year of Manufacture
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    class="mb-1"
                    :action="correctionState.action"
                    :baseline="correctionState.manufacturerYear.baseline"
                    :currentState="correctionState.manufacturerYear.currentState"
                  />
                </dt>
              </v-col>
              <v-col cols="9">
                <dd>
                  <template v-if="getMhrRegistrationHomeDescription.baseInformation.year">
                    {{ getMhrRegistrationHomeDescription.baseInformation.circa
                      ? 'Circa ' + getMhrRegistrationHomeDescription.baseInformation.year
                      : getMhrRegistrationHomeDescription.baseInformation.year
                    }}
                  </template>
                  <template v-else>
                    (Not Entered)
                  </template>
                </dd>
              </v-col>
            </v-row>
            <v-row
              noGutters
              class="pt-3 px-8 key-value-pair"
            >
              <v-col cols="3">
                <dt>
                  Make
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    class="mb-1"
                    :action="correctionState.action"
                    :baseline="correctionState.make.baseline"
                    :currentState="correctionState.make.currentState"
                  />
                </dt>
              </v-col>
              <v-col cols="9">
                <dd>{{ getMhrRegistrationHomeDescription.baseInformation.make || '(Not Entered)' }}</dd>
              </v-col>
            </v-row>
            <v-row
              noGutters
              class="pt-3 px-8 key-value-pair"
            >
              <v-col cols="3">
                <dt>
                  Model
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    class="mb-1"
                    :action="correctionState.action"
                    :baseline="correctionState.model.baseline"
                    :currentState="correctionState.model.currentState"
                  />
                </dt>
              </v-col>
              <v-col cols="9">
                <dd>{{ getMhrRegistrationHomeDescription.baseInformation.model || '(Not Entered)' }}</dd>
              </v-col>
            </v-row>
          </dl>
        </section>

        <v-divider class="mx-8" />

        <!-- Has no home certification is checked -->
        <template v-if="getMhrRegistrationHomeDescription.hasNoCertification">
          <dl>
            <v-row
              noGutters
              class="py-6 px-8 key-value-pair"
            >
              <v-col
                cols="3"
                data-test-id="home-certification-header-1"
              >
                <dt>
                  Home Certification
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    :action="correctionState.action"
                    :baseline="correctionState.homeCertification.baseline"
                    :currentState="correctionState.homeCertification.currentState"
                  />
                </dt>
              </v-col>
              <v-col
                cols="9"
                data-test-id="home-certification-content-1"
              >
                <dd>There is no certification available for this home.</dd>
              </v-col>
            </v-row>
          </dl>
        </template>

        <!-- CSA Review -->
        <template v-else-if="isCSA">
          <dl>
            <v-row
              noGutters
              class="py-6 px-8 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1"
                data-test-id="home-certification-header-1-csa"
              >
                <dt>CSA Number</dt>
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
                data-test-id="home-certification-content-1-csa"
              >
                <dd>{{ getMhrRegistrationHomeDescription.csaNumber || '(Not Entered)' }}</dd>
              </v-col>
              <v-col
                cols="3"
                class="pt-1"
                data-test-id="home-certification-header-2-csa"
              >
                <dt>
                  CSA Standard
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    :action="correctionState.action"
                    :baseline="correctionState.homeCertification.baseline"
                    :currentState="correctionState.homeCertification.currentState"
                  />
                </dt>
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
                data-test-id="home-certification-content-2-csa"
              >
                <dd>{{ getMhrRegistrationHomeDescription.csaStandard || '(Not Entered)' }}</dd>
              </v-col>
            </v-row>
          </dl>
        </template>

        <!-- Engineer Review -->
        <template v-else-if="isEngineerInspection">
          <dl>
            <v-row
              noGutters
              class="py-6 px-8 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1"
                data-test-id="home-certification-header-1-eng"
              >
                <dt>Engineer's Name</dt>
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
                data-test-id="home-certification-content-1-eng"
              >
                <dd>{{ getMhrRegistrationHomeDescription.engineerName || '(Not Entered)' }}</dd>
              </v-col>
              <v-col
                cols="3"
                class="pt-1"
                data-test-id="home-certification-header-2-eng"
              >
                <dt>
                  Date of Engineer's Report
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    :action="correctionState.action"
                    :baseline="correctionState.homeCertification.baseline"
                    :currentState="correctionState.homeCertification.currentState"
                  />
                </dt>
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
                data-test-id="home-certification-content-2-eng"
              >
                <dd>{{ engineerDisplayDate || '(Not Entered)' }}</dd>
              </v-col>
            </v-row>
          </dl>
        </template>

        <!-- No option selected -->
        <template v-else>
          <dl>
            <v-row
              noGutters
              class="py-6 px-8 key-value-pair"
            >
              <v-col cols="3">
                <dt>Home Certification</dt>
              </v-col>
              <v-col cols="9">
                <dd>(Not Entered)</dd>
              </v-col>
            </v-row>
          </dl>
        </template>

        <v-divider class="mx-8" />

        <!-- Home Sections Review -->
        <section
          id="review-home-sections"
          class="py-6"
        >
          <h4 class="fs-16 lh-24 px-8">
            Home Sections
          </h4>
          <HomeSections
            class="mt-n4 px-8 py-0"
            :isReviewMode="true"
          />
        </section>

        <template v-if="!isMhrManufacturerRegistration && !isExemption">
          <v-divider class="mx-8" />

          <!-- Rebuilt Status Review -->
          <dl>
            <v-row
              noGutters
              class="py-6 px-8 key-value-pair"
            >
              <v-col cols="3">
                <dt>
                  Rebuilt Status
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    :action="correctionState.action"
                    :baseline="correctionState.rebuilt.baseline"
                    :currentState="correctionState.rebuilt.currentState"
                  />
                </dt>
              </v-col>
              <v-col cols="9">
                <dd v-html="formatAsHtml(getMhrRegistrationHomeDescription.rebuiltRemarks) || '(Not Entered)'" />
              </v-col>
            </v-row>

            <v-divider class="mx-8" />

            <!-- Other Information Review -->
            <v-row
              noGutters
              class="py-6 px-8 key-value-pair"
            >
              <v-col cols="3">
                <dt>
                  Other Information
                  <UpdatedBadge
                    v-if="showUpdatedBadge"
                    :action="correctionState.action"
                    :baseline="correctionState.otherRemarks.baseline"
                    :currentState="correctionState.otherRemarks.currentState"
                  />
                </dt>
              </v-col>
              <v-col cols="9">
                <dd v-html="formatAsHtml(getMhrRegistrationOtherInfo) || '(Not Entered)'" />
              </v-col>
            </v-row>
          </dl>
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
import { useMhrCorrections, useMhrValidations, useUpdatedBadges } from '@/composables'
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
    const { correctionState } = useMhrCorrections()
    const { showUpdatedBadge } = useUpdatedBadges()

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
      showUpdatedBadge,
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
