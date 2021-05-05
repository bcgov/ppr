<template>
  <div id="edit-vehicle" class="white pa-6">
    <v-expand-transition>
      <ul class="list add-vehicle">
        <li class="add-vehicle-container">
          <div class="meta-container">
            <label
              class="add-vehicle-header"
              :class="{ 'error-text': invalidSection }"
            >
              <span v-if="activeIndex === -1" class="pl-5"> Add Vehicle </span>
              <span v-else>Edit Vehicle</span>
            </label>

            <div class="meta-container__inner">
              <v-form
                ref="vehicleForm"
                class="vehicle-form"
                v-on:submit.prevent="addVehicle"
              >
                <v-row>
                  <v-col>
                    <v-text-field
                      filled
                      label="Serial / VIN / DOT/ MH Number"
                      hint="17 characters; no letters O,Q or "
                      id="txt-serial"
                      v-model="vehicle.serialNumber"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="8">
                    <v-select
                      :items="vehicleTypes"
                      filled
                      label="Vehicle Type"
                      v-model="vehicle.type"
                      id="txt-type"
                    >
                      <template slot="item" slot-scope="data">
                        <span class="list-item">
                          {{ data.item.text }}
                        </span>
                      </template>
                    </v-select>
                  </v-col>
                  <v-col cols="4">
                    <v-select
                      :items="getYears"
                      filled
                      label="Year"
                      v-model="vehicle.year"
                      id="txt-years"
                    >
                    </v-select>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col>
                    <v-text-field
                      filled
                      label="Make"
                      id="txt-make"
                      v-model="vehicle.make"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col>
                    <v-text-field
                      filled
                      label="Model"
                      id="txt-model"
                      v-model="vehicle.model"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col>
                  <div class="form__row form__btns">
                    <v-btn
                      large
                      outlined
                      color="error"
                      :disabled="activeIndex === -1"
                      @click="removeVehicle()"
                      id="remove-btn"
                      >Remove
                    </v-btn>

                    <v-btn
                      large
                      id="done-btn"
                      class="m1-auto"
                      color="primary"
                      @click="validateForm()"
                    >
                      Done
                    </v-btn>

                    <v-btn
                      id="cancel-btn"
                      large
                      outlined
                      color="primary"
                      @click="resetFormAndData(true)"
                    >
                      Cancel
                    </v-btn>
                  </div>
                  </v-col>
                </v-row>
              </v-form>
            </div>
          </div>
        </li>
      </ul>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { VehicleTypes } from '@/resources'

export default defineComponent({
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    invalidSection: {
      type: Boolean,
      default: false
    }
  },
  emits: ['addEditVehicle', 'resetEvent'],
  setup (props, context) {
    console.log(props.activeIndex)
    const { setAddCollateral } = useActions<any>(['setAddCollateral'])
    const { getAddCollateral } = useGetters<any>(['getAddCollateral'])

    const localState = reactive({
      // eslint-disable-line
      vehicleTypes: VehicleTypes,
      vehicle: computed(() => {
        const vehicles: VehicleCollateralIF[] = getAddCollateral.value.vehicleCollateral
        if (props.activeIndex >= 0) {
          return vehicles[props.activeIndex]
        }
        return { id: -1, type: '', year: 2021, make: '', model: '', serialNumber: '' }
      })
    })
    const getYears = computed(function () {
      const year = new Date().getFullYear()
      return Array.from(
        { length: year - 1900 },
        (value, index) => 1901 + index
      ).reverse()
    })

    const validateForm = () => {
      let collateral = getAddCollateral.value // eslint-disable-line
      let newList: VehicleCollateralIF[] = collateral.vehicleCollateral // eslint-disable-line
      // New vehicle
      if (props.activeIndex === -1) {
        localState.vehicle.id = newList.length + 1
        newList.push(localState.vehicle)
      } else {
        // Edit vehicle
        newList.splice(props.activeIndex, 1, localState.vehicle)
      }
      collateral.vehicleCollateral = newList
      setAddCollateral(collateral)
      context.emit('resetEvent')
    }

    const resetFormAndData = (emitEvent: boolean): void => {
      if (emitEvent) {
        context.emit('resetEvent')
      }
    }
    const removeVehicle = (): void => {
      context.emit('removeVehicle', props.activeIndex)
      resetFormAndData(true)
    }

    return {
      getYears,
      validateForm,
      resetFormAndData,
      removeVehicle,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import "@/assets/styles/theme.scss";
::v-deep .theme--light.v-btn.v-btn--disabled {
  color: rgba(211, 39, 44, .4) !important;
}
</style>
