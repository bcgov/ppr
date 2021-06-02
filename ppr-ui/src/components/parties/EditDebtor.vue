<template>
  <div id="edit-debtor" class="white pa-6">
    <v-expand-transition>
      <v-row no-gutters>
        <v-col cols="3">
            <label
              class="add-debtor-header general-label"
              :class="{ 'error-text': invalidSection }"
            >
              <span v-if="activeIndex === -1" class="pl-5">Add</span>
              <span v-else>Edit</span>
              <span v-if="isBusiness"> Business</span>
              <span v-else> Individual Debtor</span>
            </label>
        </v-col>
        <v-col cols="9">
              <v-form
                ref="debtorForm"
                class="debtor-form"
                v-on:submit.prevent="addDebtor"
              >
                <v-row v-if="isBusiness" no-gutters>
                    <v-col>
                     <v-text-field
                      filled
                      id="txt-nane"
                      label="Business Legal Name"
                      v-model="currentDebtor.businessName"
                      :error-messages="errors.businessName.message ?
                      errors.businessName.message : ''"
                      persistent-hint
                    />
                    </v-col>
                </v-row>
                <v-row v-else no-gutters>
                    <v-col cols="4">
                    <v-text-field
                      filled
                      label="First Name"
                      id="txt-first"
                      v-model="currentDebtor.personName.first"
                      persistent-hint
                      @blur="onBlur('first')"
                      :error-messages="errors.first.message ? errors.first.message : ''"
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Middle Name (Optional)"
                      id="txt-middle"
                      v-model="currentDebtor.personName.middle"
                      persistent-hint
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Last Name"
                      id="txt-last"
                      v-model="currentDebtor.personName.last"
                      persistent-hint
                      @blur="onBlur('last')"
                      :error-messages="errors.last.message ? errors.last.message : ''"
                    />
                  </v-col>
                </v-row>

                <v-row no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      id="txt-street"
                      v-model="currentDebtor.address.street"
                      :error-messages="errors.street.message ? errors.street.message : ''"
                      @blur="onBlur('street')"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      label="Year"
                      id="txt-street-additional"
                      v-model="currentDebtor.address.streetAdditional"
                      @blur="onBlur('streetAdditional')"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="City"
                      id="txt-city"
                      v-model="currentDebtor.address.city"
                      persistent-hint
                      @blur="onBlur('city')"
                      :error-messages="errors.city.message ? errors.city.message : ''"
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Province"
                      id="txt-province"
                      v-model="currentDebtor.address.region"
                      persistent-hint
                      @blur="onBlur('region')"
                      :error-messages="errors.region.message ? errors.region.message : ''"
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Postal Code"
                      id="txt-postal-code"
                      v-model="currentDebtor.address.postalCode"
                      persistent-hint
                      @blur="onBlur('postalCode')"
                      :error-messages="errors.postalCode.message ? errors.postalCode.message : ''"
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
                      @click="removeDebtor()"
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

import { useDebtorValidation } from './composables/useDebtorValidation'
import { useDebtor } from './composables/useDebtor'

export default defineComponent({
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    isBusiness: {
      type: Boolean,
      default: true
    },
    invalidSection: {
      type: Boolean,
      default: false
    }
  },
  emits: ['addEditDebtor', 'resetEvent'],
  setup (props, context) {
    const {
      // @ts-ignore - returned by toRef
      currentDebtor,
      getDebtor,
      resetFormAndData,
      removeDebtor,
      addDebtor
    } = useDebtor(props, context)
    const { errors } = useDebtorValidation()

    onMounted(getDebtor)

    const onSubmitForm = async () => {
      // const isValid = await validateCollateralForm(currentVehicle.value)
      // if (!isValid) {
      //  return
      // }

      addDebtor()
    }

    return {
      currentDebtor,
      resetFormAndData,
      removeDebtor,
      onSubmitForm,
      errors
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
