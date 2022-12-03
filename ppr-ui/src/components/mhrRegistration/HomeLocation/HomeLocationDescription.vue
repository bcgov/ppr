<template>
  <v-form ref="homeLocationDescriptionForm" v-model="isHomeLocationDescriptionValid">
    <v-row no-gutters>
      <!-- Auto Populated Legal Land Description -->
      <template v-if="legalDescription">
        <v-col cols="12" class="mb-3">
          <p class="generic-label mb-0">Legal Land Description</p>
          <p class="info-text mt-2">{{ legalDescription }}</p>
        </v-col>
      </template>

      <!-- Manual Legal Land Description -->
      <template v-else-if="!showLocationInfo">
        <v-col cols="12" sm="12" md="3" class="mt-1 mb-3">
          <p class="fs-14 info-text">Don't have a pid Number?</p>
        </v-col>
        <v-col cols="12" sm="12" md="9" class="mt-1 mb-3">
          <p class="ml-0 fs-14 generic-link" @click="showLocationInfo = !showLocationInfo">
            Enter the Legal Land Description Manually
          </p>
        </v-col>
      </template>

      <!-- Home Location Info Form -->
      <v-col v-if="showLocationInfo" cols="12">
        <v-row no-gutters>
          <v-col cols="9" class="m-auto pb-0 py-2">
            <p class="generic-label">Legal Land Description</p>
          </v-col>
          <v-col class="text-right">
            <v-btn
              text
              plain="true"
              color="primary"
              class="mr-n4"
              :ripple="false"
              @click="showLocationInfo = false"
            >
              Cancel <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-col>
          <v-col cols="12">
            <p class="info-text">Enter as much of legal land description you have.</p>
            <p v-if="isStrata" class="info-text pt-2" :class="{ 'error-text': validate && !isValidLocationInfo }">
              <strong>Strata Lot, Land District</strong> and
              <strong>Strata Plan</strong> are required.
            </p>
            <p v-else class="info-text pt-2 py-1" :class="{ 'error-text': validate && !isValidLocationInfo }">
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
          :isStrata="isStrata"
          :validate="validate"
          @updateLocationInfo="locationInfo = $event"
          @updateLocationInfoValid="isValidLocationInfo = $event"
        />
      </v-col>

      <!-- Additional Location Info -->
      <v-col>
        <p class="font-weight-bold">Additional Description</p>
        <v-textarea
          filled
          class="rounded-top"
          height="6rem"
          ref="additionalDescriptionRef"
          label="Park Name / Additional Description"
          v-model.trim="additionalDescription"
          :rules="maxLength(80)"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { defineComponent, computed, reactive, toRefs, watch } from '@vue/composition-api'
import { HomeLocationInfo } from '@/components/common'
import { useInputRules } from '@/composables'
import { MhrLocationInfoIF } from '@/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeLocationDescription',
  emits: ['setIsValidLocationInfo', 'setShowLocationInfo', 'setLocationInfo', 'setAdditionalDescription'],
  components: {
    HomeLocationInfo
  },
  props: {
    validate: { type: Boolean, default: false },
    legalDescription: { type: String, default: '' },
    isStrata: { type: Boolean, default: false }
  },
  setup (props, context) {
    const { maxLength } = useInputRules()

    const localState = reactive({
      isValidLocationInfo: false,
      showLocationInfo: false,
      locationInfo: null,
      additionalDescription: '',
      isHomeLocationDescriptionValid: false,
      isValidDescription: computed((): boolean => {
        return localState.isHomeLocationDescriptionValid &&
          (!localState.showLocationInfo || localState.isValidLocationInfo)
      })
    })

    watch(() => localState.isValidDescription, (val: boolean) => {
      context.emit('setIsValidLocationInfo', val)
    })
    watch(() => localState.showLocationInfo, (val: boolean) => {
      context.emit('setShowLocationInfo', val)
    })
    watch(() => localState.locationInfo, (val: MhrLocationInfoIF) => {
      context.emit('setLocationInfo', val)
    })
    watch(() => localState.additionalDescription, (val: string) => {
      context.emit('setAdditionalDescription', val)
    })

    return {
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
