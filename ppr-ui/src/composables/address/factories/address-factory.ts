/* eslint-disable */
import { computed, reactive, Ref } from '@vue/composition-api'
import { uniqueId } from 'lodash'

import { AddressIF, SchemaIF } from '@/composables/address/interfaces'

export function useAddress (address: Ref<AddressIF>, schema: Ref<SchemaIF>) {
  const addressLocal = address
  /** The Address Country, to simplify the template and so we can watch it directly. */
  const country = computed((): string => {
    return addressLocal.value.country
  })
  const schemaLocal = schema
  const isSchemaRequired = (prop: string): boolean => {
    return Boolean(schemaLocal && schemaLocal.value[prop] && schemaLocal.value[prop].required)
  }
  const labels = {
    /** The Street Address Additional label with 'optional' as needed. */
    streetAdditionalLabel: computed((): string => {
      return 'Additional Street Address' + (isSchemaRequired('streetAdditional') ? '' : ' (Optional)')
    }),
    /** The Street Address label with 'optional' as needed. */
    streetLabel: computed((): string => {
      return 'Street Address' + (isSchemaRequired('street') ? '' : ' (Optional)')
    }),
    /** The Address City label with 'optional' as needed. */
    cityLabel: computed((): string => {
      return 'City' + (isSchemaRequired('city') ? '' : ' (Optional)')
    }),
    /** The Address Region label with 'optional' as needed. */
    regionLabel: computed((): string => {
      let label: string
      let required = isSchemaRequired('region')

      // NB: make region required for Canada and USA
      if (addressLocal.value.country === 'CA') {
        label = 'Province'
        required = true
      } else if (addressLocal.value.country === 'US') {
        label = 'State'
        required = true
      } else {
        label = 'Province/State'
      }
      return label + (required ? '' : ' (Optional)')
    }),
    /** The Postal Code label with 'optional' as needed. */
    postalCodeLabel: computed((): string => {
      let label: string
      if (addressLocal.value.country === 'US') {
        label = 'Zip Code'
      } else {
        label = 'Postal Code'
      }
      return label + (isSchemaRequired('postalCode') ? '' : ' (Optional)')
    }),
    /** The Address Country label with 'optional' as needed. */
    countryLabel: computed((): string => {
      return 'Country' + (isSchemaRequired('country') ? '' : ' (Optional)')
    }),
    /** The Delivery Instructions label with 'optional' as needed. */
    deliveryInstructionsLabel: computed((): string => {
      return 'Delivery Instructions' + (isSchemaRequired('deliveryInstructions') ? '' : ' (Optional)')
    })
  }
  return {
    addressLocal,
    country,
    schemaLocal,
    isSchemaRequired,
    labels
  }
}

export function useAddressComplete (addressLocal: Ref<AddressIF>) {
  const combineLines = (line1: string, line2: string) => {
    if (!line1) return line2
    if (!line2) return line1
    return line1 + '\n' + line2
  }
  /**
   * Callback to update the address data after the user chooses a suggested address.
   * @param address the data object returned by the AddressComplete Retrieve API
   */
  const addressCompletePopulate = (addressComplete: object): void => {
    addressLocal.value.street = addressComplete['Line1'] || 'N/A'
    // Combine extra address lines into Street Address Additional field.
    addressLocal.value.streetAdditional = combineLines(
      combineLines(addressComplete['Line2'], addressComplete['Line3']),
      combineLines(addressComplete['Line4'], addressComplete['Line5'])
    )
    addressLocal.value.city = addressComplete['City']
    if (useCountryRegions(addressComplete['CountryIso2'])) {
      // In this case, v-select will map known province code to province name
      // or v-select will be blank and user will have to select a known item.
      addressLocal.value.region = addressComplete['ProvinceCode']
    } else {
      // In this case, v-text-input will allow manual entry but province info is probably too long
      // so set region to null and add province name to the Street Address Additional field.
      // If length is excessive, user will have to fix it.
      addressLocal.value.region = null
      addressLocal.value.streetAdditional = combineLines(
        addressLocal.value.streetAdditional, addressComplete['ProvinceName']
      )
    }
    addressLocal.value.postalCode = addressComplete['PostalCode']
    addressLocal.value.country = addressComplete['CountryIso2']
  }
  const uniqueIds = reactive({
    /** A unique id for this instance of this component. */
    uniqueId: uniqueId(),
    /** A unique id for the Street Address input. */
    streetId: computed((): string => {
      return `street-address-${uniqueIds.uniqueId}`
    }),
    /** A unique id for the Address Country input. */
    countryId: computed((): string => {
      return `address-country-${uniqueIds.uniqueId}`
    })
  })
  /**
   * Creates the AddressComplete object for this instance of the component.
   * @param pca the Postal Code Anywhere object provided by AddressComplete
   * @param key the key for the Canada Post account that is to be charged for lookups
   * @returns an object that is a pca.Address instance
   */
  const createAddressComplete = (pca: any, key: string): object => {
    // Set up the two fields that AddressComplete will use for input.
    // Ref: https://www.canadapost.ca/pca/support/guides/advanced
    // Note: Use special field for country, which user can't click, and which AC will overwrite
    //       but that we don't care about.
    const fields = [
      { element: uniqueIds.streetId, field: 'Line1', mode: pca.fieldMode.SEARCH },
      { element: uniqueIds.countryId, field: 'CountryName', mode: pca.fieldMode.COUNTRY }
    ]
    const options = { key }

    const addressComplete = new pca.Address(fields, options)

    // The documentation contains sample load/populate callback code that doesn't work, but this will. The side effect
    // is that it breaks the autofill functionality provided by the library, but we really don't want the library
    // altering the DOM because Vue is already doing so, and the two don't play well together.
    addressComplete.listen('populate', addressCompletePopulate)

    return addressComplete
  }
  /** Enables AddressComplete for this instance of the address. */
  const enableAddressComplete = (): void => {
    // If you want to use this component with the Canada Post AddressComplete service:
    // 1. The AddressComplete JavaScript script (and stylesheet) must be loaded.
    // 2. Your AddressComplete account key must be defined.
    const pca = window['pca']
    const key = window['addressCompleteKey']
    if (!pca || !key) {
      // eslint-disable-next-line no-console
      console.log('AddressComplete not initialized due to missing script and/or key')
      return
    }

    // Destroy the old object if it exists, and create a new one.
    if (window['currentAddressComplete']) {
      window['currentAddressComplete'].destroy()
    }
    window['currentAddressComplete'] = createAddressComplete(pca, key)
  }
  return {
    addressCompletePopulate,
    createAddressComplete,
    enableAddressComplete,
    uniqueIds
  }
}

/**
 * Determines whether to use a country's known regions (ie, provinces/states).
 * @param code the short code of the country
 * @returns whether to use v-select (true) or v-text-field (false) for input
 */
export function useCountryRegions (code: string): boolean {
  return (code === 'CA' || code === 'US')
}
