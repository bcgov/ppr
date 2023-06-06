<template>
  <v-container v-if="isSummary" class="pb-0">
    <v-row
      no-gutters
      :class="registrationFlowType !== RegistrationFlowType.AMENDMENT ? 'ps-6' : ''"
      v-if="vehicleCollateral && vehicleCollateral.length > 0"
    >
      <v-col cols="12" class="pt-4 generic-label">
        Vehicle Collateral
      </v-col>
      <v-col
        :class="registrationFlowType === RegistrationFlowType.AMENDMENT ? 'ps-4' : ''"
        class="pt-6 pb-0"
      >
        <v-simple-table
          class="collateral-table vehicle-data-table"
          no-data-text="No vehicle collateral"
        >
          <template v-slot:default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th v-for="header in headers" :key="header.value" :class="header.class">
                  {{ header.text }}
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody v-if="vehicleCollateral.length > 0">
              <tr v-for="item in vehicleCollateral" :key="item.id" :class="rowClass(item.action)">
                <td class="summary-cell pl-0">
                  <div :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}">
                    {{ getVehicleDescription(item.type) }}
                  </div>
                  <div v-if="item.action && registrationFlowType === RegistrationFlowType.AMENDMENT">
                    <v-chip v-if="item.action === ActionTypes.REMOVED"
                            x-small label color="#grey lighten-2" text-color="$gray9">
                      {{ item.action }}
                    </v-chip>
                    <v-chip v-else x-small label color="#1669BB" text-color="white">
                      {{ item.action }}
                    </v-chip>
                  </div>
                </td>
                <td>{{ item.year }}</td>
                <td>{{ item.make }}</td>
                <td>{{ item.model }}</td>
                <td :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}"
                    class="vehicle-cell">
                  {{ item.serialNumber }}
                </td>
                <td v-if="getMH" :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}">
                  {{ item.manufacturedHomeRegistrationNumber }}
                </td>
              </tr>
            </tbody>
            <tbody v-else>
              <tr class="text-center">
                <td :colspan="headers.length">No vehicle collateral added yet.</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>
  </v-container>

  <v-container class="no-gutters" v-else
    :class="containerClass"
    fluid
  >
    <v-row
      no-gutters
      class="pb-4 pt-10 pl-1"
      v-if="(hasVehicleCollateral() || hasOptionalVehicleCollateral()) && !isRepairersLienAmendment"
    >
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
    <v-row
      :class="showErrorBar ? 'error-margin' : ''" no-gutters
      v-if="(hasVehicleCollateral() || hasOptionalVehicleCollateral())"
    >
      <v-col>
        <div>
          <v-expand-transition>
            <v-card flat class="add-collateral-container" v-if="showAddVehicle">
              <edit-collateral
                :activeIndex="activeIndex"
                :invalidSection="invalidSection"
                :setShowErrorBar="showErrorBar"
                @resetEvent="resetData"
              />
            </v-card>
          </v-expand-transition>
        </div>
      </v-col>
    </v-row>
    <v-row no-gutters class="pt-4" v-if="(hasVehicleCollateral() || hasOptionalVehicleCollateral())">
      <v-col :class="{ 'box-shadow-left': showErrorBar && activeIndex >= 0 }">

        <v-simple-table class="collateral-table vehicle-data-table" :class="{ 'invalid-message': showErrorComponent }">
          <template v-slot:default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th v-for="header in headers" :key="header.value" :class="header.class">
                  {{ header.text }}
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody v-if="vehicleCollateral.length > 0">
              <tr
                  v-for="(item, index) in vehicleCollateral"
                  :key="item.id"
                  class="vehicle-row"
                  :class="rowClass(item.action)"
              >
                <!-- Edit Form -->
                <template v-if="showEditVehicle[index]">
                  <td :colspan="getNumCols">
                    <div class="edit-vehicle-container col-12">
                      <edit-collateral
                          :activeIndex="activeIndex"
                          :invalidSection="invalidSection"
                          :setShowErrorBar="showErrorBar"
                          @removeVehicle="removeVehicle($event)"
                          @resetEvent="resetData"
                      />
                    </div>
                  </td>
                </template>

                <template v-else>
                  <td class="pl-4">
                    <div :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}">
                      {{ getVehicleDescription(item.type) }}
                    </div>
                    <div v-if="item.action && registrationFlowType === RegistrationFlowType.AMENDMENT">
                      <v-chip v-if="item.action === ActionTypes.REMOVED"
                              x-small label color="#grey lighten-2" text-color="$gray9">
                        {{ item.action }}
                      </v-chip>
                      <v-chip v-else x-small label color="#1669BB" text-color="white">
                        {{ item.action }}
                      </v-chip>
                    </div>
                  </td>
                  <td>{{ item.year }}</td>
                  <td>{{ item.make }}</td>
                  <td>{{ item.model }}</td>
                  <td class="vehicle-cell">
                    {{ item.serialNumber }}
                  </td>
                  <td v-if="getMH">
                    {{ item.manufacturedHomeRegistrationNumber }}
                  </td>

                  <!-- Action Btns -->
                  <td class="actions-width actions-cell px-0 py-2">
                    <div class="actions actions-up float-right pr-4">
                    <span v-if="isRepairersLienAmendment && !item.action">
                      <v-tooltip
                          top
                          content-class="top-tooltip pa-4 mr-2"
                          transition="fade-transition"
                          :disabled="!isLastDelete"
                      >
                        <template v-slot:activator="{ on: onTooltip }">
                          <div v-on="onTooltip">
                            <v-btn
                                text
                                color="primary"
                                class="smaller-button dlt-btn primary--text"
                                :id="'class-' + index + '-dlt-btn'"
                                @click="removeVehicle(index)"
                                :disabled="isLastDelete"
                            >
                              <v-icon small>mdi-delete</v-icon>
                              <span>Delete</span>
                            </v-btn>
                          </div>
                        </template>
                        An amendment cannot remove all vehicle collateral.
                        This would require a Total Discharge.
                      </v-tooltip>
                    </span>
                      <span
                          v-else-if="registrationFlowType !== RegistrationFlowType.AMENDMENT
                      || (registrationFlowType === RegistrationFlowType.AMENDMENT &&
                      (item.action === ActionTypes.ADDED) || !item.action)"
                      >
                      <v-btn
                          text
                          color="primary"
                          class="edit-btn smaller-button even-smaller"
                          :id="'class-' + index + '-change-added-btn'"
                          @click="initEdit(index)"
                          :disabled="addEditInProgress"
                      >
                        <v-icon small>mdi-pencil</v-icon>
                        <span
                            v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                          && item.action !== ActionTypes.ADDED"
                        >
                          Amend
                        </span>
                        <span v-else>Edit</span>
                      </v-btn>
                    </span>

                      <span class="actions-border actions__more"
                            v-if="registrationFlowType !== RegistrationFlowType.AMENDMENT
                      || (registrationFlowType === RegistrationFlowType.AMENDMENT && (!item.action ||
                      item.action === ActionTypes.ADDED)) &&
                            (registrationType !== APIRegistrationTypes.REPAIRERS_LIEN)">
                      <v-menu offset-y left nudge-bottom="4">
                        <template v-slot:activator="{ on }">
                          <v-btn
                              text
                              small
                              v-on="on"
                              color="primary"
                              class="smaller-actions actions__more-actions__btn"
                              style="padding-right: 0px !important;"
                              :disabled="addEditInProgress"
                          >
                            <v-icon>mdi-menu-down</v-icon>
                          </v-btn>
                        </template>
                        <v-list class="actions__more-actions">
                          <v-list-item @click="removeVehicle(index)">
                            <v-list-item-subtitle>
                              <v-icon small>mdi-delete</v-icon>
                              <span
                                  v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                                && item.action !== ActionTypes.ADDED"
                              >
                                Delete
                              </span>
                              <span v-else class="ml-1">Remove</span>
                            </v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </span>
                      <span
                          v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                      && ((item.action === ActionTypes.REMOVED) || (item.action === ActionTypes.EDITED))"
                          class="edit-button"
                      >
                      <v-btn
                          text
                          color="primary"
                          class="smaller-button edit-btn"
                          :id="'class-' + index + '-undo-btn'"
                          @click="undo(index)"
                          :disabled="addEditInProgress"
                      >
                        <v-icon small>mdi-undo</v-icon>
                        <span>Undo</span>
                      </v-btn>
                    </span>

                      <span class="actions-border actions__more"
                            v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                      && item.action === ActionTypes.EDITED"
                      >
                      <v-menu offset-y left nudge-bottom="4">
                        <template v-slot:activator="{ on }">
                          <v-btn
                              text
                              small
                              v-on="on"
                              color="primary"
                              class="smaller-actions actions__more-actions__btn"
                              :disabled="addEditInProgress"
                          >
                            <v-icon>mdi-menu-down</v-icon>
                          </v-btn>
                        </template>
                        <v-list class="actions__more-actions">
                          <v-list-item @click="initEdit(index)">
                            <v-list-item-subtitle>
                              <v-icon small>mdi-pencil</v-icon>
                              <span class="ml-1">Amend</span>
                            </v-list-item-subtitle>
                          </v-list-item>
                          <v-list-item @click="removeVehicle(index)">
                            <v-list-item-subtitle>
                              <v-icon small>mdi-delete</v-icon>
                              <span
                                  v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                                && item.action !== ActionTypes.ADDED"
                              >
                                Delete
                              </span>
                              <span v-else class="ml-1">Remove</span>
                            </v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </span>
                    </div>
                  </td>
                </template>
              </tr>
            </tbody>
            <tbody v-else>
              <tr class="text-center">
                <td :colspan="headers.length">No vehicle collateral added yet.</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from 'vue-demi'
