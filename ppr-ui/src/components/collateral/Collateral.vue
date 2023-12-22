<template>
  <v-container
    v-if="summaryView || registrationFlowType == RegistrationFlowType.AMENDMENT"
    id="collateral-component"
    fluid
    class="bg-white pa-0 rounded-bottom noGutters"
    :class="!valid && registrationFlowType !== RegistrationFlowType.AMENDMENT ? '' : 'pb-10'"
  >
    <v-card
      id="collateral-summary"
      flat
    >
      <v-row
        noGutters
        class="summary-header py-2"
      >
        <v-col
          cols="auto"
          class="py-2"
        >
          <v-icon color="darkBlue">
            mdi-car
          </v-icon>
          <label class="pl-3"><strong>Collateral</strong></label>
        </v-col>
      </v-row>
      <v-container
        v-if="!valid && registrationFlowType === RegistrationFlowType.NEW"
        :class="{ 'border-error-left': !valid }"
      >
        <v-row
          noGutters
          class="pa-6"
        >
          <v-col cols="auto">
            <v-icon color="error">
              mdi-information-outline
            </v-icon>&nbsp;
            <span class="error-text">This step is unfinished. </span>
            <span
              id="router-link-collateral"
              class="generic-link"
              @click="goToCollateral()"
            >Return to this step to complete it.</span>
          </v-col>
        </v-row>
      </v-container>
      <VehicleCollateral
        v-if="vehicleCollateralLength > 0 || !summaryView"
        :isSummary="summaryView"
        :showInvalid="collateral.showInvalid"
        :setShowErrorBar="showErrorBar && vehicleCollateralOpen"
        @collateralOpen="setVehicleCollateralOpen($event)"
      />
      <GeneralCollateral
        v-if="showGeneralCollateral"
        :isSummary="summaryView"
        :setShowErrorBar="showErrorBar && generalCollateralOpen"
        @collateralOpen="setGeneralCollateralOpen($event)"
      />
    </v-card>
  </v-container>
  <v-container
    v-else
    id="collateral-edit"
    class="pa-0 noGutters"
    fluid
  >
    <v-row noGutters>
      <v-col
        cols="auto"
        class="generic-label"
      >
        Your registration must include the following:
      </v-col>
    </v-row>
    <v-row
      id="collateral-edit-description"
      class="pt-6"
      noGutters
    >
      <v-col cols="auto">
        <ul
          v-if="!valid"
          class="ml-5"
        >
          <li>{{ getCollateralDescription() }}</li>
        </ul>
        <span v-else>
          <v-icon
            color="green-darken-2"
            class="agreement-valid-icon"
          >mdi-check</v-icon>
          {{ getCollateralDescription() }}
        </span>
      </v-col>
    </v-row>
    <VehicleCollateral
      :isSummary="false"
      :showInvalid="collateral.showInvalid && !valid && hasVehicleCollateral()"
      @collateralOpen="setVehicleCollateralOpen($event)"
    />
    <GeneralCollateral
      v-if="hasGeneralCollateral(registrationType)"
      class="pt-8"
      :isSummary="false"
      :setShowInvalid="collateral.showInvalid && !valid"
      @collateralOpen="setGeneralCollateralOpen($event)"
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
  watch,
  onUnmounted
} from 'vue'
import { useStore } from '@/store/store'
import { useRouter } from 'vue-router'
import { GeneralCollateral } from './generalCollateral'
import { VehicleCollateral } from './vehicleCollateral'
import { ActionTypes, APIRegistrationTypes, RegistrationFlowType } from '@/enums'
import {
  AddCollateralIF,
  GeneralCollateralIF,
} from '@/interfaces'
import { useGeneralCollateral } from './generalCollateral/factories'
import { useVehicle } from './vehicleCollateral/factories'
import { storeToRefs } from 'pinia'

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
  emits: [
    'setCollateralValid',
    'collateralOpen'
  ],
  setup (props, context) {
    const router = useRouter()
    const {
      // Actions
      setCollateralShowInvalid,
      setCollateralValid,
      setGeneralCollateral
    } = useStore()
    const {
      // Getters
      getAddCollateral,
      getRegistrationFlowType,
      getRegistrationType
    } = storeToRefs(useStore())

    const registrationFlowType = getRegistrationFlowType.value
    const registrationType = getRegistrationType.value?.registrationTypeAPI

    const {
      hasVehicleCollateral,
      hasOptionalVehicleCollateral,
      mustHaveManufacturedHomeCollateral
    } = useVehicle(props, context)
    const {
      hasGeneralCollateral,
      hasGeneralCollateralText,
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
      }),
      isValidGc: computed((): boolean => {
        return (
          (!hasGeneralCollateral(registrationType)) ||
          (hasGeneralCollateral(registrationType) && !!localState.generalCollateralLength &&
            hasOptionalVehicleCollateral()) ||
          (hasGeneralCollateral(registrationType) && hasVehicleCollateral() && !!localState.vehicleCollateralLength)
        )
      })
    })

    onMounted(() => {
      if (
        getRegistrationFlowType.value === RegistrationFlowType.NEW &&
        localState.collateral?.generalCollateral?.length === 0 &&
        !localState.summaryView
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

    onUnmounted(() => {
      // clear general collateral description if there is no valid text left in editor (html tags not included)
      if (!!getAddCollateral.value?.generalCollateral?.length &&
        getAddCollateral.value?.generalCollateral[0]?.description?.replace(/(<([^>]+)>)/ig, '')?.trim().length === 0) {
        setGeneralCollateral([])
        // clear collateral step check mark if there are no vehicles
        // (this resets check mark that was set by general collateral description)
        if (getAddCollateral.value.vehicleCollateral.length === 0) {
          getAddCollateral.value.valid = false
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

    watch(() => localState.collateral.vehicleCollateral, () => {
      if ((vehiclesValid() || localState.collateral?.generalCollateral?.length > 0 ||
        registrationType === APIRegistrationTypes.TRANSITION_TAX_LIEN) &&
        localState.isValidGc
      ) {
        setCollateralValidAndEmit(true)
        setCollateralShowInvalid(false)
      } else {
        setCollateralValidAndEmit(false)
      }
    }, { deep: true, immediate: true })

    watch(() => localState.collateral.generalCollateral, (val: GeneralCollateralIF[]) => {
      if (val?.length > 0 ||
        registrationType === APIRegistrationTypes.TRANSITION_TAX_LIEN ||
        // vehicle collateral is optional for Income Tax registration type
        (vehiclesValid() && registrationType !== APIRegistrationTypes.INCOME_TAX) &&
        localState.isValidGc
      ) {
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
      hasVehicleCollateral,
      setVehicleCollateralOpen,
      setGeneralCollateralOpen,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.summary-cell {
  overflow: visible;
  text-overflow: inherit;
  white-space: inherit;
}

.vehicle-cell {
  text-transform: uppercase;
}
</style>
