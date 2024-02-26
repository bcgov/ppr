<template>
  <v-card
    id="mhr-home-civic-address"
    flat
    rounded
    class="mt-8 px-8 pt-8 pb-2"
  >
    <v-row
      noGutters
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
        <UpdatedBadge
          v-if="updatedBadge"
          :action="updatedBadge.action"
          :baseline="updatedBadge.baseline"
          :currentState="updatedBadge.currentState"
        />
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
                hideNoData
                itemTitle="name"
                itemValue="code"
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
              class="street-address mt-3"
              variant="filled"
              color="primary"
              label="Street Address (Number and Name)"
              persistentHint
              :rules="[...schema.street]"
              @keypress.once="enableAddressComplete()"
              @click="enableAddressComplete()"
            />
          </div>
          <div class="form__row two-column mt-3">
            <v-row>
              <v-col>
                <v-text-field
                  id="city"
                  ref="city"
                  v-model="addressLocal.city"
                  variant="filled"
                  color="primary"
                  class="item address-city"
                  label="City"
                  :rules="[...schema.city]"
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
                  color="primary"
                  persistentHint
                  :items="provinceOptions"
                  itemTitle="name"
                  itemValue="value"
                  :rules="[...schema.region]"
                >
                  <template #item="{item, props}">
                    <v-divider v-if="item.value === 'divider'" />
                    <v-list-item
                      v-else
                      v-bind="props"
                    />
                  </template>
                  <template #no-data>
                    <v-list-item>
                      <p>Select a country first</p>
                    </v-list-item>
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
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import {
  useAddress,
  useAddressComplete,
  useCountriesProvinces
} from '@/composables/address/factories'
import { AddressIF, FormIF, UpdatedBadgeIF } from '@/interfaces'
import { SchemaIF } from '@/composables/address/interfaces'
import { UpdatedBadge } from '@/components/common'

export default defineComponent({
  name: 'HomeCivicAddress',
  components: {
    UpdatedBadge
  },
  props: {
    value: {
      type: Object as () => AddressIF,
      default: () => ({
        street: '',
        city: '',
        region: null,
        postalCode: '',
        country: null,
        deliveryInstructions: ''
      })
    },
    schema: {
      type: Object as () => SchemaIF,
      default: null
    },
    validate: {
      type: Boolean,
      default: false
    },
    updatedBadge: {
      type: Object as () => UpdatedBadgeIF,
      default: () => null
    }
  },
  emits: ['setStoreProperty', 'isValid'],
  setup (props, { emit }) {
    const countryProvincesHelpers = useCountriesProvinces()
    const {
      addressLocal,
      country,
      schemaLocal,
      isSchemaRequired,
      labels
    } = useAddress(toRefs(props).value, props.schema)
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
      provinceOptions: computed((): Array<object> => {
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

      emit('setStoreProperty', { key: 'country', value: country })
    })

    watch(() => addressLocal.value.street, async (street: string) => {
      emit('setStoreProperty', { key: 'street', value: street })
    })

    watch(() => addressLocal.value.city, async (city: string) => {
      emit('setStoreProperty', { key: 'city', value: city })
    })

    watch(() => addressLocal.value.region, async (region: string) => {
      emit('setStoreProperty', { key: 'region', value: region })
    })

    watch(() => localState.isValidCivicAddress, async (val: boolean) => {
      emit('isValid', val)
    })

    watch(() => props.validate, () => {
      validateForm()
    })

    return {
      addressForm,
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

:deep(.theme--light.v-select .v-select__selection--comma) {
  color: $gray9;
}
:deep(.v-text-field.v-text-field--enclosed .v-text-field__details) {
  margin-bottom: 0;
}
</style>
