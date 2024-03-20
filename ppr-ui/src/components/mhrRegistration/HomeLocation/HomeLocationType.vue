<template>
  <v-card
    id="mhr-home-location-type"
    flat
    rounded
    class="mt-8 pa-8"
  >
    <v-row
      noGutters
      class="pt-1"
    >
      <v-col
        cols="12"
        sm="3"
      >
        <label
          class="generic-label"
          :class="{'error-text': validate && !isLocationTypeValid}"
        >Location Type</label>
        <UpdatedBadge
          v-if="updatedBadge"
          :action="updatedBadge.action"
          :baseline="updatedBadge.baseline"
          :currentState="updatedBadge.currentState"
          isCaseSensitive
        />
      </v-col>
      <v-col
        cols="12"
        sm="9"
        class="mt-n1"
      >
        <v-radio-group
          id="location-type--radio-options"
          v-model="locationTypeOption"
          class="mt-0 pr-1"
          :hideDetails="true"
          :disabled="isVerifyingPid"
        >
          <!-- Dealers / Manufacturers Lot -->
          <v-row noGutters>
            <v-col>
              <v-radio
                id="lot-option"
                class="home-type-radio"
                label="Dealer's / Manufacturer's lot"
                :value="HomeLocationTypes.LOT"
              />
              <v-expand-transition>
                <v-form
                  v-show="locationTypeOption === HomeLocationTypes.LOT"
                  ref="lotForm"
                  v-model="isValidLot"
                >
                  <v-text-field
                    v-model="dealerManufacturerLot"
                    variant="filled"
                    color="primary"
                    class="ml-8 pt-2"
                    label="Dealer / Manufacturer Name"
                    :rules="dealerManufacturerLotRules"
                  />
                </v-form>
              </v-expand-transition>
            </v-col>
          </v-row>

          <!-- Manufactured Home Park -->
          <v-row noGutters>
            <v-col class="pt-3">
              <v-radio
                id="home-park-option"
                class="home-type-radio"
                label="Manufactured home park (other than a strata park)"
                :value="HomeLocationTypes.HOME_PARK"
              />
              <v-expand-transition>
                <v-form
                  v-show="locationTypeOption === HomeLocationTypes.HOME_PARK"
                  ref="homeParkForm"
                  v-model="isValidHomePark"
                >
                  <v-text-field
                    v-model="homeParkName"
                    variant="filled"
                    color="primary"
                    class="ml-8 pt-2"
                    label="Park Name"
                    :rules="homeParkNameRules"
                  />

                  <v-text-field
                    v-model="homeParkPad"
                    variant="filled"
                    color="primary"
                    class="ml-8"
                    label="Pad"
                    :rules="homeParkPadRules"
                  />
                </v-form>
              </v-expand-transition>
            </v-col>
          </v-row>

          <!-- Other Land type -->
          <v-row noGutters>
            <v-col class="pt-3">
              <v-radio
                id="other-option"
                class="home-type-radio"
                label="Other land"
                :value="HomeLocationTypes.OTHER_LAND"
              />
              <v-expand-transition>
                <v-radio-group
                  v-if="locationTypeOption === HomeLocationTypes.OTHER_LAND"
                  id="location-type--radio-options"
                  v-model="otherTypeOption"
                  class="mt-0 ml-10"
                  hideDetails="true"
                >
                  <v-radio
                    id="reserve-option"
                    class="home-type-radio"
                    label="Indian Reserve"
                    :value="HomeLocationTypes.OTHER_RESERVE"
                  />
                  <!-- Other Reserve  -->
                  <v-expand-transition>
                    <div
                      v-if="otherTypeOption === HomeLocationTypes.OTHER_RESERVE"
                      class="ml-8"
                    >
                      <HomeLocationDescription
                        :locationDescription="locationTypeInfo"
                        :isReserve="true"
                        :validate="validate"
                        :legalDescription="legalDescription"
                        @set-is-valid-location-info="isValidLocationInfo = $event"
                        @set-show-location-info="showLocationInfo = $event"
                        @set-location-info="locationInfo = $event"
                        @set-additional-description="additionalDescription = $event"
                      />
                    </div>
                  </v-expand-transition>

                  <v-radio
                    id="strata-option"
                    class="home-type-radio"
                    label="Strata"
                    :value="HomeLocationTypes.OTHER_STRATA"
                  />

                  <!-- Other Strata  -->
                  <v-expand-transition>
                    <div
                      v-if="otherTypeOption === HomeLocationTypes.OTHER_STRATA"
                      class="ml-8"
                    >
                      <PidNumber
                        class="mb-4"
                        :pidNumber="locationTypeInfo.pidNumber"
                        :disable="showLocationInfo"
                        :required="otherTypeOption === HomeLocationTypes.OTHER_STRATA && validate"
                        @set-pid="handlePidInfo($event)"
                        @verifying-pid="isVerifyingPid = $event"
                      />

                      <HomeLocationDescription
                        :locationDescription="locationTypeInfo"
                        :isStrata="true"
                        :validate="validate"
                        :legalDescription="legalDescription"
                        @set-is-valid-location-info="isValidLocationInfo = $event"
                        @set-show-location-info="showLocationInfo = $event"
                        @set-location-info="locationInfo = $event"
                        @set-additional-description="additionalDescription = $event"
                      />
                    </div>
                  </v-expand-transition>

                  <v-radio
                    id="other-land-option"
                    class="home-type-radio"
                    label="Other"
                    :value="HomeLocationTypes.OTHER_TYPE"
                  />

                  <!-- Other Type -->
                  <v-expand-transition>
                    <div
                      v-if="otherTypeOption === HomeLocationTypes.OTHER_TYPE"
                      class="ml-8"
                    >
                      <PidNumber
                        class="mb-4"
                        :pidNumber="locationTypeInfo.pidNumber"
                        :disable="showLocationInfo"
                        :required="otherTypeOption === HomeLocationTypes.OTHER_TYPE && validate"
                        @set-pid="handlePidInfo($event)"
                        @verifying-pid="isVerifyingPid = $event"
                      />

                      <HomeLocationDescription
                        :locationDescription="locationTypeInfo"
                        :validate="validate"
                        :legalDescription="legalDescription"
                        @set-is-valid-location-info="isValidLocationInfo = $event"
                        @set-show-location-info="showLocationInfo = $event"
                        @set-location-info="locationInfo = $event"
                        @set-additional-description="additionalDescription = $event"
                      />
                    </div>
                  </v-expand-transition>
                </v-radio-group>
              </v-expand-transition>
            </v-col>
          </v-row>
        </v-radio-group>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { HomeLocationTypes } from '@/enums'
