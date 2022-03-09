<template>
  <v-container fluid no-gutters
    id="collateral-component"
    class="white pa-0 rounded-bottom"
    :class="!valid && registrationFlowType !== RegistrationFlowType.AMENDMENT ? '' : 'pb-10'"
    v-if="summaryView || registrationFlowType == RegistrationFlowType.AMENDMENT"
  >
    <v-card flat id="collateral-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="darkBlue">mdi-car</v-icon>
          <label class="pl-3"><strong>Collateral</strong></label>
        </v-col>
      </v-row>
      <v-container
        v-if="!valid && registrationFlowType === RegistrationFlowType.NEW"
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
      <vehicle-collateral
        v-if="vehicleCollateralLength > 0 || !summaryView"
        :isSummary="summaryView"
        :showInvalid="collateral.showInvalid"
        :setShowErrorBar="showErrorBar && vehicleCollateralOpen"
        @collateralOpen="setVehicleCollateralOpen($event)"
      />
      <general-collateral
        v-if="showGeneralCollateral"
        :isSummary="summaryView"
        :setShowErrorBar="showErrorBar && generalCollateralOpen"
        @collateralOpen="setGeneralCollateralOpen($event)"
      />
    </v-card>
  </v-container>
  <v-container v-else id="collateral-edit" class="pa-0" fluid no-gutters>
    <v-row no-gutters>
      <v-col cols="auto" class="generic-label"
        >Your registration must include the following:</v-col
      >
    </v-row>
    <v-row id="collateral-edit-description" class="pt-6" no-gutters>
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
    <vehicle-collateral
      :isSummary="false"
      :showInvalid="collateral.showInvalid && !valid"
      @collateralOpen="setVehicleCollateralOpen($event)"
    />
    <general-collateral
      v-if="hasGeneralCollateral(registrationType)"
      class="pt-8"
      @collateralOpen="setGeneralCollateralOpen($event)"
      :isSummary="false"
    />
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  onMounted,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
// local components
import { GeneralCollateral } from './generalCollateral'
import { VehicleCollateral } from './vehicleCollateral'
// local types/resources/etc.
import { ActionTypes, APIRegistrationTypes, RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import {
  AddCollateralIF, // eslint-disable-line no-unused-vars
  GeneralCollateralIF, // eslint-disable-line no-unused-vars
  VehicleCollateralIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { useGeneralCollateral } from './generalCollateral/factories'
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
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const {
      getAddCollateral,
      getRegistrationFlowType,
      getRegistrationType
    } = useGetters<any>(['getAddCollateral', 'getRegistrationFlowType', 'getRegistrationType'])

    const {
      setCollateralShowInvalid,
      setCollateralValid,
      setGeneralCollateral
    } = useActions<any>(['setCollateralShowInvalid', 'setCollateralValid', 'setGeneralCollateral'])

    const router = context.root.$router
    const registrationFlowType = getRegistrationFlowType.value
    const registrationType = getRegistrationType.value.registrationTypeAPI

    const {
      hasVehicleCollateral,
      mustHaveManufacturedHomeCollateral
    } = useVehicle(props, context)
    const {
      hasGeneralCollateral,
      hasGeneralCollateralText
    } = useGeneralCollateral()

    const localState = reactive({
      vehicleCollateralOpen: false,
      generalCollateralOpen: false,
      summaryView: computed((): boolean => {
        return props.isSummary
      }),
      collateral: computed((): AddCollateralIF => {
        return getAddCollateral.value as AddCollateralIF
      }),
      generalCollateralLength: computed((): number => {
        return localState.collateral.generalCollateral?.length || 0
      }),
      showGeneralCollateral: computed((): boolean => {
        return ((localState.generalCollateralLength > 0 || !localState.summaryView) &&
          (hasGeneralCollateral(registrationType)))
      }),
      valid: computed((): boolean => {
        return localState.collateral.valid
      }),
      vehicleCollateralLength: computed((): number => {
        return localState.collateral.vehicleCollateral?.length || 0
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    onMounted(() => {
      if (
        getRegistrationFlowType.value === RegistrationFlowType.NEW &&
        localState.collateral?.generalCollateral?.length === 0
      ) {
        if (hasGeneralCollateral(registrationType)) {
          if (registrationType === APIRegistrationTypes.LIEN_UNPAID_WAGES) {
            setGeneralCollateral([{
              description: 'All the personal property of the debtor, ' +
            'including money due or accruing due'
            }])
          }
          if (hasGeneralCollateralText(registrationType)) {
            setGeneralCollateral([{
              description: 'All the debtor’s present and after acquired personal property, including ' +
                'but not restricted to machinery, equipment, furniture, fixtures and receivables.'
            }])
          }
        }
      }
    })

    const getCollateralDescription = (): string => {
      if (hasVehicleCollateral() && hasGeneralCollateral(registrationType) &&
        (registrationType !== APIRegistrationTypes.LIEN_UNPAID_WAGES)) {
        return 'At least one form of collateral (vehicle or general)'
      }
      if (mustHaveManufacturedHomeCollateral()) {
        return 'At least one manufactured home as vehicle collateral'
      }
      if (hasGeneralCollateral(registrationType)) {
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

    const setCollateralValidAndEmit = (valid): void => {
      setCollateralValid(valid)
      context.emit('setCollateralValid', valid)
    }

    const setVehicleCollateralOpen = (isOpen): void => {
      localState.vehicleCollateralOpen = isOpen
      context.emit('collateralOpen', localState.vehicleCollateralOpen || localState.generalCollateralOpen)
    }
    const setGeneralCollateralOpen = (isOpen): void => {
      localState.generalCollateralOpen = isOpen
      context.emit('collateralOpen', localState.vehicleCollateralOpen || localState.generalCollateralOpen)
    }

    const vehiclesValid = (): boolean => {
      let validity = false
      for (let i = 0; i < localState.collateral.vehicleCollateral?.length; i++) {
        // is valid if there is at least one vehicle
        if (localState.collateral.vehicleCollateral[i].action !== ActionTypes.REMOVED) {
          validity = true
        }
      }
      return validity
    }

    watch(() => props.isSummary, (val: boolean) => {
      localState.summaryView = val
    })

    watch(() => localState.collateral.vehicleCollateral, (val: VehicleCollateralIF[]) => {
      if (vehiclesValid() || localState.collateral?.generalCollateral?.length > 0 ||
      registrationType === APIRegistrationTypes.TRANSITION_TAX_LIEN) {
        setCollateralValidAndEmit(true)
        setCollateralShowInvalid(false)
      } else {
        setCollateralValidAndEmit(false)
      }
    }, { deep: true, immediate: true })

    watch(() => localState.collateral.generalCollateral, (val: GeneralCollateralIF[]) => {
      if (val?.length > 0 || vehiclesValid() || registrationType === APIRegistrationTypes.TRANSITION_TAX_LIEN) {
        setCollateralValidAndEmit(true)
        setCollateralShowInvalid(false)
      } else {
        setCollateralValidAndEmit(false)
      }
    }, { deep: true, immediate: true })

    return {
      goToCollateral,
      hasGeneralCollateral,
      getCollateralDescription,
      registrationFlowType,
      registrationType,
      RegistrationFlowType,
      setVehicleCollateralOpen,
      setGeneralCollateralOpen,
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