import { useStore } from '@/store/store'
// local components
import { EditCollateral } from '.'
// local types/etc.
import { ActionTypes, APIVehicleTypes, RegistrationFlowType, APIRegistrationTypes } from '@/enums'
import { VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { vehicleTableHeaders, VehicleTypes } from '@/resources'
import { useVehicle } from './factories/useVehicle'
import { cloneDeep } from 'lodash'
import { storeToRefs } from 'pinia'

export default defineComponent({
  components: {
    EditCollateral
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    showInvalid: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setVehicleCollateral } = useStore()
    const {
      getVehicleCollateral,
      getRegistrationFlowType,
      getOriginalAddCollateral,
      getRegistrationType
    } = storeToRefs(useStore())
    const { hasVehicleCollateral, hasOptionalVehicleCollateral } = useVehicle(props, context)

    const registrationFlowType = getRegistrationFlowType.value
    const registrationType = getRegistrationType.value.registrationTypeAPI

    const localState = reactive({
      activeIndex: -1,
      addEditInProgress: false,
      invalidSection: false,
      showAddVehicle: false,
      showEditVehicle: [false],
      isRepairersLienAmendment: computed((): boolean => {
        return registrationFlowType === RegistrationFlowType.AMENDMENT &&
          registrationType === APIRegistrationTypes.REPAIRERS_LIEN
      }),
      isLastDelete: computed((): boolean => {
        if (localState.isRepairersLienAmendment) {
          let ctr = 0
          for (let i = 0; i < getVehicleCollateral.value.length; i++) {
            // is valid if there is at least one vehicle
            if (getVehicleCollateral.value[i].action !== ActionTypes.REMOVED) {
              ctr++
            }
          }
          if (ctr <= 1) {
            return true
          }
        }
        return false
      }),
      showErrorComponent: computed((): boolean => {
        return props.showInvalid
      }),
      containerClass: computed((): string => {
        if (registrationFlowType === RegistrationFlowType.AMENDMENT) {
          return 'px-6 py-0'
        }
        return 'pa-0'
      }),
      summaryView: props.isSummary,
      getMH: computed(function () {
        const vc = getVehicleCollateral.value as VehicleCollateralIF[]
        return vc?.find(obj => obj.type === APIVehicleTypes.MANUFACTURED_HOME)
      }),
      getNumCols: computed((): number => {
        const vc = getVehicleCollateral.value as VehicleCollateralIF[]
        if (vc?.find(obj => obj.type === APIVehicleTypes.MANUFACTURED_HOME)) {
          return 7
        }
        return 6
      }),
      headers: computed(function () {
        const vc = getVehicleCollateral.value as VehicleCollateralIF[]
        const headersToShow = [...vehicleTableHeaders]
        const editRow = headersToShow.pop()
        if (vc?.find(obj => obj.type === APIVehicleTypes.MANUFACTURED_HOME)) {
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
      }),
      vehicleCollateral: computed((): VehicleCollateralIF[] => {
        const vehicles = getVehicleCollateral.value as VehicleCollateralIF[] || []
        if ((registrationFlowType === RegistrationFlowType.AMENDMENT) && (localState.summaryView)) {
          const displayArray = []
          for (let i = 0; i < vehicles.length; i++) {
            if (vehicles[i].action) {
              displayArray.push(vehicles[i])
            }
          }
          return displayArray
        } else {
          return vehicles
        }
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    const removeVehicle = (index: number): void => {
      const newVCollateral = [...localState.vehicleCollateral]
      const currentVehicle = localState.vehicleCollateral[index]
      if (
        registrationFlowType === RegistrationFlowType.AMENDMENT &&
        currentVehicle.action !== ActionTypes.ADDED
      ) {
        currentVehicle.action = ActionTypes.REMOVED
        newVCollateral.splice(index, 1, currentVehicle)
      } else {
        // eslint-disable-line
        newVCollateral.splice(index, 1)
      }
      setVehicleCollateral(newVCollateral)
    }

    const rowClass = (action): string => {
      if (!action) {
        return ''
      }
      if (action === ActionTypes.REMOVED && !localState.summaryView) {
        return 'disabled-text-not-action'
      }
      if (action === ActionTypes.REMOVED && localState.summaryView) {
        return 'disabled-text-not-first'
      }
      return ''
    }

    const getVehicleDescription = (code: string): string => {
      const vehicle = VehicleTypes.find(obj => obj.value === code)
      return vehicle.text
    }

    const initEdit = (index: number) => {
      localState.activeIndex = index
      localState.addEditInProgress = true
      localState.showEditVehicle[index] = true
      context.emit('collateralOpen', true)
    }

    const initAdd = () => {
      localState.addEditInProgress = true
      localState.showAddVehicle = true
      context.emit('collateralOpen', true)
    }

    const resetData = () => {
      localState.activeIndex = -1
      localState.addEditInProgress = false
      localState.showAddVehicle = false
      localState.showEditVehicle = [false]
      context.emit('collateralOpen', false)
    }

    const undo = (index: number): void => {
      const newVCollateral = [...localState.vehicleCollateral]
      const originalCollateral = getOriginalAddCollateral.value
      newVCollateral.splice(index, 1, cloneDeep(originalCollateral.vehicleCollateral[index]))
      setVehicleCollateral(newVCollateral)
    }

    return {
      removeVehicle,
      initEdit,
      initAdd,
      resetData,
      getVehicleDescription,
      hasVehicleCollateral,
      hasOptionalVehicleCollateral,
      registrationFlowType,
      RegistrationFlowType,
      registrationType,
      APIRegistrationTypes,
      ActionTypes,
      undo,
      rowClass,
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

td {
  word-wrap: break-word;
}

.vehicle-cell {
  text-transform: uppercase;
}

.error-margin {
  margin-left: -25px;
}

.even-smaller
{
  padding-left: 0px !important;
  padding-right: 8px !important;
}

.box-shadow-left {
  margin-left: -23px;
  padding-left: 25px;
  box-shadow: -2px 0 0 #D3272C;
}
::v-deep .v-chip .v-chip__content {
  font-weight: 700;
}

::v-deep .primary--text.v-btn.v-btn--disabled > .v-btn__content > span {
  color: #1669bb !important;
  opacity: 0.4 !important;
}
</style>
