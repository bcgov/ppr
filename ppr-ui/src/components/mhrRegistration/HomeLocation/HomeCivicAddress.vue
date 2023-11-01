<template>
  <v-card
    id="mhr-home-civic-address"
    flat
    rounded
    class="mt-8 px-8 pt-8 pb-2"
  >
    <v-row
      no-gutters
      class="py-2"
    >
      <v-col
        cols="12"
        sm="3"
      >
        <label
          class="generic-label"
          :class="{'error-text': validate}"
        >Civic Address</label>
      </v-col>
      <v-col
        cols="12"
        sm="9"
        class="mt-n1"
      >
        <v-form
          ref="addressForm"
          v-model="isValidCivicAddress"
          name="address-form"
        >
          <div class="form__row">
            <div class="form__row">
              <v-autocomplete
                id="country"
                v-model="addressLocal.country"
                autocomplete="new-password"
                variant="filled"
                class="address-country"
                hide-no-data
                item-title="name"
                item-value="code"
                :items="getCountries(true)"
                :label="countryLabel"
                :rules="[...schemaLocal.country]"
              />
              <!-- special field to select AddressComplete country, separate from our model field -->
              <input
                :id="countryId"
                type="hidden"
                :value="country"
              >
            </div>

            <v-text-field
              :id="streetId"
              ref="street"
              v-model="addressLocal.street"
              autocomplete="new-password"
              class="street-address"
              variant="filled"
              label="Street Address (Number and Name)"
              hint="Required if location has a street address"
              persistent-hint
              :rules="[...CivicAddressSchema.street]"
              @keypress.once="enableAddressComplete()"
              @click="enableAddressComplete()"
            />
          </div>
          <div class="form__row two-column">
            <v-row>
              <v-col>
                <v-text-field
                  id="city"
                  ref="city"
                  v-model="addressLocal.city"
                  variant="filled"
                  class="item address-city"
                  label="City"
                  :rules="[...CivicAddressSchema.city]"
                />
              </v-col>
              <v-col>
                <v-select
                  id="region"
                  v-model="addressLocal.region"
                  :label="provinceStateLabel"
                  class="item address-region"
                  autocomplete="off"
                  variant="filled"
                  persistent-hint
                  :items="provinceOptions"
                  item-title="name"
                  item-value="value"
                  :rules="[...CivicAddressSchema.region]"
                >
                  <template #item="{item, props}">
                    <v-divider v-if="item.value === 'divider'" />
                    <v-list-item
                      v-else
                      v-bind="props"
                    />
                  </template>
                </v-select>
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
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { CivicAddressSchema } from '@/schemas/civic-address'
import { useStore } from '@/store/store'
import { useMhrValidations } from '@/composables'
import {
  useAddress,
  useAddressComplete,
  useCountriesProvinces
} from '@/composables/address/factories'
import { AddressIF, FormIF } from '@/interfaces'
import { storeToRefs } from 'pinia'
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
        region: '',
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
    const { setCivicAddress } = useStore()
    const { getMhrRegistrationValidationModel } = storeToRefs(useStore())
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
    const addressForm = ref(null) as FormIF

    const localState = reactive({
      isValidCivicAddress: false,
      provinceStateLabel: computed((): string => {
        switch (addressLocal.value.country) {
          case 'CA':
            return 'Province'
          case 'US':
            return 'State'
          default:
            return 'Province/State'
        }
      }),
      provinceOptions: computed((): Array<Object> => {
        return countryProvincesHelpers.getCountryRegions(addressLocal.value.country, true).map((region: any) => {
          return {
            name: region.name,
            value: region.short
          }
        })
      })
    })

    const validateForm = (): void => {
      if (props.validate) {
        addressForm.value?.validate()
      }
    }

    /** Apply local model updates to store. **/
    watch(() => addressLocal.value.country, async (country: string) => {
      // Clear fields when country changes
      addressLocal.value.street = ''
      addressLocal.value.city = ''
      addressLocal.value.region = ''

      await setCivicAddress({ key: 'country', value: country })
    })

    watch(() => addressLocal.value.street, async (street: string) => {
      await setCivicAddress({ key: 'street', value: street })
    })

    watch(() => addressLocal.value.city, async (city: string) => {
      await setCivicAddress({ key: 'city', value: city })
    })

    watch(() => addressLocal.value.region, async (region: string) => {
      await setCivicAddress({ key: 'region', value: region })
    })

    watch(() => localState.isValidCivicAddress, async (val: boolean) => {
      setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID, val)
    })

    watch(() => props.validate, () => {
      validateForm()
    })
    /** Clear/reset forms when select option changes. **/
    return {
      addressForm,
      CivicAddressSchema,
      addressLocal,
      country,
      schemaLocal,
      isSchemaRequired,
      enableAddressComplete,
      ...labels,
      ...uniqueIds,
      ...countryProvincesHelpers,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.address-region {:deep(.v-label) {
  color: #495057;
}}
:deep() {
  .theme--light.v-select .v-select__selection--comma {
    color: $gray9;
  }
  .v-text-field.v-text-field--enclosed .v-text-field__details {
    margin-bottom: 0;
  }
  .v-list .v-list-item--active {
    background-color: $blueSelected!important;
  }
}
</style>
