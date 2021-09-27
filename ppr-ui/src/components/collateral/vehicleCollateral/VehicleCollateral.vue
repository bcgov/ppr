<template>
  <v-container v-if="isSummary">
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
  </v-container>
  <v-container v-else class="pa-0" fluid no-gutters>
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
                      @removeVehicle="removeVehicle($event)"
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
import { useGetters, useActions } from 'vuex-composition-helpers'
// local components
import { EditCollateral } from '.'
// local types/etc.
import { APIVehicleTypes } from '@/enums'
import { VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { vehicleTableHeaders, VehicleTypes } from '@/resources'
import { useVehicle } from './factories/useVehicle'

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
    }
  },
  setup (props, context) {
    const { getVehicleCollateral } = useGetters<any>(['getVehicleCollateral'])
    const { setVehicleCollateral } = useActions<any>(['setVehicleCollateral'])

    const { hasVehicleCollateral } = useVehicle(props, context)

    const localState = reactive({
      activeIndex: -1,
      addEditInProgress: false,
      invalidSection: false,
      showAddVehicle: false,
      showEditVehicle: [false],
      showErrorComponent: props.showInvalid,
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
        return getVehicleCollateral.value as VehicleCollateralIF[] || []
      })
    })

    const removeVehicle = (index: number): void => {
      // FUTURE: update this to action: removed when doing ammendments
      let newVCollateral = [...localState.vehicleCollateral] // eslint-disable-line
      newVCollateral.splice(index, 1)
      setVehicleCollateral(newVCollateral)
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

    watch(() => props.showInvalid, (val: boolean) => {
      localState.showErrorComponent = val
    })

    return {
      removeVehicle,
      initEdit,
      initAdd,
      resetData,
      getVehicleDescription,
      hasVehicleCollateral,
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
