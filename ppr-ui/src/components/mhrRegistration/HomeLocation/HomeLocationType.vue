<template>
  <v-card flat rounded id="mhr-home-location-type" class="mt-8 pa-8">
    <v-row no-gutters class="pt-1">
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': validate}">Location Type</label>
      </v-col>
      <v-col cols="12" sm="10" class="mt-n1">
        <v-radio-group
          id="location-type--radio-options"
          v-model="locationTypeOption"
          class="mt-0 pr-1"
          hide-details="true"
          :disabled="isVerifyingPid"
        >
          <!-- Dealers / Manufacturers Lot -->
          <v-row no-gutters>
            <v-col>
              <v-radio
                id="lot-option"
                class="home-type-radio"
                label="Dealer's / Manufacturer's lot"
                active-class="selected-radio"
                :value="HomeLocationTypes.LOT"
              />
              <v-expand-transition>
                <v-form
                  v-show="locationTypeOption === HomeLocationTypes.LOT"
                  ref="lotForm"
                  v-model="isValidLot"
                >
                  <v-text-field
                    filled
                    class="ml-8 pt-2"
                    label="Dealer / Manufacturer Name"
                    v-model="dealerManufacturerLot"
                    :rules="dealerManufacturerLotRules"
                  />
                </v-form>
              </v-expand-transition>
            </v-col>
          </v-row>

          <!-- Manufactured Home Park -->
          <v-row no-gutters>
            <v-col class="pt-3">
              <v-radio
                id="home-park-option"
                class="home-type-radio"
                label="Manufactured home park (other than a strata park)"
                active-class="selected-radio"
                :value="HomeLocationTypes.HOME_PARK"
              />
              <v-expand-transition>
                <v-form
                  v-show="locationTypeOption === HomeLocationTypes.HOME_PARK"
                  ref="homeParkForm"
                  v-model="isValidHomePark"
                >
                  <v-text-field
                    filled
                    class="ml-8 pt-2"
                    label="Park Name"
                    v-model="homeParkName"
                    :rules="homeParkNameRules"
                  />

                  <v-text-field
                    filled
                    class="ml-8"
                    label="Pad"
                    v-model="homeParkPad"
                    :rules="homeParkPadRules"
                  />
                </v-form>
              </v-expand-transition>
            </v-col>
          </v-row>

          <!-- Other Land type -->
          <v-row no-gutters>
            <v-col class="pt-3">
              <v-radio
                id="other-option"
                class="home-type-radio"
                label="Other land"
                active-class="selected-radio"
                :value="HomeLocationTypes.OTHER_LAND"
              />
              <v-expand-transition>
                <v-radio-group
                  v-if="locationTypeOption === HomeLocationTypes.OTHER_LAND"
                  id="location-type--radio-options"
                  v-model="otherTypeOption"
                  class="mt-0 ml-10"
                  hide-details="true"
                >
                  <v-radio
                    id="reserve-option"
                    class="home-type-radio"
                    label="Indian Reserve"
                    active-class="selected-radio"
                    :value="HomeLocationTypes.OTHER_RESERVE"
                  />
                  <!-- Other Reserve  -->
                  <v-expand-transition>

                    <div v-if="otherTypeOption === HomeLocationTypes.OTHER_RESERVE" class="ml-8">

                      <HomeLocationDescription
                        isReserve
                        :validate="validate"
                        :legalDescription="legalDescription"
                        @setIsValidLocationInfo="isValidLocationInfo = $event"
                        @setShowLocationInfo="showLocationInfo = $event"
                        @setLocationInfo="locationInfo = $event"
                        @setAdditionalDescription="additionalDescription = $event"
                      />
                    </div>

                  </v-expand-transition>

                  <v-radio
                    id="strata-option"
                    class="home-type-radio"
                    label="Strata"
                    active-class="selected-radio"
                    :value="HomeLocationTypes.OTHER_STRATA"
                  />

                  <!-- Other Strata  -->
                  <v-expand-transition>

                    <div v-if="otherTypeOption === HomeLocationTypes.OTHER_STRATA" class="ml-8">

                      <PidNumber
                        class="mb-4"
                        :disable="showLocationInfo"
                        @setPid="handlePidInfo($event)"
                        @verifyingPid="isVerifyingPid = $event"
                        :required="otherTypeOption === HomeLocationTypes.OTHER_STRATA && validate"
                      />

                      <HomeLocationDescription
                        isStrata
                        :validate="validate"
                        :legalDescription="legalDescription"
                        @setIsValidLocationInfo="isValidLocationInfo = $event"
                        @setShowLocationInfo="showLocationInfo = $event"
                        @setLocationInfo="locationInfo = $event"
                        @setAdditionalDescription="additionalDescription = $event"
                      />
                    </div>

                  </v-expand-transition>

                  <v-radio
                    id="other-land-option"
                    class="home-type-radio"
                    label="Other"
                    active-class="selected-radio"
                    :value="HomeLocationTypes.OTHER_TYPE"
                  />

                  <!-- Other Type -->
                  <v-expand-transition>

                    <div v-if="otherTypeOption === HomeLocationTypes.OTHER_TYPE" class="ml-8">
                      <PidNumber
                        class="mb-4"
                        :disable="showLocationInfo"
                        @setPid="handlePidInfo($event)"
                        @verifyingPid="isVerifyingPid = $event"
                        :required="otherTypeOption === HomeLocationTypes.OTHER_TYPE && validate"
                      />

                      <HomeLocationDescription
                        :validate="validate"
                        :legalDescription="legalDescription"
                        @setIsValidLocationInfo="isValidLocationInfo = $event"
                        @setShowLocationInfo="showLocationInfo = $event"
                        @setLocationInfo="locationInfo = $event"
                        @setAdditionalDescription="additionalDescription = $event"
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
/* eslint-disable no-unused-vars */
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { HomeLocationTypes } from '@/enums'
import { HomeLocationInfo, PidNumber } from '@/components/common'
import HomeLocationDescription from './HomeLocationDescription.vue'
import { useInputRules, useMhrValidations, useNewMhrRegistration } from '@/composables'
import { MhrLocationInfoIF } from '@/interfaces'
import { PidInfoIF } from '@/interfaces/ltsa-api-interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeLocationType',
  components: {
    HomeLocationDescription,
    HomeLocationInfo,
    PidNumber
  },
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const {
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getMhrRegistrationValidationModel'
    ])
    const {
      setMhrLocation,
      setIsManualLocation
    } = useActions<any>([
      'setMhrLocation',
      'setIsManualLocation'
    ])

    const { resetLocationInfoFields } = useNewMhrRegistration()
    const { customRules, maxLength, required } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      isValidLot: false,
      isValidHomePark: false,
      isVerifyingPid: false,
      isValidLocationInfo: false,
      locationTypeOption: HomeLocationTypes,
      otherTypeOption: HomeLocationTypes,
      dealerManufacturerLot: '',
      homeParkName: '',
      homeParkPad: '',
      pidNumber: '',
      showLocationInfo: false,
      locationInfo: {},
      legalDescription: '',
      additionalDescription: '',
      dealerManufacturerLotRules: computed(() => {
        return localState.locationTypeOption as any === HomeLocationTypes.LOT
          ? customRules(required('Enter a dealer or manufacturer name'), maxLength(60))
          : []
      }),
      homeParkNameRules: computed(() => {
        return localState.locationTypeOption as any === HomeLocationTypes.HOME_PARK
          ? customRules(required('Enter a park name'), maxLength(40))
          : []
      }),
      homeParkPadRules: computed(() => {
        return localState.locationTypeOption as any === HomeLocationTypes.HOME_PARK
          ? customRules(required('Enter a pad'), maxLength(6))
          : []
      }),
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
        }
      })
    })

    const handlePidInfo = (pidInfo: PidInfoIF): void => {
      localState.pidNumber = pidInfo.pidNumber
      localState.legalDescription = pidInfo.legalDescription
    }

    const validateForms = async () => {
      if (props.validate) {
        // @ts-ignore - function exists
        await context.refs.lotForm?.validate()
        // @ts-ignore - function exists
        await context.refs.homeParkForm?.validate()
      }
    }

    /** Apply local models to store when they change. **/
    watch(() => localState.dealerManufacturerLot, () => {
      setMhrLocation({ key: 'dealerName', value: localState.dealerManufacturerLot })
    })
    watch(() => localState.homeParkName, () => {
      setMhrLocation({ key: 'parkName', value: localState.homeParkName })
    })
    watch(() => localState.homeParkPad, () => {
      setMhrLocation({ key: 'pad', value: localState.homeParkPad })
    })
    watch(() => localState.pidNumber, () => {
      setMhrLocation({ key: 'pidNumber', value: localState.pidNumber })
      setMhrLocation({ key: 'legalDescription', value: localState.legalDescription })
    })
    watch(() => localState.locationInfo, (val: MhrLocationInfoIF) => {
      for (const [key, value] of Object.entries(val)) {
        setMhrLocation({ key: key, value: value })
      }
    }, { deep: true })
    watch(() => localState.additionalDescription, () => {
      setMhrLocation({ key: 'additionalDescription', value: localState.additionalDescription })
    })
    watch(() => localState.locationTypeOption, () => {
      setMhrLocation({ key: 'locationType', value: localState.locationTypeOption })
    })
    watch(() => localState.otherTypeOption, () => {
      setMhrLocation({ key: 'otherType', value: localState.otherTypeOption })
    })
    watch(() => localState.isLocationTypeValid, (val: boolean) => {
      setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LOCATION_TYPE_VALID, val)
    })
    watch(() => props.validate, async (val: boolean) => {
      await validateForms()
    })

    /** Clear/reset forms when select option changes. **/
    watch(() => localState.locationTypeOption, () => {
      localState.homeParkName = ''
      localState.homeParkPad = ''
      localState.pidNumber = ''
      localState.otherTypeOption = null
      localState.dealerManufacturerLot = ''
      localState.toggleInfoForm = false
      setIsManualLocation(false)
      localState.locationInfo = resetLocationInfoFields(localState.locationInfo)
      validateForms()
    })
    watch(() => localState.otherTypeOption, () => {
      localState.pidNumber = ''
      localState.legalDescription = ''
      localState.additionalDescription = ''
      localState.showLocationInfo = false
      localState.toggleInfoForm = false
      setIsManualLocation(false)
      localState.locationInfo = resetLocationInfoFields(localState.locationInfo)
    })
    watch(() => localState.validate, () => {
      validateForms()
    })

    return {
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
::v-deep {
  .v-text-field > .v-input__control > .v-input__slot {
    background-color: $gray1;
  }
  .v-icon.mdi-close {
    padding-left: 2px;
    font-size: 20px;
  }
}
</style>
