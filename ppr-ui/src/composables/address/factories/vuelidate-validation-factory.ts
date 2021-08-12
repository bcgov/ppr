/* FUTURE:
 * Delete this if we decide not to move forward with vuelidate
 * Fix it to work otherwise
 */
import { computed, Ref, reactive } from '@vue/composition-api'

import { AddressIF, SchemaIF } from '@/composables/address/interfaces'

const useVuelidate = require('@vuelidate/core').default

export function useValidations (schema: Ref<SchemaIF>, address: Ref<AddressIF>) {
  const validations = reactive({ addressLocal: schema.value })
  const $v = useVuelidate(validations, reactive({ addressLocal: address.value }))

  /**
   * Misc Vuetify rules.
   * @param prop The name of the property object to validate.
   * @param key The name of the property key (field) to validate.
   * @returns True if the rule passes, otherwise an error string.
   */
  const vuetifyRules = {
    requiredRule: (prop: string, key: string): boolean | string => {
      return Boolean($v.value[prop] && !$v.value[prop][key].required.$invalid) || 'This field is required'
    },
    minLengthRule: (prop: string, key: string): boolean | string => {
      const min = validations.addressLocal[key].max
      const msg = min ? `Minimum length is ${min}` : 'Text is below minimum length'
      return Boolean($v.value[prop] && !$v.value[prop][key].minLength.$invalid) || msg
    },
    maxLengthRule: (prop: string, key: string): boolean | string => {
      const max = validations.addressLocal[key].max
      const msg = max ? `Maximum length is ${max}` : 'Text is over maximum length'
      return Boolean($v.value[prop] && !$v.value[prop][key].maxLength.$invalid) || msg
    },
    // FUTURE: generalize this rule to take a validation parameter (ie, 'CA')
    isCanadaRule: (prop: string, key: string): boolean | string => {
      return Boolean($v.value[prop] && !$v.value[prop][key].isCanada.$invalid) || 'Address must be in Canada'
    },
    // FUTURE: generalize this rule to take a validation parameter (ie, 'BC')
    isBCRule: (prop: string, key: string): boolean | string => {
      return Boolean($v.value[prop] && !$v.value[prop][key].isBC.$invalid) || 'Address must be in BC'
    }
  }

  /**
   * Creates a Vuetify rules object from the Vuelidate state.
   * @param model The name of the model we are validating.
   * @returns A Vuetify rules object.
   */
  const createVuetifyRulesObject = (model: string): { [attr: string]: Array<Function> } => {
    const obj = {
      street: [],
      streetAdditional: [],
      city: [],
      region: [],
      postalCode: [],
      country: [],
      deliveryInstructions: []
    }

    // ensure Vuelidate state object is initialized
    if ($v && $v.value[model]) {
      // iterate over Vuelidate object properties
      Object.keys($v.value[model])
        // only look at validation properties
        .filter(prop => prop.charAt(0) !== '$')
        .forEach(prop => {
          // create array for each validation property
          obj[prop] = []
          // iterate over validation property params
          Object.keys($v.value[model][prop])
            .forEach(param => {
              // add specified validation functions to array
              switch (param) {
                case 'required': obj[prop].push(() => vuetifyRules.requiredRule(model, prop)); break
                case 'minLength': obj[prop].push(() => vuetifyRules.minLengthRule(model, prop)); break
                case 'maxLength': obj[prop].push(() => vuetifyRules.maxLengthRule(model, prop)); break
                case 'isCanada': obj[prop].push(() => vuetifyRules.isCanadaRule(model, prop)); break
                case 'isBC': obj[prop].push(() => vuetifyRules.isBCRule(model, prop)); break
                // FUTURE: add extra validation functions here
                default: break
              }
            })
        })
    }

    // sample return object
    // street: [
    //   () => this.requiredRule('addressLocal', 'street'),
    //   () => this.minLengthRule('addressLocal', 'street'),
    //   () => this.maxLengthRule('addressLocal', 'street')
    // ],
    // ...

    return obj
  }

  /**
   * The Vuetify rules object. Used to display any validation errors/styling.
   * NB: As a getter, this is initialized between created() and mounted().
   * @returns the Vuetify validation rules object
   */
  const rules = computed((): { [attr: string]: Array<Function> } => {
    return createVuetifyRulesObject('addressLocal')
  })

  /** Array of validation rules used by input elements to prevent extra whitespace. */
  const spaceRules = [
    (v: string) => !/^\s/g.test(v) || 'Invalid spaces', // leading spaces
    (v: string) => !/\s$/g.test(v) || 'Invalid spaces', // trailing spaces
    (v: string) => !/\s\s/g.test(v) || 'Invalid word spacing' // multiple inline spaces
  ]
  return {
    $v,
    rules,
    spaceRules
  }
}
