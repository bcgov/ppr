<template>
  <div class="base-address">
    <!-- Display fields -->
    <v-expand-transition>
      <div v-if="!editing" class="address-block">
        <div class="address-block__info pre-wrap">
          <div class="address-block__info-row">{{ addressLocal.street }}</div>
          <div v-if="addressLocal.streetAdditional" class="address-block__info-row">
            {{ addressLocal.streetAdditional }}
          </div>
          <div class="address-block__info-row">
            <span>{{ addressLocal.city }}</span>
            <span v-if="addressLocal.region">&nbsp;{{ addressLocal.region }}&nbsp;</span>
            <span v-if="addressLocal.postalCode">&nbsp;{{ addressLocal.postalCode }}</span>
          </div>
          <div class="address-block__info-row">{{ getCountryName(country) }}</div>
          <div v-if="addressLocal.deliveryInstructions"
          class="address-block__info-row delivery-text"
          >{{ addressLocal.deliveryInstructions }}
          </div>
        </div>
      </div>
    </v-expand-transition>

    <!-- Edit fields -->
    <v-expand-transition>
      <v-form v-if="editing" ref="addressForm" name="address-form" lazy-validation>
        <div class="form__row">
          <v-autocomplete
            autocomplete="new-password"
            :name="Math.random()"
            filled
            class="address-country"
            hide-no-data
            item-text="name"
            item-value="code"
            :items="getCountries()"
            :label="countryLabel"
            :rules="[...schemaLocal.country]"
            v-model="addressLocal.country"
          />
          <!-- special field to select AddressComplete country, separate from our model field -->
          <input type="hidden" :id="countryId" :value="country" />
        </div>
        <div class="form__row">
          <!-- NB1: AddressComplete needs to be enabled each time user clicks in this search field.
               NB2: Only process first keypress -- assumes if user moves between instances of this
                   component then they are using the mouse (and thus, clicking). -->
          <v-text-field
            autocomplete="new-password"
            class="street-address"
            filled
            :hint="hideAddressHint ? '' :  'Street address, PO box, rural route, or general delivery address'"
            :id="streetId"
            :label="streetLabel"
            :name="Math.random()"
            persistent-hint
            :rules="[...schemaLocal.street]"
            v-model="addressLocal.street"
            @keypress.once="enableAddressComplete()"
            @click="enableAddressComplete()"
          />
        </div>
        <div class="form__row">
          <v-textarea
            autocomplete="new-password"
            auto-grow
            filled
            class="street-address-additional"
            :label="streetAdditionalLabel"
            :name="Math.random()"
            rows="1"
            v-model="addressLocal.streetAdditional"
            :rules="!!addressLocal.streetAdditional ? [...schemaLocal.streetAdditional] : []"
          />
        </div>
        <div class="form__row three-column">
          <v-text-field
            autocomplete="new-password"
            filled
            class="item address-city"
            :label="cityLabel"
            :name="Math.random()"
            v-model="addressLocal.city"
            :rules="[...schemaLocal.city]"
          />
          <v-autocomplete v-if="useCountryRegions(country)"
            autocomplete="new-password"
            filled
            class="item address-region"
            hide-no-data
            item-text="name"
            item-value="short"
            :items="getCountryRegions(country)"
            :label="regionLabel"
            :menu-props="{ maxHeight: '14rem' }"
            :name="Math.random()"
            :rules="[...schemaLocal.region]"
            v-model="addressLocal.region"
          />
          <v-text-field v-else
            filled
            class="item address-region"
            :label="regionLabel"
            :name="Math.random()"
            v-model="addressLocal.region"
            :rules="[...schemaLocal.region]"
          />
          <v-text-field
            filled
            class="item postal-code"
            :label="postalCodeLabel"
            :name="Math.random()"
            v-model="addressLocal.postalCode"
            :rules="[...schemaLocal.postalCode]"
          />
        </div>
        <div class="form__row">
          <v-textarea
            auto-grow
            filled
            class="delivery-instructions"
            :label="deliveryInstructionsLabel"
            :name="Math.random()"
            rows="2"
            v-model="addressLocal.deliveryInstructions"
            :rules="!!addressLocal.deliveryInstructions ? [...schemaLocal.deliveryInstructions] : []"
          />
        </div>
      </v-form>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, toRefs, watch } from '@vue/composition-api'

