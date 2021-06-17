<template>
  <v-container fluid no-gutters class="white pa-0" v-if="summaryView">
    <v-card flat id="collateral-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="#38598A">mdi-car</v-icon>
          <label class="pl-3"><strong>Collateral</strong></label>
        </v-col>
      </v-row>
      <v-container
        v-if="showErrorSummary"
        :class="{ 'invalid-message': showErrorSummary }"
      >
        <v-row no-gutters class="pa-6">
          <v-col cols="auto">
            <v-icon color="#D3272C">mdi-information-outline</v-icon>
            <span class="invalid-message">This step is unfinished.</span>
            <router-link
              id="router-link-collateral"
              class="invalid-link"
              :to="{ path: '/add-collateral' }"
            >
              Return to this step to complete it.
            </router-link>
          </v-col>
        </v-row>
      </v-container>
      <v-container v-else>
        <v-row no-gutters class="ps-6 pb-3">
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
                <tr :key="row.item.id" class="vehicle-row">
                  <td :class="[$style['summary-cell']]">
                    {{ getVehicleDescription(row.item.type) }}
                  </td>
                  <td>{{ row.item.year }}</td>
                  <td>{{ row.item.make }}</td>
                  <td>{{ row.item.model }}</td>
                  <td>{{ row.item.serialNumber }}</td>
                  <td v-if="getMH">
                    {{ row.item.manufacturedHomeRegistrationNumber }}
                  </td>
                </tr>
              </template>
            </v-data-table>
          </v-col>
        </v-row>
        <v-row no-gutters class="ps-6 pb-3">
          <v-col cols="3" class="generic-label">
            General Collateral
          </v-col>
          <v-col :class="[$style['summary-text'], 'pa-6']">
            {{ generalCollateral }}
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
        <ul>
          <li>At least one form of collateral (vehicle or general)</li>
        </ul>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-4 pt-10">
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
    <v-row no-gutters>
      <v-col>
        <div :class="{ 'invalid-section': invalidSection }">
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
    <v-row no-gutters class="pt-4">
      <v-col>
        <v-data-table
          class="collateral-table"
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
              <td class="list-item__title">
                {{ getVehicleDescription(row.item.type) }}
              </td>
              <td>
                {{ row.item.year }}
              </td>
              <td>{{ row.item.make }}</td>
              <td>{{ row.item.model }}</td>
              <td>{{ row.item.serialNumber }}</td>
              <td v-if="getMH">
                {{ row.item.manufacturedHomeRegistrationNumber }}
              </td>

              <!-- Action Btns -->
              <td class="actions-cell pa-0">
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
              <td colspan="6" :class="{ 'invalid-section': invalidSection }">
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
    <v-row class="pt-8">
      <v-col>
        <v-card flat id="general-collateral">
          <v-container fluid no-gutters class="pa-0">
            <v-row no-gutters class="py-6">
              <v-col cols="3" class="generic-label pa-4">
                General Collateral
              </v-col>
              <v-col cols="9" class="pr-4">
                <v-textarea
                  v-model="generalCollateral"
                  id="generalCollateral"
                  auto-grow
                  counter="4000"
                  filled
                  label="Description of General Collateral"
                  class="white pt-2 text-input-field"
                  @blur="validateGeneral()"
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
  computed
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { AddCollateralIF, VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import EditCollateral from './EditCollateral.vue'
import { vehicleTableHeaders, VehicleTypes } from '@/resources'

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
  setup (props, { emit }) {
    const { setAddCollateral } = useActions<any>(['setAddCollateral'])
    const { getAddCollateral } = useGetters<any>(['getAddCollateral'])

    const collateral: AddCollateralIF = getAddCollateral.value

    const localState = reactive({
      summaryView: props.isSummary,
      showAddVehicle: false,
      addEditInProgress: false,
      invalidSection: false,
      activeIndex: -1,
      showEditVehicle: [false],
      generalCollateralError: '',
      vehicleCollateral: collateral.vehicleCollateral,
      generalCollateral: collateral.generalCollateral,
      showErrorSummary: computed((): boolean => {
        return !collateral.valid
      }),
      getMH: computed(function () {
        return collateral.vehicleCollateral.find(obj => obj.type === 'MH')
      }),
      headers: computed(function () {
        const headersToShow = [...vehicleTableHeaders]
        const editRow = headersToShow.pop()
        if (collateral.vehicleCollateral.find(obj => obj.type === 'MH')) {
          headersToShow.push({
            class: 'column-mds',
            sortable: false,
            text: 'MH Number',
            value: 'vehicle.manufacturedHomeRegistrationNumber'
          })
        }
        if (!props.isSummary) {
          headersToShow.push(editRow)
        }
        return headersToShow
      })
    })

    watch(
      () => localState.generalCollateral,
      (val: string) => {
        collateral.generalCollateral = val
        setAddCollateral(collateral)
        setValid()
      }
    )

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
    }

    const validateGeneral = () => {
      if (collateral.generalCollateral.length > 4000) {
        collateral.valid = false
        localState.generalCollateralError = 'Maximum 4000 characters'
      }
    }

    const setValid = () => {
      if (
        (collateral.generalCollateral ||
          collateral.vehicleCollateral.length > 0) &&
        collateral.generalCollateral.length <= 4000
      ) {
        collateral.valid = true
      } else {
        collateral.valid = false
      }
      setAddCollateral(collateral)
    }

    return {
      removeVehicle,
      initEdit,
      initAdd,
      resetData,
      getVehicleDescription,
      validateGeneral,
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
</style>
