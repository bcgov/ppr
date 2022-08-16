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
              id="street"
              class="street-address"
              filled
              label="Street Address"
              :name="Math.random()"
              persistent-hint
              v-model="address.street"
              :rules="[...addressSchema.street]"
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
              v-model="address.streetAdditional"
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
                  v-model="address.city"
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
                  v-model="address.region"
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
/* eslint-enable no-unused-vars */
export default defineComponent({
  name: 'HomeCivicAddress',
  components: {},
  props: {
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

    const localState = reactive({
      isValidCivicAddress: false,
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: 'British Columbia'
      }
    })

    /** Apply local model updates to store. **/
    watch(() => localState.address.street, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'street', value: localState.address.street })
    })

    watch(() => localState.address.streetAdditional, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'streetAdditional', value: localState.address.streetAdditional })
    })

    watch(() => localState.address.city, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'city', value: localState.address.city })
    })

    watch(() => localState.address.region, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'region', value: localState.address.region })
    })

    watch(() => localState.isValidCivicAddress, async (val: boolean) => {
      setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID, val)
    })

    watch(() => props.validate, async () => {
      // @ts-ignore - function exists
      context.refs.addressForm.validate()
    })

    /** Clear/reset forms when select option changes. **/
    return { addressSchema, ...toRefs(localState) }
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
