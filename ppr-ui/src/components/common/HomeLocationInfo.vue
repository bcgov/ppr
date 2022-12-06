<template>
  <v-card flat rounded id="home-location-info">
    <v-form ref="homeLocationInfoRef" v-model="homeLocationInfoValid">

      <template v-if="isReserve">
        <v-row no-gutters class="pt-5">
          <v-col cols="8" class="pr-1">
            <v-text-field
              filled
              id="band-name"
              label="Band Name"
              v-model="locationInfo.bandName"
              :rules="locationInputRules(null, 'Enter a Band Name', 'band-name')"
            />
          </v-col>
          <v-col cols="4" class="pl-2">
            <v-text-field
              filled
              id="reserve-number"
              label="Reserve Number"
              v-model="locationInfo.reserveNumber"
              :rules="locationInputRules(null,  'Enter a Reserve Number', 'reserve-number')"
            />
          </v-col>
          <v-col>
            <v-text-field
              filled
              id="reserve-additional-description"
              label="Additional Description"
              v-model="additionalDescription"
              hint="Example: PIN number"
              :error="isReserveLengthErr"
              :errorMessages="isReserveLengthErr ? reserveLengthErrMsg : ''"
              persistent-hint
            />
          </v-col>
        </v-row>
        <v-divider class="mt-3 mb-5 mx-0"/>
      </template>

      <v-row no-gutters class="pt-4">
        <v-col>
          <v-text-field
            filled
            id="lot"
            :label="isStrata ? 'Strata Lot' : 'Lot'"
            v-model="locationInfo.lot"
            :rules="locationInputRules(10, 'Enter a lot number', 'lot')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            filled
            id="land-district"
            label="Land District"
            v-model="locationInfo.landDistrict"
            :rules="locationInputRules(20, 'Enter a land district', 'land-district')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            filled
            id="plan"
            :label="isStrata ? 'Strata Plan' : 'Plan'"
            v-model="locationInfo.plan"
            :rules="locationInputRules(12, 'Enter a plan number', 'plan')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="4" class="pr-2">
          <v-text-field
            filled
            id="district-lot"
            label="District Lot"
            v-model="locationInfo.districtLot"
            :rules="locationInputRules(17, 'Enter a district lot', 'district-lot')"
            persistent-hint
          />
        </v-col>

        <v-col cols="4" class="px-1">
          <v-text-field
            filled
            id="part-of"
            label="Part Of"
            v-model="locationInfo.partOf"
            :rules="maxLength(10)"
            persistent-hint
          />
        </v-col>

        <v-col cols="4" class="pl-2">
          <v-text-field
            filled
            id="section"
            label="Section"
            v-model="locationInfo.section"
            :rules="maxLength(10)"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="4" class="pr-2">
          <v-text-field
            filled
            id="township"
            label="Township"
            v-model="locationInfo.township"
            :rules="maxLength(2)"
            persistent-hint
          />
        </v-col>

        <v-col cols="4" class="px-1">
          <v-text-field
            filled
            id="Range"
            label="Range"
            v-model="locationInfo.range"
            :rules="maxLength(2)"
            persistent-hint
          />
        </v-col>

        <v-col cols="4" class="pl-2">
          <v-text-field
            filled
            id="meridian"
            label="Meridian"
            v-model="locationInfo.meridian"
            :rules="maxLength(3)"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="6" class="pr-2">
          <v-text-field
            filled
            id="parcel"
            label="Parcel"
            v-model="locationInfo.parcel"
            :rules="locationInputRules(10, 'Enter a parcel block')"
            persistent-hint
          />
        </v-col>

        <v-col cols="6" class="pl-2">
          <v-text-field
            filled
            id="block"
            label="Block"
            v-model="locationInfo.block"
            :rules="locationInputRules(10, 'Enter a block')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="12">
          <v-textarea
            filled
            id="exceptPlan"
            label="Except Plan"
            height="100"
            v-model="locationInfo.exceptPlan"
            :rules="maxLength(80)"
            persistent-hint
          />
        </v-col>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { MhrLocationInfoIF } from '@/interfaces'
import { useInputRules } from '@/composables/useInputRules'
/* eslint-disable no-unused-vars */

export default defineComponent({
  name: 'HomeLocationInfo',
  emits: ['updateLocationInfo', 'updateLocationDescription', 'updateLocationValid'],
  props: {
    validate: { type: Boolean, default: false },
    isReserve: { type: Boolean, default: false },
    isStrata: { type: Boolean, default: false }
  },
  setup (props, context) {
    const {
      customRules,
      maxLength,
      required
    } = useInputRules()

    const localState = reactive({
      homeLocationInfoValid: false,
      locationInfo: {
        bandName: '',
        reserveNumber: '',
        lot: '',
        landDistrict: '',
        plan: '',
        districtLot: '',
        partOf: '',
        section: '',
        township: '',
        range: '',
        meridian: '',
        parcel: '',
        block: '',
        exceptPlan: ''
      } as MhrLocationInfoIF,
      additionalDescription: '',
      reserveLengthErrMsg: 'Band Name, Reserve Number and Details combined cannot exceed 80 characters',
      isReserveLengthErr: computed((): boolean => {
        return (
          localState.locationInfo?.bandName + localState.locationInfo?.reserveNumber + localState.additionalDescription
        ).length > 80
      })
    })

    onMounted(() => {
      if (props.validate) validateLocationInfo()
    })

    const locationInputRules = (length: number = null, requiredMsg: string, fieldId: string = null) => {
      let requiredFields
      switch (true) {
        case props.isStrata:
          requiredFields = ['lot', 'land-district', 'plan']
          break
        case props.isReserve:
          requiredFields = ['band-name', 'reserve-number']
          break
        default:
          requiredFields = (localState.locationInfo.districtLot || localState.locationInfo.landDistrict) &&
            (!localState.locationInfo.lot && !localState.locationInfo.plan)
            ? ['land-district', 'district-lot']
            : ['lot', 'land-district', 'plan']
      }

      return customRules(
        length ? maxLength(length) : [],
        requiredFields.includes(fieldId) ? required(requiredMsg) : []
      )
    }

    const validateLocationInfo = (): void => {
      // @ts-ignore - function exists
      context.refs.homeLocationInfoRef.validate()
    }

    /** Prompt local validations on validate event. **/
    watch(() => props.validate, (val) => {
      if (val) validateLocationInfo()
    })

    /** Emit local model to parent when it changes. **/
    watch(() => localState.locationInfo, (locationInfo: MhrLocationInfoIF) => {
      context.emit('updateLocationInfo', locationInfo)
    }, { deep: true })

    /** Emit validation state to parent when it changes. **/
    watch(() => localState.additionalDescription, (description: string) => {
      context.emit('updateLocationDescription', description)
    })

    /** Emit validation state to parent when it changes. **/
    watch(() => localState.homeLocationInfoValid, (isValid: boolean) => {
      context.emit('updateLocationInfoValid', isValid)
    })

    return {
      maxLength,
      locationInputRules,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
