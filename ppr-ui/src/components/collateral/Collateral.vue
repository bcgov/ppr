<template>
  <v-container fluid no-gutters class="white pa-0" v-if="summaryView">
    <v-card flat id="collateral-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="darkBlue">mdi-car</v-icon>
          <label class="pl-3"><strong>Collateral</strong></label>
        </v-col>
      </v-row>
      <v-container
        v-if="showErrorSummary"
        :class="{ 'invalid-message': showErrorSummary }"
      >
        <v-row no-gutters class="pa-6">
          <v-col cols="auto">
            <v-icon color="error">information-outline</v-icon>&nbsp;
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
      <v-container v-else>
        <v-row no-gutters class="ps-6 pb-3" v-if="vehicleCollateral && vehicleCollateral.length > 0">
          <v-col cols="3" class="pt-4 generic-label">
            Vehicle Collateral
          </v-col>
          <v-col class="pt-6 pb-0">
            <v-data-table
              class="collateral-table"
              :headers="headers"
              :items="vehicleCollateral"
              disable-pagination
              disable-sort
              hide-default-footer
              calculate-widths
              no-data-text="No vehicle collateral"
            >
              <template v-slot:item="row" class="vehicle-data-table">
                <tr :key="row.item.id">
                  <td :class="[$style['summary-cell'], 'pl-0']">
                    {{ getVehicleDescription(row.item.type) }}
                  </td>
                  <td>{{ row.item.year }}</td>
                  <td>{{ row.item.make }}</td>
                  <td>{{ row.item.model }}</td>
                  <td :class="[$style['vehicle-cell']]">
                    {{ row.item.serialNumber }}
                  </td>
                  <td v-if="getMH">
                    {{ row.item.manufacturedHomeRegistrationNumber }}
                  </td>
                </tr>
              </template>
            </v-data-table>
          </v-col>
        </v-row>
        <v-row
          no-gutters
          class="ps-6 pt-4 pb-3"
          v-if="generalCollateralDesc.length > 0"
        >
          <v-col cols="3" class="generic-label">
            General Collateral
          </v-col>
        </v-row>
        <v-row class="px-6" no-gutters v-if="generalCollateralDesc.length > 0">
          <v-col :class="[$style['summary-text'], 'py-6']">
            {{ generalCollateralDesc }}
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-container>
  <v-container fluid no-gutters v-else class="pa-0">
    <v-row no-gutters>
      <v-col cols="auto" class="generic-label"
        >Your registration must include the following:</v-col
      >
    </v-row>
    <v-row no-gutters class="pt-6">
      <v-col cols="auto">
        <ul v-if="!collateralValid">
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
    <v-row no-gutters class="pb-4 pt-10" v-if="hasVehicleCollateral()">
      <v-col>
        <v-btn
          id="btn-add-collateral"
          outlined
          color="primary"
          :disabled="addEditInProgress"
          @click="initAdd()"
        >
          <v-icon>mdi-plus</v-icon>
          <span>Add Vehicle Collateral</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters v-if="hasVehicleCollateral()">
      <v-col>
        <div>
          <v-expand-transition>
            <v-card flat class="add-collateral-container" v-if="showAddVehicle">
              <edit-collateral
                :activeIndex="activeIndex"
                :invalidSection="invalidSection"
                @resetEvent="resetData"
              />
            </v-card>
          </v-expand-transition>
        </div>
      </v-col>
    </v-row>
    <v-row no-gutters class="pt-4" v-if="hasVehicleCollateral()">
      <v-col>
        <v-data-table
          class="collateral-table"
          :class="{ 'invalid-message': showErrorComponent }"
          :headers="headers"
          :items="vehicleCollateral"
          disable-pagination
          disable-sort
          hide-default-footer
          no-data-text="No vehicle collateral added yet."
        >
          <template v-slot:item="row" class="vehicle-data-table">
            <tr
              v-if="!showEditVehicle[row.index]"
              :key="row.item.id"
              class="vehicle-row"
            >
              <td class="pl-4">
                {{ getVehicleDescription(row.item.type) }}
              </td>
              <td>
                {{ row.item.year }}
              </td>
              <td>{{ row.item.make }}</td>
              <td>{{ row.item.model }}</td>
              <td :class="[$style['vehicle-cell']]">
                {{ row.item.serialNumber }}
              </td>
              <td v-if="getMH">
                {{ row.item.manufacturedHomeRegistrationNumber }}
              </td>

              <!-- Action Btns -->
              <td class="actions-cell px-0 py-2">
                <div class="actions">
                  <span class="edit-action">
                    <v-btn
                      text
                      color="primary"
                      class="edit-btn"
                      :id="'class-' + row.index + '-change-added-btn'"
                      @click="initEdit(row.index)"
                      :disabled="addEditInProgress"
                    >
                      <v-icon small>mdi-pencil</v-icon>
                      <span>Edit</span>
                    </v-btn>
                  </span>

                  <span class="actions__more">
                    <v-menu offset-y left nudge-bottom="4">
                      <template v-slot:activator="{ on }">
                        <v-btn
                          text
                          small
                          v-on="on"
                          color="primary"
                          class="actions__more-actions__btn"
                          :disabled="addEditInProgress"
                        >
                          <v-icon>mdi-menu-down</v-icon>
                        </v-btn>
                      </template>
                      <v-list class="actions__more-actions">
                        <v-list-item @click="removeVehicle(row.index)">
                          <v-list-item-subtitle>
                            <v-icon small>mdi-delete</v-icon>
                            <span class="ml-1">Remove</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </span>
                </div>
              </td>
            </tr>

            <!-- Edit Form -->
            <tr v-if="showEditVehicle[row.index]">
              <td :colspan="getNumCols">
                <v-expand-transition>
                  <div class="edit-vehicle-container col-12">
                    <edit-collateral
                      :activeIndex="activeIndex"
                      :invalidSection="invalidSection"
                      @removeVehicle="removeVehicle"
                      @resetEvent="resetData"
                    />
                  </div>
                </v-expand-transition>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row class="pt-8" v-if="hasGeneralCollateral()">
      <v-col>
        <v-card
          flat
          id="general-collateral"
          :class="{ 'invalid-message': showErrorComponent }"
        >
          <v-container fluid no-gutters class="pa-0">
            <v-row no-gutters class="py-6">
              <v-col cols="3" class="generic-label pa-4">
                General Collateral
              </v-col>
              <v-col cols="9" class="pr-4">
                <v-textarea
                  v-model="generalCollateralDesc"
                  id="generalCollateral"
                  auto-grow
                  counter="4000"
                  filled
                  label="Description of General Collateral"
                  class="white pt-2 text-input-field"
                  @keyup="validateGeneral()"
                  :error-messages="generalCollateralError"
                >
                </v-textarea>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted,
  computed
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { AddCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import EditCollateral from './EditCollateral.vue'
import { vehicleTableHeaders, VehicleTypes } from '@/resources'
import { useVehicle } from './composables/useVehicle'
import { APIRegistrationTypes } from '@/enums'

export default defineComponent({
  components: {
    EditCollateral
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setAddCollateral } = useActions<any>(['setAddCollateral'])
    const { getAddCollateral } = useGetters<any>(['getAddCollateral'])
    const { getRegistrationType } = useGetters<any>(['getRegistrationType'])

    const collateral: AddCollateralIF = getAddCollateral.value
    const setGeneralCollateralDesc = (collateral.generalCollateral?.length || 0) > 0
      ? collateral.generalCollateral[0].description : ''

    const registrationType = getRegistrationType.value.registrationTypeAPI

    const router = context.root.$router

    const {
      hasVehicleCollateral,
      hasGeneralCollateral,
      hasGeneralCollateralText,
      mustHaveManufacturedHomeCollateral
    } = useVehicle(props, context)

    const localState = reactive({
      summaryView: props.isSummary,
      showAddVehicle: false,
      addEditInProgress: false,
      invalidSection: false,
      activeIndex: -1,
      showEditVehicle: [false],
      generalCollateralError: '',
      vehicleCollateral: collateral.vehicleCollateral,
      generalCollateralDesc: setGeneralCollateralDesc,
      collateralValid: collateral.valid,
      showErrorComponent: collateral.showInvalid,
      getNumCols: computed((): number => {
        if (collateral.vehicleCollateral?.find(obj => obj.type === 'MH')) {
          return 7
        }
        return 6
      }),
      showErrorSummary: computed((): boolean => {
        return !collateral.valid
      }),
      getMH: computed(function () {
        return collateral.vehicleCollateral?.find(obj => obj.type === 'MH')
      }),
      headers: computed(function () {
        const headersToShow = [...vehicleTableHeaders]
        const editRow = headersToShow.pop()
        if (collateral.vehicleCollateral?.find(obj => obj.type === 'MH')) {
          headersToShow.push({
            class: 'column-mds',
            sortable: false,
            text: 'MHR Number',
            value: 'vehicle.manufacturedHomeRegistrationNumber'
          })
        }
        if (!props.isSummary) {
          headersToShow[0].class = 'column-md'
          headersToShow.push(editRow)
        } else {
          // remove left padding for summary table
          headersToShow[0].class = 'column-md pl-0'
        }
        return headersToShow
      })
    })

    watch(
      () => localState.generalCollateralDesc,
      (val: string) => {
        collateral.generalCollateral = [
          {
            added: false,
            addedDateTime: (new Date()).toString(),
            description: val,
            legacy: false
          }
        ]
        setAddCollateral(collateral)
        setValid()
      }
    )

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

    const removeVehicle = (index: number): void => {
      let collateral = getAddCollateral.value // eslint-disable-line
      localState.vehicleCollateral.splice(index, 1)
      collateral.vehicleCollateral = localState.vehicleCollateral
      setAddCollateral(collateral)
      setValid()
    }

    const getVehicleDescription = (code: string): string => {
      const vehicle = VehicleTypes.find(obj => obj.value === code)
      return vehicle.text
    }

    const initEdit = (index: number) => {
      localState.activeIndex = index
      localState.addEditInProgress = true
      localState.showEditVehicle[index] = true
    }

    const initAdd = () => {
      localState.addEditInProgress = true
      localState.showAddVehicle = true
    }

    const resetData = () => {
      localState.activeIndex = -1
      localState.addEditInProgress = false
      localState.showAddVehicle = false
      localState.showEditVehicle = [false]
      setValid()
    }

    const validateGeneral = () => {
      if (collateral.generalCollateral.length > 4000) {
        collateral.valid = false
        localState.generalCollateralError = 'Maximum 4000 characters'
      } else {
        localState.generalCollateralError = ''
        setValid()
      }
    }

    const setValid = () => {
      if (
        collateral.vehicleCollateral.length > 0 ||
        (collateral.generalCollateral.length <= 4000 &&
          collateral.generalCollateral.length > 0)
      ) {
        collateral.valid = true
        collateral.showInvalid = false
        localState.showErrorComponent = false
      } else {
        collateral.valid = false
      }
      localState.collateralValid = collateral.valid
      setAddCollateral(collateral)
    }

    const goToCollateral = (): void => {
      collateral.showInvalid = true
      setAddCollateral(collateral)
      router.push({ path: '/new-registration/add-collateral' })
    }

    onMounted(() => {
      if (hasGeneralCollateral() && !localState.generalCollateralDesc) {
        if (registrationType === APIRegistrationTypes.LIEN_UNPAID_WAGES) {
          localState.generalCollateralDesc =
            'All the personal property of the debtor'
        }
        if (hasGeneralCollateralText()) {
          localState.generalCollateralDesc =
            'All the debtor’s present and after acquired personal property, including ' +
            'but not restricted to machinery, equipment, furniture, fixtures and receivables.'
        }
      }
    })

    return {
      removeVehicle,
      initEdit,
      initAdd,
      resetData,
      getVehicleDescription,
      validateGeneral,
      goToCollateral,
      registrationType,
      hasVehicleCollateral,
      hasGeneralCollateral,
      mustHaveManufacturedHomeCollateral,
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