import { PidNumber, UpdatedBadge } from '@/components/common'
import HomeLocationDescription from './HomeLocationDescription.vue'
import { useInputRules, useNewMhrRegistration } from '@/composables'
import { FormIF, MhrLocationInfoIF, MhrRegistrationHomeLocationIF, UpdatedBadgeIF } from '@/interfaces'
import { PidInfoIF } from '@/interfaces/ltsa-api-interfaces'

export default defineComponent({
  name: 'HomeLocationType',
  components: {
    HomeLocationDescription,
    PidNumber,
    UpdatedBadge
  },
  props: {
    locationTypeInfo: {
      type: Object as () => MhrRegistrationHomeLocationIF,
      default: {
        parkName: '',
        pad: '',
        address: {
          street: '',
          streetAdditional: '',
          city: '',
          region: null,
          country: null,
          postalCode: ''
        },
        leaveProvince: false,
        pidNumber: '',
        taxCertificate: false,
        taxExpiryDate: '',
        dealerName: '',
        additionalDescription: '',
        locationType: null,
        otherType: null,
        legalDescription: '',
        lot: '',
        parcel: '',
        block: '',
        districtLot: '',
        partOf: '',
        section: '',
        township: '',
        range: '',
        meridian: '',
        landDistrict: '',
        plan: '',
        bandName: '',
        reserveNumber: '',
        exceptionPlan: ''
      } as MhrRegistrationHomeLocationIF
    },
    validate: {
      type: Boolean,
      default: false
    },
    updatedBadge: {
      type: Object as () => UpdatedBadgeIF,
      default: () => null
    }
  },
  emits: ['setStoreProperty', 'isValid'],
  setup (props, { emit }) {
    const {
      // Actions
      setIsManualLocation
    } = useStore()
    const { resetLocationInfoFields } = useNewMhrRegistration()
    const { customRules, maxLength, required } = useInputRules()
    const lotForm = ref(null) as FormIF
    const homeParkForm = ref(null) as FormIF

    // Home location store properties
    // Developer note: de-construction of store computed properties in this manner will result in the loss of reactivity
    const { additionalDescription, dealerName, legalDescription, locationType, pad, pidNumber, parkName, otherType } =
      props.locationTypeInfo

    const localState = reactive({
      isValidLot: false,
      isValidHomePark: false,
      isVerifyingPid: false,
      isValidLocationInfo: false,
      locationTypeOption: locationType || HomeLocationTypes,
      otherTypeOption: otherType || HomeLocationTypes,
      dealerManufacturerLot: dealerName || '',
      homeParkName: parkName || '',
      homeParkPad: pad || '',
      pidNumber: pidNumber || '',
      showLocationInfo: false,
      locationInfo: {},
      legalDescription: legalDescription || '',
      additionalDescription: additionalDescription || '',
      dealerManufacturerLotRules: computed(() =>
        customRules(required('Enter a dealer or manufacturer name'), maxLength(60))
      ),
      homeParkNameRules: computed(() =>
        customRules(required('Enter a park name'), maxLength(40))
      ),
      homeParkPadRules: computed(() =>
        customRules(required('Enter a pad'), maxLength(6))
      ),
      isLocationTypeValid: computed((): boolean => {
        // Return false if there is no radio selection
        if (!localState.locationTypeOption) return false

        switch (localState.locationTypeOption as any) {
          case HomeLocationTypes.LOT:
            return localState.isValidLot
          case HomeLocationTypes.HOME_PARK:
            return localState.isValidHomePark
          case HomeLocationTypes.OTHER_LAND:
            switch (localState.otherTypeOption as any) {
              case HomeLocationTypes.OTHER_RESERVE:
                return localState.isValidLocationInfo
              case HomeLocationTypes.OTHER_STRATA:
              case HomeLocationTypes.OTHER_TYPE:
                return (localState.showLocationInfo && localState.isValidLocationInfo) ||
                  (!!localState.pidNumber && !!localState.legalDescription && localState.isValidLocationInfo)
              default:
                return false
            }
          default:
            return false
        }
      })
    })

    const handlePidInfo = (pidInfo: PidInfoIF): void => {
      localState.pidNumber = pidInfo.pidNumber
      localState.legalDescription = pidInfo.legalDescription
    }

    const validateForms = () => {
      if (props.validate) {
        lotForm.value?.validate()
        homeParkForm.value?.validate()
      }
    }

    const resetFormValidations = () => {
      if (!props.validate) {
        lotForm.value?.resetValidation()
        homeParkForm.value?.resetValidation()
      }
    }

    /** Apply local models to store when they change. **/
    watch(() => localState.dealerManufacturerLot, () => {
      emit('setStoreProperty', { key: 'dealerName', value: localState.dealerManufacturerLot })
    })
    watch(() => localState.homeParkName, () => {
      emit('setStoreProperty', { key: 'parkName', value: localState.homeParkName })
    })
    watch(() => localState.homeParkPad, () => {
      emit('setStoreProperty', { key: 'pad', value: localState.homeParkPad })
    })
    watch(() => localState.pidNumber, () => {
      emit('setStoreProperty', { key: 'pidNumber', value: localState.pidNumber })
      emit('setStoreProperty', { key: 'legalDescription', value: localState.legalDescription })
    })
    watch(() => localState.locationInfo, (val: MhrLocationInfoIF) => {
      for (const [key, value] of Object.entries(val)) {
        emit('setStoreProperty', { key, value })
      }
    }, { deep: true })
    watch(() => localState.additionalDescription, () => {
      emit('setStoreProperty', { key: 'additionalDescription', value: localState.additionalDescription })
    })
    watch(() => localState.locationTypeOption, () => {
      emit('setStoreProperty', { key: 'locationType', value: localState.locationTypeOption })
    })
    watch(() => localState.otherTypeOption, () => {
      emit('setStoreProperty', { key: 'otherType', value: localState.otherTypeOption })
    })
    watch(() => localState.isLocationTypeValid, (val: boolean) => {
      emit('isValid', val)
    })
    watch(() => props.validate, async () => {
      validateForms()
    })

    /** Clear/reset forms when select option changes. **/
    watch(() => localState.locationTypeOption, async () => {
      resetFormValidations()
      localState.homeParkName = ''
      localState.homeParkPad = ''
      localState.pidNumber = ''
      localState.otherTypeOption = null
      localState.dealerManufacturerLot = ''
      localState.toggleInfoForm = false
      setIsManualLocation(false)
      localState.legalDescription = ''
      localState.locationInfo = resetLocationInfoFields(localState.locationInfo)

      // Await data propagation before validation
      await nextTick()
      validateForms()
    })
    watch(() => localState.otherTypeOption, () => {
      localState.pidNumber = ''
      localState.legalDescription = ''
      localState.additionalDescription = ''
      localState.showLocationInfo = false
      localState.toggleInfoForm = false
      setIsManualLocation(false)
      localState.legalDescription = ''
      localState.locationInfo = resetLocationInfoFields(localState.locationInfo)
    })

    return {
      lotForm,
      homeParkForm,
      handlePidInfo,
      HomeLocationTypes,
      customRules,
      required,
      maxLength,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

:deep(.v-text-field > .v-input__control > .v-input__slot) {
  background-color: $gray1;
}
:deep(.v-icon.mdi-close) {
  padding-left: 2px;
  font-size: 20px;
}

</style>
