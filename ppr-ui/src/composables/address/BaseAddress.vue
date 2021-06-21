<template>
  <div class="base-address">
    <!-- Display fields -->
    <v-expand-transition>
      <div v-if="!editing" class="address-block">
        <div class="address-block__info pre-wrap">
          <div class="address-block__info-row">{{ addressLocal.street }}</div>
          <div class="address-block__info-row">{{ addressLocal.streetAdditional }}</div>
          <div class="address-block__info-row">
            <span>{{ addressLocal.city }}</span>
            <span v-if="addressLocal.region">&nbsp;{{ addressLocal.region }}</span>
            <span v-if="addressLocal.postalCode">&nbsp;{{ addressLocal.postalCode }}</span>
          </div>
          <div class="address-block__info-row">{{ getCountryName(country) }}</div>
          <div class="address-block__info-row">{{ addressLocal.deliveryInstructions }}</div>
        </div>
      </div>
    </v-expand-transition>

    <!-- Edit fields -->
    <v-expand-transition>
      <v-form v-if="editing" ref="addressForm" name="address-form" lazy-validation>
        <div class="form__row">
          <!-- NB1: AddressComplete needs to be enabled each time user clicks in this search field.
               NB2: Only process first keypress -- assumes if user moves between instances of this
                   component then they are using the mouse (and thus, clicking). -->
          <v-text-field autocomplete="chrome-off"
                        :name="Math.random()"
                        filled
                        class="street-address"
                        :id="streetId"
                        :label="streetLabel"
                        v-model="addressLocal.street"
                        :rules="[...rules.street, ...spaceRules]"
                        @keypress.once="enableAddressComplete()"
                        @click="enableAddressComplete()"
          />
        </div>
        <div class="form__row">
          <v-textarea auto-grow
                      filled
                      class="street-address-additional"
                      :label="streetAdditionalLabel"
                      rows="1"
                      v-model="addressLocal.streetAdditional"
                      :rules="[...rules.streetAdditional, ...spaceRules]"
          />
        </div>
        <div class="form__row three-column">
          <v-text-field filled
                        class="item address-city"
                        :label="cityLabel"
                        v-model="addressLocal.city"
                        :rules="[...rules.city, ...spaceRules]"
          />
          <v-select v-if="useCountryRegions(country)"
                    filled
                    class="item address-region"
                    :menu-props="{maxHeight:'40rem'}"
                    :label="regionLabel"
                    item-text="name"
                    item-value="short"
                    v-model="addressLocal.region"
                    :items="getCountryRegions(country)"
                    :rules="[...rules.region, ...spaceRules]"
          />
          <v-text-field v-else
                        filled
                        class="item address-region"
                        :label="regionLabel"
                        v-model="addressLocal.region"
                        :rules="[...rules.region, ...spaceRules]"
          />
          <v-text-field filled
                        class="item postal-code"
                        :label="postalCodeLabel"
                        v-model="addressLocal.postalCode"
                        :rules="[...rules.postalCode, ...spaceRules]"
          />
        </div>
        <div class="form__row">
          <v-select filled
                    class="address-country"
                    :label="countryLabel"
                    menu-props="auto"
                    item-text="name"
                    item-value="code"
                    v-model="addressLocal.country"
                    :items="getCountries()"
                    :rules="[...rules.country, ...spaceRules]"
          />
          <!-- special field to select AddressComplete country, separate from our model field -->
          <input type="hidden" :id="countryId" :value="country" />
        </div>
        <div class="form__row">
          <v-textarea auto-grow
                      filled
                      class="delivery-instructions"
                      :label="deliveryInstructionsLabel"
                      rows="2"
                      v-model="addressLocal.deliveryInstructions"
                      :rules="[...rules.deliveryInstructions, ...spaceRules]"
          />
        </div>
      </v-form>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRefs, watch } from '@vue/composition-api'
import { required } from 'vuelidate/lib/validators'

import {
  useAddress,
  useAddressComplete,
  useCountryRegions,
  useCountriesProvinces,
  useValidations
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
    editing: {
      type: Boolean,
      default: false
    },
    schema: {
      type: Object as () => SchemaIF,
      default: null
    }
  },
  setup (props, { emit }) {
    /**
     * NOTE: since toRefs(props).address / toRefs(props).schema are being passed in to useAddress
     * both addressLocal / schemaLocal will update/be updated by the parent component even though
     * neither one has a watcher or an emit
     */
    const {
      addressLocal,
      country,
      schemaLocal,
      isSchemaRequired,
      labels
    } = useAddress(toRefs(props).value, toRefs(props).schema)

    const { $v, rules, spaceRules } = useValidations(schemaLocal, addressLocal)

    const { enableAddressComplete, uniqueIds } = useAddressComplete(addressLocal)

    const countryProvincesHelpers = useCountriesProvinces()

    /**
     * Watches changes to the Address Country and updates the schema accordingly.
     */
    watch(() => country, () => {
      // skip this if component is called without a schema (eg, display mode)
      if (schemaLocal) {
        if (useCountryRegions(addressLocal.value.country)) {
          // we are using a region list for the current country so make region a required field
          const region = { ...schemaLocal.value.region, required }
          // re-assign the local schema because Vue does not detect property addition
          schemaLocal.value = { ...schemaLocal.value, region }
        } else {
          // we are not using a region list for the current country so remove required property
          const { required, ...region } = schemaLocal.value.region
          // re-assign the local schema because Vue does not detect property deletion
          schemaLocal.value = { ...schemaLocal.value, region }
        }
      }
    })
    watch(() => $v.value, (val) => {
      emit('valid', !val.$invalid)
    }, { deep: true, immediate: true })

    return {
      addressLocal,
      country,
      ...countryProvincesHelpers,
      enableAddressComplete,
      isSchemaRequired,
      ...labels,
      rules,
      schemaLocal,
      spaceRules,
      useCountryRegions,
      ...uniqueIds,
      $v
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

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
