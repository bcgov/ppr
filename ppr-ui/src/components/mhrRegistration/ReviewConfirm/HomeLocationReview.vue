<template>
  <v-card
    id="home-location-summary"
    flat
    class="mt-10 home-location-review"
  >
    <header
      v-if="!hideDefaultHeader"
      class="review-header d-flex"
    >
      <img
        class="ml-1 review-header-icon"
        alt="home-location-review-icon"
        src="@/assets/svgs/homelocationicon_reviewscreen.svg"
      >
      <h3 class="fs-16 lh-24 ml-2">
        Location of Home
      </h3>
    </header>
    <div
      v-if="isCancelChangeLocationActive && !isCancelTransportPermitReview && !hideSectionHeader"
      class="px-8 mt-5 mb-n5"
    >
      <div class="d-flex align-center">
        <img
          v-if="isPrevTransportPermitLocation"
          width="25"
          src="@/assets/svgs/homelocationicon_reviewscreen.svg"
        >
        <img
          v-else
          width="25"
          src="@/assets/svgs/icon_cancel_permit.svg"
        >
        <h4 class="fs-16 lh-24 pl-2">
          {{ isPrevTransportPermitLocation ? 'Restored Location' : 'Cancelled Location' }}
        </h4>
      </div>
      <v-divider
        class="border-opacity-15 mt-4"
      />
    </div>

    <div
      :class="[
        {'border-error-left': showStepError && !isTransferReview && !isTransportPermitReview && !isMhrCorrection},
        {'cancelled-location-info': isCancelChangeLocationActive && !isPrevTransportPermitLocation &&
          !isCancelTransportPermitReview && !isCancelledTransportPermitDetails},
        {'restored-location-info': isCancelChangeLocationActive && isPrevTransportPermitLocation}
      ]"
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
        class="pb-9"
      >
        <v-row
          v-if="isCancelChangeLocationActive && isPrevTransportPermitLocation"
          noGutters
          class="px-8 my-5 pt-5"
        >
          <v-col>
            <p>
              This is the location of the home prior to the transport permit being issued and will be the
              registered location of the home.
            </p>
          </v-col>
        </v-row>

        <!-- Transport permit details rendered when there is an active permit -->
        <!-- add top margin to compensate negative bottom margin of the section tag -->
        <TransportPermitDetails
          v-if="hasActiveTransportPermit &&
            !isChangeLocationActive &&
            !isCorrectionReview &&
            !isPrevTransportPermitLocation &&
            !isCancelTransportPermitReview"
          :isCancelledLocation="isCancelledTransportPermitDetails"
          :isVoidPermit="isExemptionWithActiveTransportPermit"
          :infoText="exemptionWithActivePermitText"
          class="mt-5"
        />

        <!-- Details of Cancelled Transport Permit should be greyed out -->
        <span
          :class="{'disabled-text': isCancelledTransportPermitDetails }"
        >
          <v-row
            noGutters
            class="pt-5 px-8 key-value-pair"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              Location Type
            </v-col>
            <v-col
              cols="9"
              class="pt-1"
            >
              {{ locationType }}
            </v-col>
          </v-row>

          <!-- Lot Type -->
          <template v-if="homeLocationInfo.locationType === HomeLocationTypes.LOT">
            <v-row
              noGutters
              class="px-8 pt-1 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1 pr-3"
              >
                Dealer / Manufacturer Name
                <UpdatedBadge
                  v-if="isAmendLocationActive && (isPadEditable || isTransportPermitReview)"
                  action="AMENDED"
                  :baseline="amendedBadgeLocationType.baseline"
                  :currentState="amendedBadgeLocationType.currentState"
                  isCaseSensitive
                />
                <UpdatedBadge
                  v-else-if="isMhrReRegistration"
                  class="mb-1"
                  :action="correctionState.action"
                  :baseline="correctionState.location.baseline"
                  :currentState="correctionState.location.currentState"
                />
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
              >
                {{ homeLocationInfo.dealerName || '(Not Entered)' }}
              </v-col>
            </v-row>
          </template>

          <!-- Park Type -->
          <template v-if="homeLocationInfo.locationType === HomeLocationTypes.HOME_PARK">
            <v-row
              noGutters
              class="px-8 pt-1 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1"
              >
                Park Name
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
              >
                {{ homeLocationInfo.parkName || '(Not Entered)' }}
              </v-col>
            </v-row>
            <v-row
              noGutters
              class="px-8 pt-1 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1"
              >
                <span
                  :class="{ 'error-text': isPadEditable && validate && !isNewPadNumberValid }"
                >
                  Pad
                </span>
                <UpdatedBadge
                  v-if="isAmendLocationActive && (isPadEditable || isTransportPermitReview)"
                  action="AMENDED"
                  :baseline="amendedBadgeLocationType.baseline"
                  :currentState="amendedBadgeLocationType.currentState"
                  isCaseSensitive
                />
                <UpdatedBadge
                  v-else-if="isMhrReRegistration"
                  class="mb-1"
                  :action="correctionState.action"
                  :baseline="correctionState.location.baseline"
                  :currentState="correctionState.location.currentState"
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
              class="px-8 pt-1 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1"
              >
                Legal Land Description
                <UpdatedBadge
                  v-if="isAmendLocationActive && (isPadEditable || isTransportPermitReview)"
                  action="AMENDED"
                  :baseline="amendedBadgeLocationType.baseline"
                  :currentState="amendedBadgeLocationType.currentState"
                  isCaseSensitive
                />
                <UpdatedBadge
                  v-else-if="isMhrReRegistration"
                  class="mb-1"
                  :action="correctionState.action"
                  :baseline="correctionState.location.baseline"
                  :currentState="correctionState.location.currentState"
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
            <template v-if="!isManualLocation">
              <v-row
                noGutters
                class="px-8 pt-1 key-value-pair"
              >
                <v-col
                  cols="3"
                  class="pt-1 key-value-pair"
                >
                  PID Number
                </v-col>
                <v-col
                  cols="9"
                  class="pt-1"
                >
                  {{ displayPid || '(Not Entered)' }}
                </v-col>
              </v-row>
              <v-row
                v-if="homeLocationInfo.legalDescription"
                noGutters
                class="px-8 pt-1 key-value-pair"
              >
                <v-col
                  cols="3"
                  class="pt-1"
                >
                  Legal Land Description
                </v-col>
                <v-col
                  cols="9"
                  class="pt-1"
                >
                  {{ homeLocationInfo.legalDescription }}
                </v-col>
              </v-row>
            </template>

            <!-- No PID -->
            <v-row
              v-else
              noGutters
              class="px-8 pt-1 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1"
              >
                Legal Land Description
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
                (Not Entered)
              </v-col>
            </v-row>

            <!-- Additional Details -->
            <v-row
              noGutters
              class="px-8 pt-1 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1"
              >
                Additional Description
              </v-col>
              <v-col
                cols="9"
                class="pt-1"
              >
                {{ homeLocationInfo.additionalDescription || '(Not Entered)' }}
              </v-col>
            </v-row>
          </template>

          <!-- Location Type Corrections Row -->
          <v-row
            noGutters
            class="px-8"
          >
            <v-col>
              <UpdatedBadge
                v-if="isMhrCorrection || (isMhrReRegistration && includesPid)"
                class="mb-1"
                :action="correctionState.action"
                :baseline="correctionState.location.baseline"
                :currentState="correctionState.location.currentState"
              />
              <InfoChip
                v-if="isCancelTransportPermitReview"
                class="mt-2"
                action="RESTORED"
              />
            </v-col>
          </v-row>

          <!-- Civic Address -->
          <v-divider class="mx-8 mt-6" />
          <v-row
            noGutters
            class="px-8 pt-5 key-value-pair"
          >
            <v-col
              cols="3"
              class="pt-1"
            >
              Civic Address
              <UpdatedBadge
                v-if="showUpdatedBadge"
                class="mb-1"
                :action="correctionState.action"
                :baseline="correctionState.civicAddress.baseline"
                :currentState="correctionState.civicAddress.currentState"
              />
              <UpdatedBadge
                v-if="isAmendLocationActive && isTransportPermitReview"
                action="AMENDED"
                :baseline="amendedBadgeCivicAddress.baseline"
                :currentState="amendedBadgeCivicAddress.currentState"
                isCaseSensitive
              />
              <InfoChip
                v-if="isCancelTransportPermitReview"
                class="mt-2"
                action="RESTORED"
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
            v-if="!isMhrManufacturerRegistration && !isTransferReview && !hideLandLease &&
              !(isMhrCorrection && hasActiveTransportPermit) && !isCancelChangeLocationActive"
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
                <h4 class="fs-16 lh-24">Land Details</h4>
              </v-col>
            </v-row>

            <!-- Lease or Land Ownership -->
            <v-row
              noGutters
              class="px-8 pt-1 key-value-pair"
            >
              <v-col
                cols="3"
                class="pt-1"
              >
                Lease or Land <br>Ownership
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
                <span v-html="landOwnershipLabel" />
              </v-col>
            </v-row>
            <!-- Land Details Corrections Row -->
            <v-row
              noGutters
              class="px-8"
            >
              <v-col>
                <UpdatedBadge
                  v-if="showUpdatedBadge"
                  class="mb-1"
                  :action="correctionState.action"
                  :baseline="correctionState.landDetails.baseline"
                  :currentState="correctionState.landDetails.currentState"
                />
              </v-col>
            </v-row>
          </template>
        </span>

        <!-- Tax Certificate -->
        <template v-if="isTransportPermitReview && showTaxCertificateExpiryDate">
          <v-divider class="mx-8 mt-7 mb-6" />
          <v-row
            noGutters
            class="px-8 key-value-pair"
          >
            <v-col cols="3">
              Tax Certificate <br>Expiry Date
            </v-col>
            <v-col cols="9">
              {{ convertDateToLongFormat(homeLocationInfo.taxExpiryDate) }}
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
  useExemptions,
  useInputRules,
  useMhrCorrections,
  useMhrInfoValidation,
  useMhrValidations,
  useTransportPermits,
