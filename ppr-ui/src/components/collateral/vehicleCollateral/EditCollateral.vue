<template>
  <div id="edit-vehicle" class="white py-8" :class="{ 'border-error-left': showErrorBar }">
    <v-expand-transition>
      <v-row no-gutters :class="{ 'border-over': showErrorBar }">
        <v-col cols="3">
          <label
            class="add-vehicle-header generic-label"
            :class="{ 'error-text': invalidSection }"
          >
            <span
              v-if="activeIndex === -1"
              :class="registrationFlowType === RegistrationFlowType.AMENDMENT ? '' : 'pl-4'"
            >
              Add Vehicle
            </span>
            <span v-else class="ml-n3">
              <span v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                        && (!currentVehicle.action || currentVehicle.action !== ActionTypes.ADDED)">
                Amend
              </span>
              <span v-else>Edit</span>
               Vehicle</span>
          </label>
        </v-col>
        <v-col cols="9" :class="registrationFlowType === RegistrationFlowType.AMENDMENT ? '' : 'pr-6'">
          <v-form
            ref="vehicleForm"
            class="vehicle-form"
            v-on:submit.prevent="addVehicle"
          >
            <v-row no-gutters>
              <v-col v-if="mustHaveManufacturedHomeCollateral()">
                <v-text-field
                  filled
                  id="txt-type"
                  label="Vehicle Type"
                  value="Manufactured Home (MH)"
                  readonly
                  persistent-hint
                />
              </v-col>
              <v-col v-else-if="excludesManufacturedHomeCollateral()">
                <v-select
                  :items="vehicleTypesNoMH"
                  filled
                  label="Vehicle Type"
                  v-model="currentVehicle.type"
                  id="txt-type-drop"
                  :error-messages="
                    errors.type.message ? errors.type.message : ''
                  "
                  @change="changeVehicleType"
                >
                  <template slot="item" slot-scope="data">
                    <span class="list-item">
                      {{ data.item.text }}
                    </span>
                  </template>
                </v-select>
              </v-col>
              <v-col v-else>
                <v-select
                  :items="vehicleTypes"
                  filled
                  label="Vehicle Type"
                  v-model="currentVehicle.type"
                  id="txt-type-drop"
                  :error-messages="
                    errors.type.message ? errors.type.message : ''
                  "
                  @change="changeVehicleType"
                >
                  <template slot="item" slot-scope="data">
                    <span :id="`txt-type-drop-${data.item.text}`" class="list-item">
                      {{ data.item.text }}
                    </span>
                  </template>
                </v-select>
              </v-col>
            </v-row>
            <v-row no-gutters v-if="currentVehicle.type === 'MH'">
              <v-col>
                <v-text-field
                  filled
                  id="txt-man"
                  label="Manufactured Home Registration Number"
                  v-model="currentVehicle.manufacturedHomeRegistrationNumber"
                  :error-messages="
                    errors.manufacturedHomeRegistrationNumber.message
                      ? errors.manufacturedHomeRegistrationNumber.message
                      : ''
                  "
                  @keyup="onBlur('manufacturedHomeRegistrationNumber')"
                  persistent-hint
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  filled
                  :label="getSerialLabel"
                  :disabled="getSerialDisabled"
                  id="txt-serial"
                  v-model="currentVehicle.serialNumber"
                  :error-messages="
                    errors.serialNumber.message
                      ? errors.serialNumber.message
                      : ''
                  "
                  @keyup="onBlur('serialNumber')"
                  persistent-hint
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="4">
                <v-text-field
                  filled
                  label="Year (Optional)"
                  id="txt-years"
                  v-model="currentVehicle.year"
                  @blur="onBlur('year')"
                  hint="YYYY"
                  persistent-hint
                  :error-messages="
                    errors.year.message ? errors.year.message : ''
                  "
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  filled
                  label="Make"
                  id="txt-make"
                  v-model="currentVehicle.make"
                  persistent-hint
                  @keyup="onBlur('make')"
                  :error-messages="
                    errors.make.message ? errors.make.message : ''
                  "
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  filled
                  label="Model"
                  id="txt-model"
                  v-model="currentVehicle.model"
                  @keyup="onBlur('model')"
                  persistent-hint
                  :error-messages="
                    errors.model.message ? errors.model.message : ''
                  "
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
                    class="remove-btn"
                    id="remove-btn-collateral"
                    >
                    <span v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                              && currentIndex !== -1
                              && (!currentVehicle.action || currentVehicle.action !== ActionTypes.ADDED)">
                      Delete
                    </span>
                    <span v-else>Remove</span>
                  </v-btn>

                  <v-btn
                    large
                    id="done-btn-collateral"
                    class="ml-auto"
                    color="primary"
                    @click="onSubmitForm()"
                  >
                    Done
                  </v-btn>

                  <v-btn
                    id="cancel-btn-collateral"
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
import { defineComponent, onMounted, reactive, computed, toRefs } from '@vue/composition-api'

import { useCollateralValidation, useVehicle } from './factories'
import { APIVehicleTypes } from '@/enums'

export default defineComponent({
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    invalidSection: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  emits: ['resetEvent'],
  setup (props, context) {
    const {
      // @ts-ignore - returned by toRef
      currentVehicle,
      // @ts-ignore - returned by toRef
      vehicleTypes,
      // @ts-ignore - returned by toRef
      vehicleTypesNoMH,
      // @ts-ignore - returned by toRef
      getSerialLabel,
      // @ts-ignore - returned by toRef
      getSerialDisabled,
      // @ts-ignore - returned by toRef
      registrationFlowType,
      getVehicle,
      ActionTypes,
      RegistrationFlowType,
      resetFormAndData,
      removeVehicle,
      addVehicle,
      mustHaveManufacturedHomeCollateral,
      excludesManufacturedHomeCollateral
    } = useVehicle(props, context)
    const {
      errors,
      validateInput,
      validateSerial,
      validateCollateralForm,
      resetSerialError
    } = useCollateralValidation()

    const localState = reactive({
      currentIndex: computed((): number => {
        return props.activeIndex
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    onMounted(() => {
      getVehicle()
      if (mustHaveManufacturedHomeCollateral()) {
        // set the current vehicle type to motor home
        currentVehicle.value.type = APIVehicleTypes.MANUFACTURED_HOME
      }
    })

    const onSubmitForm = async () => {
      const isValid = await validateCollateralForm(currentVehicle.value)
      if (!isValid) {
        return
      }

      addVehicle()
    }

    const onBlur = fieldname => {
      if (fieldname === 'serialNumber') {
        validateSerial(currentVehicle.value)
      } else {
        validateInput(fieldname, currentVehicle.value[fieldname])
        // remove serial number validation if manufactured home number entered
        if (fieldname === 'manufacturedHomeRegistrationNumber') {
          validateSerial(currentVehicle.value)
        }
      }
    }

    const changeVehicleType = () => {
      resetSerialError()
    }

    return {
      onSubmitForm,
      resetFormAndData,
      removeVehicle,
      onBlur,
      errors,
      currentVehicle,
      vehicleTypes,
      vehicleTypesNoMH,
      getSerialLabel,
      getSerialDisabled,
      registrationFlowType,
      RegistrationFlowType,
      ActionTypes,
      mustHaveManufacturedHomeCollateral,
      excludesManufacturedHomeCollateral,
      changeVehicleType,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.container .v-card > .border-error-left
{
  border-top-left-radius: unset;
  border-bottom-left-radius: unset;
  margin-left: 0px;
}
.border-over
{
  margin-left: 25px;
}
</style>
