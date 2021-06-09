import { maxLength, required } from 'vuelidate/lib/validators'

import { SchemaIF } from '@/composables/address/interfaces'

export const DefaultSchema: SchemaIF = {
  streetAddress: {
    max: 50,
    maxLength: maxLength(50),
    required
  },
  streetAddressAdditional: {
    max: 50,
    maxLength: maxLength(50)
  },
  addressCity: {
    max: 40,
    maxLength: maxLength(40),
    required
  },
  addressCountry: {
    // FUTURE: create new validation function isCountry('CA')
    isCanada: (val: string) => Boolean(val === 'CA'),
    required
  },
  addressRegion: {
    // FUTURE: create new validation function isRegion('BC')
    isBC: (val: string) => Boolean(val === 'BC'),
    max: 2,
    maxLength: maxLength(2),
    required
  },
  postalCode: {
    max: 15,
    maxLength: maxLength(15),
    required
  },
  deliveryInstructions: {
    max: 80,
    maxLength: maxLength(80),
  }
}