useUpdatedBadges
} from '@/composables'
import { storeToRefs } from 'pinia'
import { useCountriesProvinces } from '@/composables/address/factories'
import { FormIF, MhrRegistrationHomeLocationIF } from '@/interfaces'
import { convertDateToLongFormat } from '@/utils/date-helper'
import { TransportPermitDetails } from '@/components/mhrTransportPermit'
import { InfoChip, UpdatedBadge } from '@/components/common'

export default defineComponent({
  name: 'HomeLocationReview',
  components: { TransportPermitDetails, UpdatedBadge, InfoChip },
  props: {
    hideDefaultHeader: {
      type: Boolean,
      default: false
    },
    hideSectionHeader: {
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
    },
    isPrevTransportPermitLocation: {
      type: Boolean,
      default: false
    },
    isCancelTransportPermitReview: {
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
      getMhrTransportPermitPreviousLocation,
      getMhrTransportPermitHomeLocation,
      isMhrReRegistration
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
      isMovingWithinSamePark,
      isCancelChangeLocationActive
    } = useTransportPermits()
    const { correctionState, isMhrCorrection } = useMhrCorrections()
    const { showUpdatedBadge } = useUpdatedBadges()
    const { isExemptionWithActiveTransportPermit, exemptionLabel } = useExemptions()

    const homeLocationInfo: MhrRegistrationHomeLocationIF =
      (props.isPrevTransportPermitLocation || props.isCancelTransportPermitReview)
        ? getMhrTransportPermitPreviousLocation.value
        : props.isTransportPermitReview
            ? getMhrTransportPermit.value.newLocation
            : getMhrRegistrationLocation.value

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
      isCancelledTransportPermitDetails: computed((): boolean =>
        isCancelChangeLocationActive.value && props.hideSectionHeader),

      includesPid: computed((): boolean => {
        return [HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE]
          .includes(homeLocationInfo.otherType)
      }),
      isManualLocation: computed((): boolean => {
        return props.isPrevTransportPermitLocation ? !homeLocationInfo.pidNumber : getIsManualLocation.value
      }),
      hasAddress: computed((): boolean => {
        return !!(homeLocationInfo.address?.street ||
        homeLocationInfo.address?.streetAdditional ||
        homeLocationInfo.address?.city)
      }),
      exemptionWithActivePermitText: computed((): string =>
        isExemptionWithActiveTransportPermit.value
          ? `The transport permit on this home will no longer be valid upon filing this ${exemptionLabel.value}`
          : ''
      ),
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
      isMhrManufacturerRegistration,
      convertDateToLongFormat,
      getMhrRegistrationLocation,
      ...countryProvincesHelpers,
      hasActiveTransportPermit,
      isNotManufacturersLot,
      isAmendLocationActive,
      isChangeLocationActive,
      isCancelChangeLocationActive,
      correctionState,
      isMhrCorrection,
      isMhrReRegistration,
      showUpdatedBadge,
      isExemptionWithActiveTransportPermit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.home-location-review {
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

.cancelled-location-info {
  opacity: 0.5;
}
</style>
