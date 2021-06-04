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
                     <label class="general-label">Business Legal Name</label>
                    </v-col>
                </v-row>
                <v-row v-else no-gutters>
                    <v-col>
                     <label class="general-label">Individual Name</label>
                    </v-col>
                </v-row>
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
                    <v-col cols="4" class="pr-4">
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
                  <v-col cols="4" class="pr-4">
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
                <v-row v-if="!isBusiness" no-gutters>
                    <v-col>
                     <label class="general-label">Birthdate</label>
                    </v-col>
                </v-row>
                <v-row v-if="!isBusiness" no-gutters>
                   <v-col cols="4" class="pr-4">
                     <v-autocomplete
                        auto-select-first
                        :items="months"
                        filled
                      label="Month"
                      item-text="name"
                      item-value="id"
                      id="txt-first"
                      v-model="month"
                      persistent-hint
                      ></v-autocomplete>

                  </v-col>
                  <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="Day"
                      id="txt-middle"
                      v-model="day"
                      persistent-hint
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Year"
                      id="txt-last"
                      v-model="year"
                      persistent-hint
                     />
                  </v-col>
                </v-row>
                <v-row no-gutters>
                    <v-col>
                      <label class="general-label">Address</label>
                    </v-col>
                </v-row>
                <base-address ref="regMailingAddress"
                    id="address-debtor"
                    :address="currentDebtor.address"
                    :editing="true"
                    :schema="addressSchema"
                    @update:address="updateAddress($event)"
                    @valid="updateValidity(AddressTypes.MAILING_ADDRESS, $event)"
                  />

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
import BaseAddress from 'sbc-common-components/src/components/BaseAddress.vue'
import { useDebtorValidation } from './composables/useDebtorValidation'
import { useDebtor } from './composables/useDebtor'

export default defineComponent({
  components: {
    BaseAddress
  },
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
      year,
      month,
      day,
      months,
      countries,
      provinces,
      getDebtor,
      resetFormAndData,
      removeDebtor,
      addDebtor,
      addressSchema
    } = useDebtor(props, context)
    const { errors, updateValidity } = useDebtorValidation()

    onMounted(getDebtor)

    const onBlur = (fieldname) => {
    }

    const onSubmitForm = async () => {
      // const isValid = await validateCollateralForm(currentVehicle.value)
      // if (!isValid) {
      //  return
      // }

      addDebtor()
    }

    return {
      currentDebtor,
      year,
      month,
      day,
      months,
      countries,
      provinces,
      resetFormAndData,
      removeDebtor,
      onSubmitForm,
      onBlur,
      addressSchema,
      updateValidity,
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
