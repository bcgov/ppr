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
        <section class="py-6 px-8">
          <dl class="flex-3-9 key-value-pair">
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
            <dd>{{ getMhrRegistrationHomeDescription.manufacturer || '(Not Entered)' }}</dd>
          </dl>
          <dl class="flex-3-9 key-value-pair mt-3">
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
            <dd>
              <span v-if="getMhrRegistrationHomeDescription.baseInformation.year">
                {{ getMhrRegistrationHomeDescription.baseInformation.circa
                  ? 'Circa ' + getMhrRegistrationHomeDescription.baseInformation.year
                  : getMhrRegistrationHomeDescription.baseInformation.year
                }}
              </span>
              <span v-else>
                (Not Entered)
              </span>
            </dd>
          </dl>
          <dl class="flex-3-9 key-value-pair mt-3">
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
            <dd>{{ getMhrRegistrationHomeDescription.baseInformation.make || '(Not Entered)' }}</dd>
          </dl>
          <dl class="flex-3-9 key-value-pair mt-3">
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
            <dd>{{ getMhrRegistrationHomeDescription.baseInformation.model || '(Not Entered)' }}</dd>
          </dl>
        </section>

        <v-divider class="mx-8" />

        <!-- Has no home certification is checked -->
        <template v-if="getMhrRegistrationHomeDescription.hasNoCertification">
          <dl class="flex-3-9 key-value-pair py-6 px-8">
            <dl data-test-id="home-certification-header-1">
              Home Certification
              <UpdatedBadge
                v-if="showUpdatedBadge"
                :action="correctionState.action"
                :baseline="correctionState.homeCertification.baseline"
                :currentState="correctionState.homeCertification.currentState"
              />
            </dl>
            <dt data-test-id="home-certification-content-1">
              There is no certification available for this home.
            </dt>
          </dl>
        </template>

        <!-- CSA Review -->
        <template v-else-if="isCSA">
          <dl class="flex-3-9 key-value-pair pt-6 pb-3 px-8">
            <dl data-test-id="home-certification-header-1-csa">
              CSA Number
            </dl>
            <dt data-test-id="home-certification-content-1-csa">
              {{ getMhrRegistrationHomeDescription.csaNumber || '(Not Entered)' }}
            </dt>
          </dl>

          <dl class="flex-3-9 key-value-pair pb-6 px-8">
            <dl data-test-id="home-certification-header-2-csa">
              CSA Standard
              <UpdatedBadge
                v-if="showUpdatedBadge"
                :action="correctionState.action"
                :baseline="correctionState.homeCertification.baseline"
                :currentState="correctionState.homeCertification.currentState"
              />
            </dl>
            <dt data-test-id="home-certification-content-2-csa">
              {{ getMhrRegistrationHomeDescription.csaStandard || '(Not Entered)' }}
            </dt>
          </dl>
        </template>

        <!-- Engineer Review -->
        <template v-else-if="isEngineerInspection">
          <dl class="flex-3-9 key-value-pair pt-6 pb-3 px-8">
            <dl data-test-id="home-certification-header-1-eng">
              Engineer's Name
            </dl>
            <dt data-test-id="home-certification-content-1-eng">
              {{ getMhrRegistrationHomeDescription.engineerName || '(Not Entered)' }}
            </dt>
          </dl>

          <dl class="flex-3-9 key-value-pair pb-6 px-8">
            <dl data-test-id="home-certification-header-2-eng">
              Date of Engineer's Report
              <UpdatedBadge
                v-if="showUpdatedBadge"
                :action="correctionState.action"
                :baseline="correctionState.homeCertification.baseline"
                :currentState="correctionState.homeCertification.currentState"
              />
            </dl>
            <dt data-test-id="home-certification-content-2-eng">
              {{ engineerDisplayDate || '(Not Entered)' }}
            </dt>
          </dl>
        </template>

        <!-- No option selected -->
        <template v-else>
          <dl class="flex-3-9 key-value-pair py-6 px-8">
            <dl>Home Certification</dl>
            <dt>(Not Entered)</dt>
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
          <dl class="flex-3-9 key-value-pair py-6 px-8">
            <dl>
              Rebuilt Status
              <UpdatedBadge
                v-if="showUpdatedBadge"
                :action="correctionState.action"
                :baseline="correctionState.rebuilt.baseline"
                :currentState="correctionState.rebuilt.currentState"
              />
            </dl>
            <dt><span v-html="formatAsHtml(getMhrRegistrationHomeDescription.rebuiltRemarks) || '(Not Entered)'" /></dt>
          </dl>

          <v-divider class="mx-8" />

          <!-- Other Information Review -->
          <dl class="flex-3-9 key-value-pair py-6 px-8">
            <dl>
              Other Information
              <UpdatedBadge
                v-if="showUpdatedBadge"
                :action="correctionState.action"
                :baseline="correctionState.otherRemarks.baseline"
                :currentState="correctionState.otherRemarks.currentState"
              />
            </dl>
            <dt><span v-html="formatAsHtml(getMhrRegistrationOtherInfo) || '(Not Entered)'" /></dt>
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
