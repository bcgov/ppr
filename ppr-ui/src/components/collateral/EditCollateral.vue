<template>
  <div id="edit-vehicle" class="white pa-6">
    <v-expand-transition>
      <v-row no-gutters>
        <v-col cols="3">
            <label
              class="add-vehicle-header general-label"
              :class="{ 'error-text': invalidSection }"
            >
              <span v-if="activeIndex === -1" class="pl-5"> Add Vehicle </span>
              <span v-else>Edit Vehicle</span>
            </label>
        </v-col>
        <v-col cols="9">
              <v-form
                ref="vehicleForm"
                class="vehicle-form"
                v-on:submit.prevent="addVehicle"
              >
                <v-row no-gutters>
                    <v-col>
                      <v-select
                        :items="vehicleTypes"
                        filled
                        label="Vehicle Type"
                        v-model="type"
                        id="txt-type"
                      >
                        <template slot="item" slot-scope="data">
                          <span class="list-item">
                            {{ data.item.text }}
                          </span>
                        </template>
                      </v-select>
                    </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      :label="getSerialLabel"
                      :disabled="getSerialDisabled"
                      id="txt-serial"
                      v-model="serialNumber"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Year"
                      id="txt-years"
                      v-model="year"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      label="Make"
                      id="txt-make"
                      v-model="make"
                      persistent-hint
                      @blur="validateInput('make')"
                    />
                    <span>{{ errors.make.message }}</span>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      label="Model"
                      id="txt-model"
                      v-model="model"
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
                      @click="validateCollateralForm()"
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
        </v-col>
      </v-row>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  onMounted
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { VehicleTypes } from '@/resources'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from '@/composables/collateralFormValidator'
// import { useCollateralForm } from '@/composables/useCollateralForm'  // eslint-disable-line

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
    const { setAddCollateral } = useActions<any>(['setAddCollateral'])
    const { getAddCollateral } = useGetters<any>(['getAddCollateral'])

    let vehicleState = reactive({} as VehicleCollateralIF)

    const getVehicle = () => {
      const vehicles: VehicleCollateralIF[] = getAddCollateral.value.vehicleCollateral
      if (props.activeIndex >= 0) {
        vehicleState = vehicles[props.activeIndex]
      }
    }

    onMounted(getVehicle)

    const createEmptyErrors = () => ({
      type: createDefaultValidationResult(),
      year: createDefaultValidationResult(),
      make: createDefaultValidationResult(),
      model: createDefaultValidationResult(),
      serialNumber: createDefaultValidationResult()
    })

    // const { vehicle, errors, handleBlur, isValidForm, formErrors } = useCollateralForm(props.activeIndex)
    const localState = reactive({
      errors: createEmptyErrors(),
      vehicleTypes: VehicleTypes,
      getSerialLabel: computed(function () {
        if (vehicleState.type === '') {
          return 'Select a vehicle type first'
        } else {
          return 'Serial or VIN Number'
        }
      }),
      getSerialDisabled: computed(function () {
        if (vehicleState.type === '') {
          return true
        } else {
          return false
        }
      })
    })

    const validateCollateralForm = async () => {
      const validationResult = await formValidation.validateForm(vehicleState)
      localState.errors = { ...localState.errors, ...validationResult.fieldErrors }
      if (validationResult.succeeded) {
        let collateral = getAddCollateral.value // eslint-disable-line
        let newList: VehicleCollateralIF[] = collateral.vehicleCollateral // eslint-disable-line
        // New vehicle
        if (props.activeIndex === -1) {
          vehicleState.id = newList.length + 1
          newList.push(vehicleState)
        } else {
          // Edit vehicle
          newList.splice(props.activeIndex, 1, vehicleState)
        }
        collateral.vehicleCollateral = newList
        setAddCollateral(collateral)
        context.emit('resetEvent')
      } else {
        // let errors = formErrors() // eslint-disable-line 
      }
    }

    const validateInput = fieldName => {
      const value = event.target
      formValidation.validateField(fieldName, value)
        .then(validationResult => (localState.errors[fieldName] = validationResult))
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
      validateCollateralForm,
      resetFormAndData,
      removeVehicle,
      validateInput,
      ...toRefs(localState),
      ...toRefs(vehicleState)
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
