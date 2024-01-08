import { PartyAddressSchema } from '@/schemas/party-address'
import { useInputRules } from '@/composables'
import { PartySchemaIF } from '@/interfaces'

const {
  firstNameRules,
  middleNameRules,
  lastNameRules,
  businessNameRules,
  dbaNameRules,
  phoneRules,
  phoneExtensionRules,
  emailRules
} = useInputRules()

export const PartyFormSchema: PartySchemaIF = {
  firstName: { rules: firstNameRules(), optional: false },
  middleName: { rules: middleNameRules, optional: true },
  lastName: { rules: lastNameRules(), optional: false },
  businessName: { rules: businessNameRules(), optional: false },
  dbaName: { rules: dbaNameRules(), optional: true },
  phone: { rules: phoneRules(), optional: false },
  phoneExt: { rules: phoneExtensionRules, optional: true },
  email: { rules: emailRules, optional: true },
  address: { rules: PartyAddressSchema, optional: false }
}

export const ExemptionPartyFormSchema: PartySchemaIF = {
  firstName: { rules: firstNameRules(), optional: false },
  middleName: { rules: middleNameRules, optional: true },
  lastName: { rules: lastNameRules(), optional: false },
  businessName: { rules: businessNameRules(), optional: false },
  phone: { rules: phoneRules(true), optional: true },
  phoneExt: { rules: phoneExtensionRules, optional: true },
  email: { rules: emailRules, optional: true },
  address: { rules: PartyAddressSchema, optional: false }
}
