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
      <vehicle-collateral
        v-if="vehicleCollateralLength > 0"
        :isSummary="true"
        :showInvalid="showInvalid"
      />
      <general-collateral
        v-if="generalCollateralLength > 0"
        :isSummary="true"
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
    <vehicle-collateral :isSummary="false" :showInvalid="showInvalid && !valid" />
    <general-collateral
      v-if="hasGeneralCollateral(registrationType)"
      class="pt-8"
      :isSummary="false"
      @valid="generalCollateralValid = $event"
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
import { APIRegistrationTypes, RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
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
    setRegistrationType: String as () => APIRegistrationTypes
  },
  setup (props, context) {
    const {
      getAddCollateral,
      getRegistrationFlowType
    } = useGetters<any>(['getAddCollateral', 'getRegistrationFlowType'])

    const {
      setCollateralShowInvalid,
      setCollateralValid,
      setGeneralCollateral
    } = useActions<any>(['setCollateralShowInvalid', 'setCollateralValid', 'setGeneralCollateral'])

    const router = context.root.$router

    const {
      hasVehicleCollateral,
      mustHaveManufacturedHomeCollateral
    } = useVehicle(props, context)
    const {
      hasGeneralCollateral,
      hasGeneralCollateralText
    } = useGeneralCollateral()

    const localState = reactive({
      generalCollateralValid: true,
      registrationType: props.setRegistrationType,
      summaryView: props.isSummary,
      collateral: computed((): AddCollateralIF => {
        return getAddCollateral.value as AddCollateralIF
      }),
      generalCollateralLength: computed((): number => {
        return localState.collateral.generalCollateral?.length || 0
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

    onMounted(() => {
      if (
        getRegistrationFlowType.value === RegistrationFlowType.NEW &&
        localState.collateral?.generalCollateral?.length === 0
      ) {
        if (hasGeneralCollateral(localState.registrationType)) {
          if (localState.registrationType === APIRegistrationTypes.LIEN_UNPAID_WAGES) {
            setGeneralCollateral([{ description: 'All the personal property of the debtor' }])
          }
          if (hasGeneralCollateralText(localState.registrationType)) {
            setGeneralCollateral([{
              description: 'All the debtor’s present and after acquired personal property, including ' +
                'but not restricted to machinery, equipment, furniture, fixtures and receivables.'
            }])
          }
        }
      }
    })

    const getCollateralDescription = (): string => {
      if (hasVehicleCollateral() && hasGeneralCollateral(localState.registrationType)) {
        return 'At least one form of collateral (vehicle or general)'
      }
      if (mustHaveManufacturedHomeCollateral()) {
        return 'At least one manufactured home as vehicle collateral'
      }
      if (hasGeneralCollateral(localState.registrationType)) {
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

    watch(() => props.isSummary, (val: boolean) => {
      localState.summaryView = val
    })

    watch(() => localState.collateral.vehicleCollateral, (val: VehicleCollateralIF[]) => {
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
