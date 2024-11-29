export interface SchemaIF {
  street: Array<(v:string) => true | string>
  streetAdditional: Array<(v:string) => true | string>
  city: Array<(v:string) => true | string>
  region: Array<(v:string) => true | string>
  postalCode: Array<(v:string) => true | string>
  country: Array<(v:string) => true | string>
  deliveryInstructions: Array<(v:string) => true | string>
}
