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
                    label="Pad (Optional)"
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
                  <v-radio
                    id="strata-option"
                    class="home-type-radio"
                    label="Strata"
                    active-class="selected-radio"
                    :value="HomeLocationTypes.OTHER_STRATA"
                  />

                  <!-- Pid Number Input -->
                  <v-expand-transition>
                    <PidNumber
                      v-if="otherTypeOption === HomeLocationTypes.OTHER_STRATA"
                      class="ml-8 mb-4"
                      @setPid="pidNumber = $event"
                      @verifyingPid="isVerifyingPid = $event"
                    />
                  </v-expand-transition>

                  <v-radio
                    id="other-land-option"
                    class="home-type-radio"
                    label="Other"
                    active-class="selected-radio"
                    :value="HomeLocationTypes.OTHER_TYPE"
                  />

                  <!-- Pid Number Input -->
                  <v-expand-transition>
                    <PidNumber
                      v-if="otherTypeOption === HomeLocationTypes.OTHER_TYPE"
                      class="ml-8"
                      @setPid="pidNumber = $event"
                      @verifyingPid="isVerifyingPid = $event"
                    />
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
import { PidNumber } from '@/components/common'
import { useInputRules, useMhrValidations } from '@/composables'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeLocationType',
  components: {
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
      setMhrLocation
    } = useActions<any>([
      'setMhrLocation'
    ])

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
      locationTypeOption: HomeLocationTypes,
      otherTypeOption: HomeLocationTypes,
      dealerManufacturerLot: '',
      homeParkName: '',
      homeParkPad: '',
      pidNumber: '',
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
          ? maxLength(6)
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
        }
      })
    })

    const validateForms = (): void => {
      if (props.validate) {
        // @ts-ignore - function exists
        if (props.validate) context.refs.lotForm.validate()
        // @ts-ignore - function exists
        if (props.validate) context.refs.homeParkForm.validate()
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

    /** Clear/reset forms when select option changes. **/
    watch(() => localState.locationTypeOption, () => {
      switch (localState.locationTypeOption as any) {
        case HomeLocationTypes.LOT:
          localState.homeParkName = ''
          localState.homeParkPad = ''
          localState.pidNumber = ''
          localState.otherTypeOption = null
          break
        case HomeLocationTypes.HOME_PARK:
          localState.dealerManufacturerLot = ''
          localState.pidNumber = ''
          localState.otherTypeOption = null
          break
        case HomeLocationTypes.OTHER_LAND:
          localState.homeParkName = ''
          localState.homeParkPad = ''
          localState.dealerManufacturerLot = ''
          break
      }
      validateForms()
    })
    watch(() => localState.otherTypeOption, () => {
      localState.pidNumber = ''
    })
    watch(() => localState.validate, () => {
      validateForms()
    })

    return {
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
</style>
