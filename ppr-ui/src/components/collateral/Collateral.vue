<template>
  <v-container fluid no-gutters class="white pa-0 pb-10" v-if="summaryView">
    <v-card flat id="collateral-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="darkBlue">mdi-car</v-icon>
          <label class="pl-3"><strong>Collateral</strong></label>
        </v-col>
      </v-row>
      <v-container
        v-if="!valid"
        :class="{ 'invalid-message': !valid }"
      >
        <v-row no-gutters class="pa-6">
          <v-col cols="auto">
            <v-icon color="error">mdi-information-outline</v-icon>&nbsp;
            <span class="invalid-message">This step is unfinished. </span>
            <span
              id="router-link-collateral"
              class="invalid-link"
              @click="goToCollateral()"
              >Return to this step to complete it.</span
            >
          </v-col>
        </v-row>
      </v-container>
      <div v-else>
        <vehicle-collateral :isSummary="true" :showInvalid="showInvalid" />
        <general-collateral :isSummary="true" />
      </div>
    </v-card>
  </v-container>
  <v-container v-else class="pa-0" fluid no-gutters>
    <v-row no-gutters>
      <v-col cols="auto" class="generic-label"
        >Your registration must include the following:</v-col
      >
    </v-row>
    <v-row no-gutters class="pt-6">
      <v-col cols="auto">
        <ul v-if="!valid">
          <li>{{ getCollateralDescription() }}</li>
        </ul>
        <span v-else>
          <v-icon color="green darken-2" class="agreement-valid-icon"
            >mdi-check</v-icon
          >
          {{ getCollateralDescription() }}
        </span>
      </v-col>
    </v-row>
    <vehicle-collateral :isSummary="false" :showInvalid="showInvalid && !valid" />
    <general-collateral
      v-if="hasGeneralCollateral()"
      class="pt-8"
      :isSummary="false"
      :showInvalid="showInvalid && !valid"
      @valid="generalCollateralValid = $event"
    />
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
// local components
import { GeneralCollateral } from './generalCollateral'
import { VehicleCollateral } from './vehicleCollateral'
// local types/resources/etc.
import {
  AddCollateralIF, // eslint-disable-line no-unused-vars
  GeneralCollateralIF, // eslint-disable-line no-unused-vars
  VehicleCollateralIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { useVehicle } from './vehicleCollateral/factories'

export default defineComponent({
  name: 'Collateral',
  components: {
    GeneralCollateral,
    VehicleCollateral
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { getAddCollateral } = useGetters<any>(['getAddCollateral'])
    const {
      setCollateralShowInvalid,
      setCollateralValid
    } = useActions<any>(['setCollateralShowInvalid', 'setCollateralValid'])

    const router = context.root.$router

    const {
      hasVehicleCollateral,
      hasGeneralCollateral,
      mustHaveManufacturedHomeCollateral
    } = useVehicle(props, context)

    const localState = reactive({
      generalCollateralValid: true,
      summaryView: props.isSummary,
      collateral: computed((): AddCollateralIF => {
        return getAddCollateral.value as AddCollateralIF
      }),
      showInvalid: computed((): boolean => {
        return localState.collateral.showInvalid
      }),
      valid: computed((): boolean => {
        return localState.collateral.valid
      }),
      vehicleCollateralLength: computed((): number => {
        return localState.collateral.vehicleCollateral?.length || 0
      })
    })

    const getCollateralDescription = (): string => {
      if (hasVehicleCollateral() && hasGeneralCollateral()) {
        return 'At least one form of collateral (vehicle or general)'
      }
      if (mustHaveManufacturedHomeCollateral()) {
        return 'At least one manufactured home as vehicle collateral'
      }
      if (hasGeneralCollateral()) {
        return 'General Collateral'
      }
      if (hasVehicleCollateral()) {
        return 'At least one vehicle as collateral'
      }
    }

    const goToCollateral = (): void => {
      setCollateralShowInvalid(true)
      router.push({ path: '/new-registration/add-collateral' })
    }

    watch(() => localState.collateral.vehicleCollateral, (val: VehicleCollateralIF[]) => {
      console.log('here1', val)
      if (
        val?.length > 0 ||
        (localState.collateral?.generalCollateral?.length > 0 &&
          localState.generalCollateralValid)
      ) {
        setCollateralValid(true)
        setCollateralShowInvalid(false)
      } else {
        setCollateralValid(false)
      }
    }, { deep: true, immediate: true })

    watch(() => localState.collateral.generalCollateral, (val: GeneralCollateralIF[]) => {
      console.log('here2', val)
      if (
        (val?.length > 0 && localState.generalCollateralValid) ||
        localState.collateral?.vehicleCollateral?.length > 0
      ) {
        setCollateralValid(true)
        setCollateralShowInvalid(false)
      } else {
        setCollateralValid(false)
      }
    }, { deep: true, immediate: true })

    return {
      goToCollateral,
      hasGeneralCollateral,
      getCollateralDescription,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.length-trust-label {
  font-size: 0.875rem;
}
.summary-text {
  font-size: 14px;
  color: $gray7;
}
.summary-cell {
  overflow: visible;
  text-overflow: inherit;
  white-space: inherit;
}

.vehicle-cell {
  text-transform: uppercase;
}
</style>