import {
  baseRules,
  useAddress,
  useAddressComplete,
  useCountryRegions,
  useCountriesProvinces,
  useBaseValidations,
  spaceRules
} from '@/composables/address/factories'
import { AddressIF, SchemaIF } from '@/composables/address/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'base-address',
  props: {
    value: {
      type: Object as () => AddressIF,
      default: () => ({
        street: '',
        streetAdditional: '',
        city: '',
        region: '',
        postalCode: '',
        country: '',
        deliveryInstructions: ''
      })
    },
    /* used for readonly mode vs edit mode */
    editing: {
      type: Boolean,
      default: false
    },
    /* contains validation for each field */
    schema: {
      type: Object as () => SchemaIF,
      default: null
    },
    /* triggers all current form validation errors */
    triggerErrors: {
      type: Boolean,
      default: false
    },
    /* Hides the persistent hint field on Address Input */
    hideAddressHint: {
      type: Boolean,
      default: false
    }
  },
  emits: ['valid'],
  setup (props, { emit }) {
    const {
      addressLocal,
      country,
      schemaLocal,
      isSchemaRequired,
      labels
    } = useAddress(toRefs(props).value, props.schema)

    const origPostalCodeRules = schemaLocal.value.postalCode
    const origRegionRules = schemaLocal.value.region

    const { addressForm, resetValidation, validate } = useBaseValidations()

    const { enableAddressComplete, uniqueIds } = useAddressComplete(addressLocal)

    const countryProvincesHelpers = useCountriesProvinces()

    const countryChangeHandler = (val: string, oldVal: string) => {
      // do not trigger any changes if it is view only (summary instance)
      if (!props.editing) return

      if (val === 'CA') {
        schemaLocal.value.postalCode = origPostalCodeRules.concat([baseRules.postalCode])
        schemaLocal.value.region = origRegionRules
      } else if (val === 'US') {
        schemaLocal.value.postalCode = origPostalCodeRules.concat([baseRules.zipCode])
        schemaLocal.value.region = origRegionRules
      } else {
        schemaLocal.value.postalCode = origPostalCodeRules.concat([baseRules.maxLength(15)])
        schemaLocal.value.region = [baseRules.maxLength(2), ...spaceRules]
      }
      // reset other address fields (check is for loading an existing address)
      if (oldVal) {
        addressLocal.value.street = ''
        addressLocal.value.streetAdditional = ''
        addressLocal.value.city = ''
        addressLocal.value.region = ''
        addressLocal.value.postalCode = ''
      }
      !props.triggerErrors && resetValidation()
    }

    onMounted(() => {
      countryChangeHandler(addressLocal.value.country, null)
    })

    watch(() => addressLocal.value, (val) => {
      let valid = true
      /** checks each field against the schema rules to see if the address is valid or not
       * NOTE: we don't want it to trigger error msgs yet which is why this does not call validate()
      */
      for (const key in val) {
        for (const index in schemaLocal.value[key]) {
          if (schemaLocal.value[key][index](val[key]) !== true) {
            valid = false
            break
          }
        }
        if (!valid) break
      }
      emit('valid', valid)
    }, { immediate: true, deep: true })

    watch(() => country.value, (val, oldVal) => {
      countryChangeHandler(val, oldVal)
    })

    watch(() => props.triggerErrors, () => {
      validate()
    })

    return {
      addressForm,
      addressLocal,
      country,
      ...countryProvincesHelpers,
      enableAddressComplete,
      isSchemaRequired,
      ...labels,
      schemaLocal,
      useCountryRegions,
      ...uniqueIds,
      validate
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.delivery-text {
  font-style: italic;
  margin-top: 10px;
}

// Address Block Layout
.address-block {
  display: flex;
}

.address-block__info {
  flex: 1 1 auto;
}

// Form Row Elements
.form__row.three-column {
  align-items: stretch;
  display: flex;
  flex-flow: row nowrap;
  margin-left: -0.5rem;
  margin-right: -0.5rem;

  .item {
    flex: 1 1 auto;
    flex-basis: 0;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
  }
}

.pre-wrap {
  white-space: pre-wrap;
}

// make 'readonly' inputs looks disabled
// (can't use 'disabled' because we want normal error styling)
.v-select.v-input--is-readonly,
.v-text-field.v-input--is-readonly {
  pointer-events: none;

  ::v-deep .v-label {
    // set label colour to same as disabled
    color: rgba(0,0,0,.38);
  }

  ::v-deep .v-select__selection {
    // set selection colour to same as disabled
    color: rgba(0,0,0,.38);
  }

  ::v-deep .v-icon {
    // set error icon colour to same as disabled
    color: rgba(0,0,0,.38) !important;
    opacity: 0.6;
  }
}
</style>
