<template>
  <v-card
    id="home-location-info"
    flat
    rounded
  >
    <v-form
      ref="homeLocationInfoRef"
      v-model="homeLocationInfoValid"
    >
      <template v-if="isReserve">
        <v-row
          no-gutters
          class="pt-5"
        >
          <v-col
            cols="8"
            class="pr-1"
          >
            <v-text-field
              id="band-name"
              v-model="locationInfo.bandName"
              variant="filled"
              color="primary"
              label="Band Name"
              :rules="locationInputRules(null, 'Enter a band name', 'band-name')"
            />
          </v-col>
          <v-col
            cols="4"
            class="pl-2"
          >
            <v-text-field
              id="reserve-number"
              v-model="locationInfo.reserveNumber"
              variant="filled"
              color="primary"
              label="Reserve Number"
              :rules="locationInputRules(null, 'Enter a reserve number', 'reserve-number')"
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
              id="reserve-additional-description"
              v-model="additionalDescription"
              variant="filled"
              color="primary"
              label="Additional Description"
              hint="Example: PIN number"
              :error="isReserveLengthErr"
              :error-messages="isReserveLengthErr ? reserveLengthErrMsg : ''"
              persistent-hint
            />
          </v-col>
        </v-row>
        <v-divider class="mt-3 mb-5 mx-0" />
      </template>

      <v-row
        no-gutters
        class="pt-4"
      >
        <v-col>
          <v-text-field
            id="lot"
            v-model="locationInfo.lot"
            variant="filled"
            color="primary"
            :label="isStrata ? 'Strata Lot' : 'Lot'"
            :rules="locationInputRules(10, 'Enter a lot number', 'lot')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            id="land-district"
            v-model="locationInfo.landDistrict"
            variant="filled"
            color="primary"
            label="Land District"
            :rules="locationInputRules(20, 'Enter a land district', 'land-district')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            id="plan"
            v-model="locationInfo.plan"
            variant="filled"
            color="primary"
            :label="isStrata ? 'Strata Plan' : 'Plan'"
            :rules="locationInputRules(12, 'Enter a plan number', 'plan')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col
          cols="4"
          class="pr-2"
        >
          <v-text-field
            id="district-lot"
            v-model="locationInfo.districtLot"
            variant="filled"
            color="primary"
            label="District Lot"
            :rules="locationInputRules(17, 'Enter a district lot', 'district-lot')"
            persistent-hint
          />
        </v-col>

        <v-col
          cols="4"
          class="px-1"
        >
          <v-text-field
            id="part-of"
            v-model="locationInfo.partOf"
            variant="filled"
            color="primary"
            label="Part Of"
            :rules="maxLength(10)"
            persistent-hint
          />
        </v-col>

        <v-col
          cols="4"
          class="pl-2"
        >
          <v-text-field
            id="section"
            v-model="locationInfo.section"
            variant="filled"
            color="primary"
            label="Section"
            :rules="maxLength(10)"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col
          cols="4"
          class="pr-2"
        >
          <v-text-field
            id="township"
            v-model="locationInfo.township"
            variant="filled"
            color="primary"
            label="Township"
            :rules="maxLength(2)"
            persistent-hint
          />
        </v-col>

        <v-col
          cols="4"
          class="px-1"
        >
          <v-text-field
            id="Range"
            v-model="locationInfo.range"
            variant="filled"
            color="primary"
            label="Range"
            :rules="maxLength(2)"
            persistent-hint
          />
        </v-col>

        <v-col
          cols="4"
          class="pl-2"
        >
          <v-text-field
            id="meridian"
            v-model="locationInfo.meridian"
            variant="filled"
            color="primary"
            label="Meridian"
            :rules="maxLength(3)"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col
          cols="6"
          class="pr-2"
        >
          <v-text-field
            id="parcel"
            v-model="locationInfo.parcel"
            variant="filled"
            color="primary"
            label="Parcel"
            :rules="locationInputRules(10, 'Enter a parcel block')"
            persistent-hint
          />
        </v-col>

        <v-col
          cols="6"
          class="pl-2"
        >
          <v-text-field
            id="block"
            v-model="locationInfo.block"
            variant="filled"
            color="primary"
            label="Block"
            :rules="locationInputRules(10, 'Enter a block')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="12">
          <v-textarea
            id="exceptionPlan"
            v-model="locationInfo.exceptionPlan"
            variant="filled"
            color="primary"
            label="Except Plan"
            :rules="maxLength(80)"
            persistent-hint
          />
        </v-col>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">

import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from 'vue'
import type { FormIF, MhrLocationInfoIF, MhrRegistrationHomeLocationIF } from '@/interfaces'
import { useInputRules } from '@/composables/useInputRules'

export default defineComponent({
  name: 'HomeLocationInfo',
  props: {
    homeLocationInfo: {
      type: Object as () => MhrRegistrationHomeLocationIF,
      default: () => {}
    },
    validate: { type: Boolean, default: false },
    isReserve: { type: Boolean, default: false },
    isStrata: { type: Boolean, default: false }
  },
  emits: ['updateLocationInfo', 'updateLocationDescription', 'updateLocationInfoValid'],
  setup (props, context) {
    const {
      customRules,
      maxLength,
      required
    } = useInputRules()
    const homeLocationInfoRef = ref(null) as FormIF

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
        exceptionPlan: ''
      } as MhrLocationInfoIF,
      additionalDescription: props.homeLocationInfo?.additionalDescription || '',
      reserveLengthErrMsg: 'Band Name, Reserve Number and Details combined cannot exceed 80 characters',
      isReserveLengthErr: computed((): boolean => {
        return (
          localState.locationInfo?.bandName + localState.locationInfo?.reserveNumber + localState.additionalDescription
        ).length > 80
      }),
      isValidOtherType: computed((): boolean => {
        return localState.homeLocationInfoValid && (
          (!!localState.locationInfo.lot && !!localState.locationInfo.landDistrict && !!localState.locationInfo.plan) ||
          (!!localState.locationInfo.landDistrict && !!localState.locationInfo.districtLot)
        )
      })
    })

    onMounted(() => {
      if (props.validate) validateLocationInfo()
      // Map specific local properties to draft data if it exists
      for (const key in localState.locationInfo) localState.locationInfo[key] = props.homeLocationInfo[key]
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
          requiredFields = []
      }

      return customRules(
        length ? maxLength(length) : [],
        requiredFields.includes(fieldId) ? required(requiredMsg) : []
      )
    }

    const validateLocationInfo = (): void => {
      homeLocationInfoRef.value?.validate()
    }

    const emitOtherTypeValid = (): void => {
      if (!props.isStrata && !props.isReserve) {
        context.emit('updateLocationInfoValid', localState.isValidOtherType)
      }
    }

    /** Prompt local validations on validate event. **/
    watch(() => props.validate, (val) => {
      if (val) validateLocationInfo()
    })

    /** Emit local model to parent when it changes. **/
    watch(() => localState.locationInfo, (locationInfo: MhrLocationInfoIF) => {
      context.emit('updateLocationInfo', locationInfo)
      emitOtherTypeValid()
    }, { deep: true })

    /** Emit validation state to parent when it changes. **/
    watch(() => localState.additionalDescription, (description: string) => {
      context.emit('updateLocationDescription', description)
    })

    /** Emit validation state to parent when it changes. **/
    watch(() => localState.homeLocationInfoValid, (isValid: boolean) => {
      context.emit('updateLocationInfoValid', isValid)
      emitOtherTypeValid()
    })

    return {
      maxLength,
      locationInputRules,
      homeLocationInfoRef,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
</style>
