<template>
  <v-card flat rounded id="home-location-info">
    <v-form ref="homeLocationInfoRef" v-model="homeLocationInfoValid">

      <v-row no-gutters class="pt-4">
        <v-col>
          <v-text-field
            filled
            id="lot"
            label="Lot"
            v-model="locationInfo.lot"
            :rules="locationInputRules(10, 'Enter a lot number')"
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
            :rules="locationInputRules(20, 'Enter a land district')"
            persistent-hint
          />
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            filled
            id="plan"
            label="Plan"
            v-model="locationInfo.plan"
            :rules="locationInputRules(12, 'Enter a plan number')"
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
            :rules="locationInputRules(17, 'Enter a district lot')"
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
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { MhrLocationInfoIF } from '@/interfaces'
import { useInputRules } from '@/composables/useInputRules'
/* eslint-disable no-unused-vars */

export default defineComponent({
  name: 'HomeLocationInfo',
  emits: ['updateLocationInfo', 'updateLocationValid'],
  props: {
    validate: { type: Boolean, default: false }
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
      applyRequired: computed((): boolean => {
        const info = localState.locationInfo
        return !info.lot && !info.parcel && !info.block && !info.districtLot && !info.landDistrict && !info.plan
      })
    })

    const locationInputRules = (length: number, requiredMsg: string) => {
      return customRules(
        maxLength(length),
        localState.applyRequired ? required(requiredMsg) : []
      )
    }

    /** Prompt local validations on validate event. **/
    watch(() => props.validate, (validate) => {
      // @ts-ignore - function exists
      if (validate) context.refs.homeLocationInfoRef.validate()
    })

    /** Emit local model to parent when it changes. **/
    watch(() => localState.locationInfo, (locationInfo: MhrLocationInfoIF) => {
      context.emit('updateLocationInfo', locationInfo)
    }, { deep: true })

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
