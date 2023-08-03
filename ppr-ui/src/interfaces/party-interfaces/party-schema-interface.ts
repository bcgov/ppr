import { SchemaIF } from '@/composables/address/interfaces'

export interface PartySchemaIF {
  firstName: Array<(v:string) => true | string>,
  middleName: Array<(v:string) => true | string>,
  lastName: Array<(v:string) => true | string>,
  businessName: Array<(v:string) => true | string>,
  phone: Array<(v:string) => true | string>,
  phoneExt: Array<(v:string) => true | string>,
  email: Array<(v:string) => true | string>,
  address: SchemaIF
}
