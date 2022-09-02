<template>
  <v-card flat rounded id="mhr-home-civic-address" class="mt-8 pa-8">
    <v-row no-gutters class="pt-1">
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': validate}">Civic Address</label>
      </v-col>
      <v-col cols="12" sm="10" class="mt-n1">
        <v-form ref="addressForm" name="address-form" v-model="isValidCivicAddress">
          <div class="form__row">
            <v-text-field
              autocomplete="new-password"
              :id="streetId"
              class="street-address"
              filled
              label="Street Address"
              :name="Math.random()"
              persistent-hint
              v-model="addressLocal.street"
              @keypress.once="enableAddressComplete()"
              @click="enableAddressComplete()"
            />
          </div>
          <div class="form__row">
            <v-textarea
              id="streetAdditional"
              auto-grow
              filled
              class="street-address-additional"
              label="Additional Street Address (Optional)"
              :name="Math.random()"
              rows="1"
              v-model="addressLocal.streetAdditional"
            />
          </div>
          <div class="form__row two-column">
            <v-row>
              <v-col>
                <v-text-field
                  id="city"
                  filled
                  class="item address-city"
                  label="City"
                  :name="Math.random()"
                  v-model="addressLocal.city"
                  :rules="[...addressSchema.city]"
                />
              </v-col>
              <v-col>
                <v-text-field
                  id="region"
                  label="Province"
                  class="item address-region"
                  filled
                  disabled
                  hint="Address must be in B.C."
                  persistent-hint
                  :name="Math.random()"
                  v-model="addressLocal.region"
                  :rules="[...addressSchema.region]"
                />
              </v-col>
            </v-row>
          </div>
        </v-form>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { CivicAddressSchema } from '@/schemas/civic-address'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { useMhrValidations } from '@/composables'
import {
  useAddress,
  useAddressComplete,
  useCountriesProvinces,
  useBaseValidations
} from '@/composables/address/factories'
import { AddressIF } from '@/interfaces'
/* eslint-enable no-unused-vars */
export default defineComponent({
  name: 'HomeCivicAddress',
  components: {},
  props: {
    value: {
      type: Object as () => AddressIF,
      default: () => ({
        street: '',
        streetAdditional: '',
        city: '',
        region: 'British Columbia',
        postalCode: '',
        country: '',
        deliveryInstructions: ''
      })
    },
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const {
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getMhrRegistrationValidationModel'
    ])
    const {
      setCivicAddress
    } = useActions<any>([
      'setCivicAddress'
    ])

    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const addressSchema = CivicAddressSchema

    const {
      addressLocal,
      country,
      schemaLocal,
      isSchemaRequired,
      labels
    } = useAddress(toRefs(props).value, addressSchema)

    const { enableAddressComplete, uniqueIds } = useAddressComplete(addressLocal)

    const localState = reactive({
      isValidCivicAddress: false,
      addressLocal
    })

    const validateForm = (): void => {
      if (props.validate) {
        // @ts-ignore - function exists
        localState.isValidCivicAddress = true
      }
    }

    /** Apply local model updates to store. **/
    watch(() => addressLocal.value.street, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'street', value: addressLocal.value.street })
    })

    watch(() => addressLocal.value.streetAdditional, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'streetAdditional', value: addressLocal.value.streetAdditional })
    })

    watch(() => addressLocal.value.city, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'city', value: addressLocal.value.city })
    })

    watch(() => addressLocal.value.region, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'region', value: 'BC' })
    })

    watch(() => localState.isValidCivicAddress, async (val: boolean) => {
      setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID, val)
    })

    watch(() => props.validate, async () => {
      // @ts-ignore - function exists
      addressLocal.value.region = 'British Columbia'
      validateForm()
    })
    /** Clear/reset forms when select option changes. **/
    return {
      addressSchema,
      addressLocal,
      country,
      schemaLocal,
      isSchemaRequired,
      enableAddressComplete,
      ...labels,
      ...uniqueIds,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.address-region {::v-deep .v-input__slot{
  border-bottom: thin dashed;
  color: #212529;
}}
.address-region {::v-deep input{
  color: #212529 !important;
  font-size: 16px;
}}
.address-region {::v-deep .v-label{
  color: #495057;
}}
.address-region {::v-deep .v-text-field__details{
  color: #495057;
}}
</style>
