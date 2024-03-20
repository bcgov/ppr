<template>
  <v-card
    id="home-location-summary"
    flat
    class="mt-10"
  >
    <header
      v-if="!hideDefaultHeader"
      class="review-header"
    >
      <img
        class="ml-1 review-header-icon"
        alt="home-location-review-icon"
        src="@/assets/svgs/homelocationicon_reviewscreen.svg"
      >
      <label class="font-weight-bold pl-2">Location of Home</label>
    </header>

    <div
      :class="{
        'border-error-left': showStepError && !isTransferReview && !isTransportPermitReview && !isMhrCorrection
      }"
    >
      <section
        v-if="showStepError && !isTransferReview && !isTransportPermitReview && !isMhrCorrection"
        :class="{ 'pb-8': !(!!homeLocationInfo.locationType) && !hasAddress }"
        class="mx-6 pt-8"
      >
        <span>
          <v-icon color="error mt-n1">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link
            :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.HOME_LOCATION}` }"
          ><span>Return to this step to complete it.</span></router-link>
        </span>
      </section>

      <section
        v-if="(!!homeLocationInfo.locationType || hasAddress || isOwnLand !== null)"
        id="review-home-location-section"
        class="pt-5 pb-9"
      >
        <!-- Transport permit details rendered when there is an active permit -->
        <!-- add top margin to compensate negative bottom margin of the section tag -->
        <TransportPermitDetails
          v-if="hasActiveTransportPermit && !isChangeLocationActive && !isCorrectionReview"
          class="mt-5"
        />

        <v-row
          noGutters
          class="px-8"
        >
          <v-col
            cols="3"
            class="pt-1"
          >
            <h3>Location Type</h3>
          </v-col>
          <v-col
            cols="9"
            class="pt-1"
          >
            <p>{{ locationType }}</p>
          </v-col>
        </v-row>

        <!-- Lot Type -->
        <template v-if="homeLocationInfo.locationType === HomeLocationTypes.LOT">
          <v-row
            noGutters
            class="px-8 pt-1"
          >
            <v-col
              cols="3"
              class="pt-1 pr-3"
            >
              <h3>Dealer / Manufacturer Name</h3>
              <UpdatedBadge
                v-if="isAmendLocationActive && (isPadEditable || isTransportPermitReview)"
                action="AMENDED"
                :baseline="amendedBadgeLocationType.baseline"
                :currentState="amendedBadgeLocationType.currentState"
                isCaseSensitive
              />
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
            >
              <p>{{ homeLocationInfo.dealerName || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
        </template>

        <!-- Park Type -->
        <template v-if="homeLocationInfo.locationType === HomeLocationTypes.HOME_PARK">
          <v-row
            noGutters
            class="px-8 pt-1"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              <h3>Park Name</h3>
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
            >
              <p>{{ homeLocationInfo.parkName || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
          <v-row
            noGutters
            class="px-8 pt-1"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              <h3
                :class="{ 'error-text': isPadEditable && validate && !isNewPadNumberValid }"
              >
                Pad
              </h3>
              <UpdatedBadge
                v-if="isAmendLocationActive && (isPadEditable || isTransportPermitReview)"
                action="AMENDED"
                :baseline="amendedBadgeLocationType.baseline"
                :currentState="amendedBadgeLocationType.currentState"
                isCaseSensitive
              />
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
            >
              <p v-if="!isPadEditable">
                {{ homeLocationInfo.pad || '(Not Entered)' }}
              </p>
              <p v-else>
                <v-text-field
                  id="transport-permit-edit-pad"
                  ref="newPadNumberRef"
                  v-model="newTransportPermitPadNumber"
                  :rules="newPadRules"
                  variant="filled"
                  color="primary"
                  class=""
                  label="Pad"
                />
              </p>
            </v-col>
          </v-row>
        </template>

        <!-- Reserve -->
        <template v-if="homeLocationInfo.otherType === HomeLocationTypes.OTHER_RESERVE">
          <v-row
            noGutters
            class="px-8 pt-1"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              <h3>Legal Land Description</h3>
              <UpdatedBadge
                v-if="isAmendLocationActive && (isPadEditable || isTransportPermitReview)"
                action="AMENDED"
                :baseline="amendedBadgeLocationType.baseline"
                :currentState="amendedBadgeLocationType.currentState"
                isCaseSensitive
              />
            </v-col>
            <v-col
              v-if="hasManualEntries"
              cols="9"
              class="pt-1"
            >
              <p>Band Name: {{ homeLocationInfo.bandName || '(Not Entered)' }}</p>
              <p>Reserve Number: {{ homeLocationInfo.reserveNumber || '(Not Entered)' }}</p>
              <p v-if="homeLocationInfo.additionalDescription">
                Additional Description: {{ homeLocationInfo.additionalDescription }}
              </p>

              <p
                v-if="homeLocationInfo.lot"
                class="pt-4"
              >
                Lot: {{ homeLocationInfo.lot }}
              </p>
              <p v-if="homeLocationInfo.parcel">
                Parcel: {{ homeLocationInfo.parcel }}
              </p>
              <p v-if="homeLocationInfo.block">
                Block: {{ homeLocationInfo.block }}
              </p>
              <p v-if="homeLocationInfo.districtLot">
                District Lot: {{ homeLocationInfo.districtLot }}
              </p>
              <p v-if="homeLocationInfo.partOf">
                Part of: {{ homeLocationInfo.partOf }}
              </p>
              <p v-if="homeLocationInfo.section">
                Section: {{ homeLocationInfo.section }}
              </p>
              <p v-if="homeLocationInfo.township">
                Township: {{ homeLocationInfo.township }}
              </p>
              <p v-if="homeLocationInfo.range">
                Range: {{ homeLocationInfo.range }}
              </p>
              <p v-if="homeLocationInfo.meridian">
                Meridian: {{ homeLocationInfo.meridian }}
              </p>
              <p v-if="homeLocationInfo.landDistrict">
                Land District: {{ homeLocationInfo.landDistrict }}
              </p>
              <p v-if="homeLocationInfo.plan">
                Plan: {{ homeLocationInfo.plan }}
              </p>
              <p v-if="homeLocationInfo.exceptionPlan">
                Except Plan: {{ homeLocationInfo.exceptionPlan }}
              </p>
            </v-col>
            <v-col v-else>
              <p>(Not Entered)</p>
            </v-col>
          </v-row>
        </template>

        <!-- PID -->
        <template v-if="includesPid">
          <!-- PID Entered-->
          <template v-if="!getIsManualLocation">
            <v-row
              noGutters
              class="px-8 pt-1"
            >
              <v-col
                cols="3"
                class="pt-1"
              >
                <h3>PID Number</h3>
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
              >
                <p>{{ displayPid || '(Not Entered)' }}</p>
              </v-col>
            </v-row>
            <v-row
              v-if="homeLocationInfo.legalDescription"
              noGutters
              class="px-8 pt-1"
            >
              <v-col
                cols="3"
                class="pt-1"
              >
                <h3>Legal Land Description</h3>
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
              >
                <p>{{ homeLocationInfo.legalDescription }}</p>
              </v-col>
            </v-row>
          </template>

          <!-- No PID -->
          <v-row
            v-else
            noGutters
            class="px-8 pt-1"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              <h3>Legal Land Description</h3>
            </v-col>
            <v-col
              v-if="hasManualEntries"
              cols="9"
              class="pt-1"
            >
              <p
                v-if="homeLocationInfo.otherType !== HomeLocationTypes.OTHER_TYPE ||
                  homeLocationInfo.lot"
              >
                {{ displayStrata ? 'Strata ' : '' }}Lot: {{ homeLocationInfo.lot || '(Not Entered)' }}
              </p>
              <p v-if="homeLocationInfo.parcel">
                Parcel: {{ homeLocationInfo.parcel }}
              </p>
              <p v-if="homeLocationInfo.block">
                Block: {{ homeLocationInfo.block }}
              </p>
              <p v-if="homeLocationInfo.districtLot">
                District Lot: {{ homeLocationInfo.districtLot }}
              </p>
              <p v-if="homeLocationInfo.partOf">
                Part of: {{ homeLocationInfo.partOf }}
              </p>
              <p v-if="homeLocationInfo.section">
                Section: {{ homeLocationInfo.section }}
              </p>
              <p v-if="homeLocationInfo.township">
                Township: {{ homeLocationInfo.township }}
              </p>
              <p v-if="homeLocationInfo.range">
                Range: {{ homeLocationInfo.range }}
              </p>
              <p v-if="homeLocationInfo.meridian">
                Meridian: {{ homeLocationInfo.meridian }}
              </p>
              <p
                v-if="homeLocationInfo.otherType !== HomeLocationTypes.OTHER_TYPE ||
                  homeLocationInfo.landDistrict"
              >
                Land District: {{ homeLocationInfo.landDistrict || '(Not Entered)' }}
              </p>
              <p
                v-if="homeLocationInfo.otherType !== HomeLocationTypes.OTHER_TYPE ||
                  homeLocationInfo.plan"
              >
                {{ displayStrata ? 'Strata ' : '' }}Plan: {{ homeLocationInfo.plan || '(Not Entered)' }}
              </p>
              <p
                v-if="homeLocationInfo.exceptionPlan"
                class="pt-3 pb-1"
              >
                Except Plan: {{ homeLocationInfo.exceptionPlan }}
              </p>
            </v-col>
            <v-col
              v-else
              cols="9"
              class="pt-1"
            >
              <p>(Not Entered)</p>
            </v-col>
          </v-row>

          <!-- Additional Details -->
          <v-row
            noGutters
            class="px-8 pt-1"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              <h3>Additional Description</h3>
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
            >
              <p>{{ homeLocationInfo.additionalDescription || '(Not Entered)' }}</p>
            </v-col>
          </v-row>
        </template>

        <!-- Civic Address -->
        <v-divider class="mx-8 mt-6" />
        <v-row
          noGutters
          class="px-8 pt-5"
        >
          <v-col
            cols="3"
            class="pt-1"
          >
            <h3>Civic Address</h3>
            <UpdatedBadge
              v-if="isAmendLocationActive && isTransportPermitReview"
              action="AMENDED"
              :baseline="amendedBadgeCivicAddress.baseline"
              :currentState="amendedBadgeCivicAddress.currentState"
              isCaseSensitive
            />
          </v-col>
          <v-col
            cols="9"
            class="pt-1"
          >
            <p v-if="hasAddress">
              <span v-if="!!homeLocationInfo.address.street">
                {{ homeLocationInfo.address.street }}<br>
              </span>
              <span v-if="!!homeLocationInfo.address.streetAdditional">
                {{ homeLocationInfo.address.streetAdditional }}<br>
              </span>
              {{ homeLocationInfo.address.city }}
              {{ homeLocationInfo.address.region }}
              <br>{{ getCountryName(homeLocationInfo.address.country) }}
            </p>
            <p v-else>
              {{ '(Not Entered)' }}
            </p>
          </v-col>
        </v-row>
        <template
          v-if="!isMhrManufacturerRegistration && !isTransferReview && !hideLandLease && !isCorrectionReview"
        >
          <v-divider class="mx-8 mt-6" />

          <!-- Land Details -->
          <v-row
            noGutters
            class="px-8 pt-6"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              <h3>Land Details</h3>
            </v-col>
          </v-row>

          <!-- Lease or Land Ownership -->
          <v-row
            noGutters
            class="px-8 pt-1"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              <h3>Lease or Land <br>Ownership</h3>
              <UpdatedBadge
                v-if="isAmendLocationActive && (isPadEditable || isTransportPermitReview)"
                action="AMENDED"
                :baseline="amendedBadgeLandDetails.baseline"
                :currentState="amendedBadgeLandDetails.currentState"
              />
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
            >
              <p>
                <span v-html="landOwnershipLabel" />
              </p>
            </v-col>
          </v-row>
        </template>

        <!-- Tax Certificate -->
        <template v-if="isTransportPermitReview && showTaxCertificateExpiryDate">
          <v-divider class="mx-8 mt-7 mb-6" />
          <v-row
            noGutters
            class="px-8"
          >
            <v-col cols="3">
              <h3>Tax Certificate <br>Expiry Date</h3>
            </v-col>
            <v-col cols="9">
              <p>{{ shortPacificDate(homeLocationInfo.taxExpiryDate) }}</p>
            </v-col>
          </v-row>
        </template>
      </section>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from 'vue'
import { HomeLocationTypes, LocationChangeTypes, RouteNames } from '@/enums'
import { useStore } from '@/store/store'
import {
  useInputRules,
  useMhrCorrections,
  useMhrInfoValidation,
  useMhrValidations,
  useTransportPermits
} from '@/composables'
import { storeToRefs } from 'pinia'
import { useCountriesProvinces } from '@/composables/address/factories'
import { FormIF, MhrRegistrationHomeLocationIF } from '@/interfaces'
import { shortPacificDate } from '@/utils/date-helper'
import { TransportPermitDetails } from '@/components/mhrTransportPermit'
import { UpdatedBadge } from '@/components/common'

export default defineComponent({
  name: 'HomeLocationReview',
  components: { TransportPermitDetails, UpdatedBadge },
  props: {
    hideDefaultHeader: {
      type: Boolean,
      default: false
    },
    validate: {
      type: Boolean,
      default: false
    },
    isTransferReview: {
      type: Boolean,
      default: false
    },
    isTransportPermitReview: {
      type: Boolean,
      default: false
    },
    isCorrectionReview: {
      type: Boolean,
      default: false
    },
    isPadEditable: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {

    const newPadNumberRef = ref(null) as FormIF

    const { setMhrTransportPermitNewPad, setUnsavedChanges } = useStore()
    const {
      getMhrRegistrationLocation,
      getMhrRegistrationValidationModel,
      getIsManualLocation,
      getMhrRegistrationOwnLand,
      isMhrManufacturerRegistration,
      getMhrInfoValidation,
      getMhrTransportPermit,
      getMhrOriginalTransportPermit,
      getMhrOriginalTransportPermitHomeLocation,
      getMhrTransportPermitHomeLocation
    } = storeToRefs(useStore())

    const {
      MhrSectVal,
      getStepValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { setValidation } = useMhrInfoValidation(getMhrInfoValidation.value)
    const countryProvincesHelpers = useCountriesProvinces()
    const { required, notEqualTo, customRules } = useInputRules()
    const {
      hasActiveTransportPermit,
      isChangeLocationActive,
      isAmendLocationActive,
      isNotManufacturersLot,
      isMovingWithinSamePark
    } = useTransportPermits()
    const { isMhrCorrection } = useMhrCorrections()

    const homeLocationInfo: MhrRegistrationHomeLocationIF =
      props.isTransportPermitReview ? getMhrTransportPermit.value.newLocation : getMhrRegistrationLocation.value

    const localState = reactive({
      // transport permit
      currentPadNumber: homeLocationInfo.pad,
      newTransportPermitPadNumber: '',
      showTaxCertificateExpiryDate: homeLocationInfo.taxCertificate
        && isNotManufacturersLot.value && !isMovingWithinSamePark.value,
      isNewPadNumberValid: false,
      amendedBadgeLocationType: {
        baseline: getMhrOriginalTransportPermitHomeLocation.value,
        currentState: computed(() => getMhrTransportPermitHomeLocation.value)
      },
      amendedBadgeCivicAddress: {
        baseline: getMhrOriginalTransportPermit.value?.newLocation?.address,
        currentState: computed(() => getMhrTransportPermit.value?.newLocation?.address)
      },
      amendedBadgeLandDetails: {
        baseline: getMhrOriginalTransportPermit.value?.ownLand,
        currentState: computed(() => getMhrTransportPermit.value?.ownLand)
      },
      hideLandLease: props.isTransportPermitReview &&
        getMhrTransportPermit.value.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK,

      includesPid: computed((): boolean => {
        return [HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE]
          .includes(homeLocationInfo.otherType)
      }),
      hasAddress: computed((): boolean => {
        return !!(homeLocationInfo.address?.street ||
        homeLocationInfo.address?.streetAdditional ||
        homeLocationInfo.address?.city)
      }),
      displayPid: computed((): string => {
        return homeLocationInfo.pidNumber?.replace(/(\d{3})(\d{3})(\d{3})/, '$1-$2-$3')
      }),
      displayStrata: computed((): boolean => {
        return homeLocationInfo.otherType === HomeLocationTypes.OTHER_STRATA
      }),
      locationType: computed((): string => {
        switch (homeLocationInfo.locationType) {
          case HomeLocationTypes.LOT:
            return 'Dealer\'s / Manufacturer\'s lot'
          case HomeLocationTypes.HOME_PARK:
            return 'Manufactured home park (other than a strata park)'
          case HomeLocationTypes.OTHER_LAND:
            switch (homeLocationInfo.otherType) {
              case HomeLocationTypes.OTHER_RESERVE:
                return 'Indian Reserve'
              case HomeLocationTypes.OTHER_STRATA:
                return 'Strata'
              case HomeLocationTypes.OTHER_TYPE:
                return 'Other'
              default:
                return '(Not Entered)'
            }
          default:
            return '(Not Entered)'
        }
      }),
      hasManualEntries: computed((): boolean => {
        const location = homeLocationInfo
        return !!location.lot || !!location.parcel || !!location.block || !!location.districtLot || !!location.partOf ||
          !!location.section || !!location.township || !!location.range || !!location.meridian || !!location.bandName ||
          !!location.landDistrict || !!location.plan || !!location.exceptionPlan || !!location.reserveNumber
      }),
      isOwnLand: computed(() => props.isTransportPermitReview
        ? getMhrTransportPermit.value.ownLand
        : getMhrRegistrationOwnLand.value),
      landOwnershipLabel: computed(() => {
        if (localState.isOwnLand === null) return '(Not Entered)'
        return `The manufactured home is<b>${localState.isOwnLand ? '' : ' not'}</b> located on land that the
            homeowners own or on land that they have a registered lease of 3 years or more.`
      }),
      showStepError: computed(() => {
        return !isMhrManufacturerRegistration.value && !getStepValidation(MhrSectVal.LOCATION_VALID)
      }),
      newPadRules: computed(() =>
        customRules(required('Enter pad'), notEqualTo(localState.currentPadNumber, 'Must be a different pad'))
      )
    })

    onMounted(async (): Promise<void> => {
      if (props.validate) newPadNumberRef.value?.validate()
    })

    watch(() => localState.newTransportPermitPadNumber, (val, oldVal) => {
      setMhrTransportPermitNewPad(val)
      // new Pad should be different than the current one
      localState.isNewPadNumberValid = val && localState.currentPadNumber !== val
      setValidation('isNewPadNumberValid', localState.isNewPadNumberValid)
      // when prefilling the pad number (when no initial value exists), do not trigger saved changes
      !!oldVal && setUnsavedChanges(true)
    })

    watch(() => props.validate, async () => {
      newPadNumberRef.value?.validate()
    })

    // if editing Pad number - get the value from either Permit or Registration
    watch(() => props.isPadEditable, async () => {
      if (props.isPadEditable) {
        localState.newTransportPermitPadNumber =
          getMhrTransportPermit.value.newLocation.pad || structuredClone(homeLocationInfo.pad)
      }
    }, { immediate: true })

    return {
      homeLocationInfo,
      newPadNumberRef,
      HomeLocationTypes,
      RouteNames,
      MhrSectVal,
      getStepValidation,
      getIsManualLocation,
      isMhrManufacturerRegistration,
      shortPacificDate,
      getMhrRegistrationLocation,
      ...countryProvincesHelpers,
      hasActiveTransportPermit,
      isNotManufacturersLot,
      isAmendLocationActive,
      isChangeLocationActive,
      isMhrCorrection,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#home-location-summary {
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
</style>
