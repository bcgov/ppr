<template>
  <v-form
    ref="homeLocationDescriptionForm"
    v-model="isHomeLocationDescriptionValid"
  >
    <v-row no-gutters>
      <!-- Auto Populated Legal Land Description -->
      <template v-if="legalDescription">
        <v-col
          cols="12"
          class="mb-5"
        >
          <p class="generic-label mb-0">
            Legal Land Description
          </p>
          <p class="info-text mt-2">
            {{ legalDescription }}
          </p>
        </v-col>
      </template>

      <!-- Manual Legal Land Description -->
      <template v-else-if="!showLocationInfo && !isReserve">
        <v-col
          cols="12"
          sm="12"
          md="3"
          class="mt-1 mb-3"
        >
          <p class="fs-14 info-text">
            Don't have a PID Number?
          </p>
        </v-col>
        <v-col
          cols="12"
          sm="12"
          md="9"
          class="mt-1 mb-3"
        >
          <p
            class="ml-0 fs-14 generic-link"
            @click="showLocationInfo = !showLocationInfo"
          >
            Enter the Legal Land Description Manually
          </p>
        </v-col>
      </template>

      <!-- Home Location Info Form -->
      <v-col
        v-if="showLocationInfo || isReserve"
        cols="12"
      >
        <v-row no-gutters>
          <v-col
            cols="9"
            class="pb-0 py-2"
          >
            <p class="generic-label">
              Legal Land Description
            </p>
          </v-col>
          <v-col
            v-if="!isReserve"
            class="text-right"
          >
            <v-btn
              variant="plain"
              color="primary"
              class="mr-n4"
              :ripple="false"
              @click="handleCancel()"
            >
              Cancel <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-col>
          <v-col cols="12">
            <p class="info-text">
              Enter as much of the legal land description as you have.
            </p>
            <p
              v-if="isReserve"
              class="info-text pt-2"
              :class="{ 'error-text': validate && !isValidLocationInfo }"
            >
              <strong>Band Name and Reserve Number</strong> are required.
            </p>
            <p
              v-else-if="isStrata"
              class="info-text pt-2"
              :class="{ 'error-text': validate && !isValidLocationInfo }"
            >
              <strong>Strata Lot, Land District</strong> and
              <strong>Strata Plan</strong> are required.
            </p>
            <p
              v-else
              class="info-text pt-2 py-1"
              :class="{ 'error-text': validate && !isValidOtherType }"
            >
              <span>At least one of the following combinations is required:</span><br>
              <span class="ml-4">
                1) <strong>Lot, Land District</strong> and <strong>Plan</strong> or<br>
              </span>
              <span class="ml-4">
                2) <strong>Land District</strong> and <strong>District Lot</strong>
              </span>
            </p>
          </v-col>
        </v-row>

        <HomeLocationInfo
          :home-location-info="locationDescription"
          :is-reserve="isReserve"
          :is-strata="isStrata"
          :validate="validate"
          @update-location-info="locationInfo = $event"
          @update-location-description="additionalDescription = $event"
          @update-location-info-valid="isValidLocationInfo = $event"
        />
      </v-col>

      <!-- Additional Location Info -->
      <v-col v-if="!isReserve">
        <p class="font-weight-bold">
          Additional Description
        </p>
        <v-textarea
          ref="additionalDescriptionRef"
          v-model.trim="additionalDescription"
          variant="filled"
          color="primary"
          class="rounded-top mt-3"
          label="Park Name / Additional Description"
          :rules="maxLength(80)"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, computed, reactive, toRefs, watch, onMounted } from 'vue'
import { HomeLocationInfo } from '@/components/common'
import { useStore } from '@/store/store'
import { useInputRules, useNewMhrRegistration } from '@/composables'
import type { MhrLocationInfoIF, MhrRegistrationHomeLocationIF } from '@/interfaces'

export default defineComponent({
  name: 'HomeLocationDescription',
  components: {
    HomeLocationInfo
  },
  props: {
    locationDescription: {
      type: Object as () => MhrRegistrationHomeLocationIF,
      default: () => {}
    },
    validate: { type: Boolean, default: false },
    legalDescription: { type: String, default: '' },
    isReserve: { type: Boolean, default: false },
    isStrata: { type: Boolean, default: false }
  },
  emits: ['setIsValidLocationInfo', 'setShowLocationInfo', 'setLocationInfo', 'setAdditionalDescription'],
  setup (props, context) {
    const { setIsManualLocation } = useStore()

    const { maxLength } = useInputRules()
    const { resetLocationInfoFields } = useNewMhrRegistration()

    const localState = reactive({
      isValidLocationInfo: false,
      showLocationInfo: false,
      locationInfo: {} as MhrLocationInfoIF,
      additionalDescription: props.locationDescription.additionalDescription || '',
      isHomeLocationDescriptionValid: false,
      isValidDescription: computed((): boolean => {
        return (props.isReserve || localState.isHomeLocationDescriptionValid) &&
          ((!localState.showLocationInfo && !props.isReserve) || localState.isValidLocationInfo)
      }),
      isValidOtherType: computed((): boolean => {
        return (
          (!!localState.locationInfo.lot && !!localState.locationInfo.landDistrict && !!localState.locationInfo.plan) ||
          (!!localState.locationInfo.landDistrict && !!localState.locationInfo.districtLot)
        )
      })
    })

    onMounted(() => {
      // Show the locationInfo form if there is any common properties that have stored/draft data
      // We have to be specific because registrationLocation contains other properties
      const commonLocationProperties = [
        'lot', 'landDistrict', 'plan', 'districtLot',
        'partOf', 'section', 'township', 'range',
        'meridian', 'parcel', 'block', 'exceptionPlan'
      ]
      localState.showLocationInfo = commonLocationProperties.some(key => !!props.locationDescription[key])
    })

    const handleCancel = (): void => {
      // reset locationInfo values and hide manual form
      localState.locationInfo = resetLocationInfoFields(localState.locationInfo)
      localState.showLocationInfo = false
    }

    watch(() => localState.isValidDescription, (isValid: boolean) => {
      context.emit('setIsValidLocationInfo', isValid)
    })
    watch(() => localState.showLocationInfo, (showLocationInfo: boolean) => {
      setIsManualLocation(showLocationInfo)
      context.emit('setShowLocationInfo', showLocationInfo)
    })
    watch(() => localState.locationInfo, (locationInfo: MhrLocationInfoIF) => {
      context.emit('setLocationInfo', locationInfo)
    }, { deep: true })
    watch(() => localState.additionalDescription, (description: string) => {
      context.emit('setAdditionalDescription', description)
    })

    return {
      maxLength,
      handleCancel,
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
