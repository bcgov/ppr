interface SchemaOptionsIF {
  isBC?: (val: string) => boolean
  isCanada?: (val: string) => boolean
  max?: number // expected if maxLength is defined
  maxLength?: () => boolean // vuelidate builtin maxLength is expected
  min?: number // expected if minLength is defined
  minLength?: () => boolean // vuelidate builtin minLength is expected
  required?: () => boolean // vuelidate builtin required is expected
}

export interface SchemaIF {
  street: SchemaOptionsIF,
  streetAdditional: SchemaOptionsIF,
  city: SchemaOptionsIF,
  region: SchemaOptionsIF,
  postalCode: SchemaOptionsIF,
  country: SchemaOptionsIF,
  deliveryInstructions: SchemaOptionsIF
}
