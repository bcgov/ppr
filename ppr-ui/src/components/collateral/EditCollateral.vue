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
                        v-model="currentVehicle.type"
                        id="txt-type"
                        :error-messages="errors.type.message ? errors.type.message : ''"
                      >
                        <template slot="item" slot-scope="data">
                          <span class="list-item">
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
                      :error-messages="errors.serialNumber.message ? errors.serialNumber.message : ''"
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
                      v-model="currentVehicle.year"
                      persistent-hint
                      :error-messages="errors.year.message ? errors.year.message : ''"
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
                      @blur="validateInput('make')"
                      :error-messages="errors.make.message ? errors.make.message : ''"
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
                      persistent-hint
                      :error-messages="errors.model.message ? errors.model.message : ''"
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
                      @click="onSubmitForm()"
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
  defineComponent,
  onMounted
} from '@vue/composition-api'

import { useCollateralValidation } from './composables/useCollateralValidation'
import { useVehicle } from './composables/useVehicle'

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
    const {
      currentVehicle,
      vehicleTypes,
      getSerialLabel,
      getSerialDisabled,
      getVehicle,
      resetFormAndData,
      removeVehicle,
      addVehicle
    } = useVehicle(props, context)
    const { errors, validateInput, validateCollateralForm } = useCollateralValidation()
    onMounted(getVehicle)

    const onSubmitForm = async () => {
      const isValid = await validateCollateralForm(currentVehicle.value)
      if (!isValid) {
        // let errors = formErrors() // eslint-disable-line
        return
      }

      addVehicle()
    }

    return {
      onSubmitForm,
      resetFormAndData,
      removeVehicle,
      validateInput,
      errors,
      currentVehicle,
      vehicleTypes,
      getSerialLabel,
      getSerialDisabled
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
