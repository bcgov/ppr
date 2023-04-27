<template>
  <v-card flat rounded id="mhr-home-civic-address" class="mt-8 px-8 pt-8 pb-2">
    <v-row no-gutters class="py-2">
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
              label="Street Address (Number and Name)"
              :name="Math.random()"
              hint="Required if location has a street address"
              persistent-hint
              ref="street"
              v-model="addressLocal.street"
              @keypress.once="enableAddressComplete()"
              @click="enableAddressComplete()"
              :rules="[...CivicAddressSchema.street]"
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
                  ref="city"
                  :name="Math.random()"
                  v-model="addressLocal.city"
                  :rules="[...CivicAddressSchema.city]"
                />
              </v-col>
              <v-col>
                <v-select
                  id="region"
                  label="Province"
                  class="item address-region"
                  autocomplete="off"
                  filled
                  hint="Address must be in B.C."
                  persistent-hint
                  :items="provinceOptions"
                  item-text="name"
                  item-value="value"
                  v-model="addressLocal.region"
                  :rules="[...CivicAddressSchema.region]"
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
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { CivicAddressSchema } from '@/schemas/civic-address'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { useMhrValidations } from '@/composables'
import {
  useAddress,
  useAddressComplete,
  useCountriesProvinces
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
        city: '',
        region: 'BC',
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

    const countryProvincesHelpers = useCountriesProvinces()

    const {
      addressLocal,
      country,
      schemaLocal,
      isSchemaRequired,
      labels
    } = useAddress(toRefs(props).value, CivicAddressSchema)

    const { enableAddressComplete, uniqueIds } = useAddressComplete(addressLocal)

    const localState = reactive({
      isValidCivicAddress: false,
      provinceOptions: computed((): Array<Object> => {
        return countryProvincesHelpers.getCountryRegions('CA', true).map((region: any) => {
          return {
            name: region.name,
            value: region.short
          }
        })
      })
    })

    const validateForm = (context): void => {
      if (props.validate) {
        // @ts-ignore - function exists
        context.refs.addressForm.validate()
      }
    }

    /** Apply local model updates to store. **/
    watch(() => addressLocal.value.street, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'street', value: addressLocal.value.street })
    })

    watch(() => addressLocal.value.city, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'city', value: addressLocal.value.city })
    })

    watch(() => addressLocal.value.region, async () => {
      // Set civic address data to store
      await setCivicAddress({ key: 'region', value: addressLocal.value.region })
    })

    watch(() => localState.isValidCivicAddress, async (val: boolean) => {
      setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID, val)
    })

    watch(() => props.validate, async () => {
      // @ts-ignore - function exists
      validateForm(context)
    })
    /** Clear/reset forms when select option changes. **/
    return {
      CivicAddressSchema,
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
.address-region {::v-deep .v-label{
  color: #495057;
}}
::v-deep {
  .theme--light.v-select .v-select__selection--comma {
    color: $gray9;
  }
  .v-text-field.v-text-field--enclosed .v-text-field__details {
    margin-bottom: 0;
  }
}
</style>
