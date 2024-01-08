import { SchemaIF } from '@/composables/address/interfaces'

export interface PartySchemaIF {
  firstName: { rules: Array<(v:string) => true | string>, optional: boolean }
  middleName: { rules: Array<(v:string) => true | string>, optional: boolean }
  lastName: { rules: Array<(v:string) => true | string>, optional: boolean }
  businessName: { rules: Array<(v:string) => true | string>, optional: boolean }
  dbaName?: { rules: Array<(v:string) => true | string>, optional: boolean }
  phone: { rules: Array<(v:string) => true | string>, optional: boolean }
  phoneExt: { rules: Array<(v:string) => true | string>, optional: boolean }
  email: { rules: Array<(v:string) => true | string>, optional: boolean }
  address: { rules: SchemaIF, optional: boolean }
}
