import { PartyAddressSchema } from '@/schemas/party-address'
import { useInputRules } from '@/composables'
import { PartySchemaIF } from '@/interfaces'

const {
  firstNameRules,
  middleNameRules,
  lastNameRules,
  businessNameRules,
  phoneRules,
  phoneExtensionRules,
  emailRules
} = useInputRules()

export const PartyFormSchema: PartySchemaIF = {
  firstName: firstNameRules(),
  middleName: middleNameRules,
  lastName: lastNameRules(),
  businessName: businessNameRules(),
  phone: phoneRules(),
  phoneExt: phoneExtensionRules,
  email: emailRules,
  address: PartyAddressSchema
}
