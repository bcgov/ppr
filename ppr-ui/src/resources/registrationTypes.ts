import { APIRegistrationTypes, UIRegistrationTypes } from '@/enums'
import { RegistrationTypeIF } from '@/interfaces'

export const RegistrationTypesMiscellaneousCC: Array<RegistrationTypeIF> = [
  {
    class: 'registration-list-header',
    disabled: true,
    divider: false,
    group: 1,
    registrationTypeUI: null,
    registrationTypeAPI: null,
    text: 'Miscellaneous Registrations Act - Crown Charge Registrations'
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.CARBON_TAX,
    registrationTypeAPI: APIRegistrationTypes.CARBON_TAX,
    text: `${UIRegistrationTypes.CARBON_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.EXCISE_TAX,
    registrationTypeAPI: APIRegistrationTypes.EXCISE_TAX,
    text: `${UIRegistrationTypes.EXCISE_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.FOREST,
    registrationTypeAPI: APIRegistrationTypes.FOREST,
    text: `${UIRegistrationTypes.FOREST}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.INCOME_TAX,
    registrationTypeAPI: APIRegistrationTypes.INCOME_TAX,
    text: `${UIRegistrationTypes.INCOME_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.INSURANCE_PREMIUM_TAX,
    registrationTypeAPI: APIRegistrationTypes.INSURANCE_PREMIUM_TAX,
    text: `${UIRegistrationTypes.INSURANCE_PREMIUM_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.LOGGING_TAX,
    registrationTypeAPI: APIRegistrationTypes.LOGGING_TAX,
    text: `${UIRegistrationTypes.LOGGING_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.MINERAL_LAND_TAX,
    registrationTypeAPI: APIRegistrationTypes.MINERAL_LAND_TAX,
    text: `${UIRegistrationTypes.MINERAL_LAND_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.MOTOR_FUEL_TAX,
    registrationTypeAPI: APIRegistrationTypes.MOTOR_FUEL_TAX,
    text: `${UIRegistrationTypes.MOTOR_FUEL_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
    registrationTypeAPI: APIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
    text: `${UIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.PROPERTY_TRANSFER_TAX,
    registrationTypeAPI: APIRegistrationTypes.PROPERTY_TRANSFER_TAX,
    text: `${UIRegistrationTypes.PROPERTY_TRANSFER_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.PROVINCIAL_SALES_TAX,
    registrationTypeAPI: APIRegistrationTypes.PROVINCIAL_SALES_TAX,
    text: `${UIRegistrationTypes.PROVINCIAL_SALES_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.RURAL_PROPERTY_TAX,
    registrationTypeAPI: APIRegistrationTypes.RURAL_PROPERTY_TAX,
    text: `${UIRegistrationTypes.RURAL_PROPERTY_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.SCHOOL_ACT,
    registrationTypeAPI: APIRegistrationTypes.SCHOOL_ACT,
    text: `${UIRegistrationTypes.SCHOOL_ACT}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.SPECULATION_VACANCY_TAX,
    registrationTypeAPI: APIRegistrationTypes.SPECULATION_VACANCY_TAX,
    text: `${UIRegistrationTypes.SPECULATION_VACANCY_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.TOBACCO_TAX,
    registrationTypeAPI: APIRegistrationTypes.TOBACCO_TAX,
    text: `${UIRegistrationTypes.TOBACCO_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIRegistrationTypes.OTHER,
    registrationTypeAPI: APIRegistrationTypes.OTHER,
    text: `${UIRegistrationTypes.OTHER}`
  }
]
export const RegistrationTypesMiscellaneousOT: Array<RegistrationTypeIF> = [
  {
    class: 'registration-list-header',
    disabled: true,
    divider: false,
    group: 2,
    registrationTypeUI: null,
    registrationTypeAPI: null,
    text: 'Miscellaneous Registrations Act - Other Registrations'
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIRegistrationTypes.LIEN_UNPAID_WAGES,
    registrationTypeAPI: APIRegistrationTypes.LIEN_UNPAID_WAGES,
    text: `${UIRegistrationTypes.LIEN_UNPAID_WAGES}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
    registrationTypeAPI: APIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
    text: `${UIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
    registrationTypeAPI: APIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
    text: `${UIRegistrationTypes.MANUFACTURED_HOME_NOTICE}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIRegistrationTypes.MAINTENANCE_LIEN,
    registrationTypeAPI: APIRegistrationTypes.MAINTENANCE_LIEN,
    text: `${UIRegistrationTypes.MAINTENANCE_LIEN}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
    registrationTypeAPI: APIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
    text: `${UIRegistrationTypes.PROCEEDS_CRIME_NOTICE}`
  }
]
export const RegistrationTypesStandard: Array<RegistrationTypeIF> = [
  {
    class: 'registration-list-header',
    disabled: true,
    divider: false,
    group: 3,
    registrationTypeUI: null,
    registrationTypeAPI: null,
    text: 'Standard Registrations'
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.SECURITY_AGREEMENT,
    registrationTypeAPI: APIRegistrationTypes.SECURITY_AGREEMENT,
    text: `${UIRegistrationTypes.SECURITY_AGREEMENT} (${APIRegistrationTypes.SECURITY_AGREEMENT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.REPAIRERS_LIEN,
    registrationTypeAPI: APIRegistrationTypes.REPAIRERS_LIEN,
    text: `${UIRegistrationTypes.REPAIRERS_LIEN} (${APIRegistrationTypes.REPAIRERS_LIEN})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.MARRIAGE_MH,
    registrationTypeAPI: APIRegistrationTypes.MARRIAGE_MH,
    text: `${UIRegistrationTypes.MARRIAGE_MH} (${APIRegistrationTypes.MARRIAGE_MH})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.SALE_OF_GOODS,
    registrationTypeAPI: APIRegistrationTypes.SALE_OF_GOODS,
    text: `${UIRegistrationTypes.SALE_OF_GOODS} (${APIRegistrationTypes.SALE_OF_GOODS})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.LAND_TAX_LIEN,
    registrationTypeAPI: APIRegistrationTypes.LAND_TAX_LIEN,
    text: `${UIRegistrationTypes.LAND_TAX_LIEN} (${APIRegistrationTypes.LAND_TAX_LIEN})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.MANUFACTURED_HOME_LIEN,
    registrationTypeAPI: APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
    text: `${UIRegistrationTypes.MANUFACTURED_HOME_LIEN} (${APIRegistrationTypes.MANUFACTURED_HOME_LIEN})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
    registrationTypeAPI: APIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
    text: `${UIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN} (${APIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
    registrationTypeAPI: APIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
    text: `${UIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE} (${APIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN,
    registrationTypeAPI: APIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN,
    text: `${UIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN} (${APIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN})`
  }
]

export const MhrRegistrationType: RegistrationTypeIF = {
  class: 'registration-list-item',
  disabled: false,
  divider: false,
  group: 3,
  registrationTypeUI: UIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION,
  registrationTypeAPI: APIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION,
  text:
    `${UIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION} (${APIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION})`
}

export const LegacyRegistrationTypes: Array<RegistrationTypeIF> = [
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.MISC_MINERAL_RESOURCE,
    registrationTypeAPI: APIRegistrationTypes.MISC_MINERAL_RESOURCE,
    text: `${UIRegistrationTypes.MISC_MINERAL_RESOURCE}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.CROWN_MINING_TAX,
    registrationTypeAPI: APIRegistrationTypes.CROWN_MINING_TAX,
    text: `${UIRegistrationTypes.CROWN_MINING_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.CROWN_CORP_CAPITAL_TAX,
    registrationTypeAPI: APIRegistrationTypes.CROWN_CORP_CAPITAL_TAX,
    text: `${UIRegistrationTypes.CROWN_CORP_CAPITAL_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.CROWN_CONSUMPTION_TRANSITION_TAX,
    registrationTypeAPI: APIRegistrationTypes.CROWN_CONSUMPTION_TRANSITION_TAX,
    text: `${UIRegistrationTypes.CROWN_CONSUMPTION_TRANSITION_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.CROWN_HOTEL_ROOM_TAX,
    registrationTypeAPI: APIRegistrationTypes.CROWN_HOTEL_ROOM_TAX,
    text: `${UIRegistrationTypes.CROWN_HOTEL_ROOM_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.CROWN_SOCIAL_SERVICE_TAX,
    registrationTypeAPI: APIRegistrationTypes.CROWN_SOCIAL_SERVICE_TAX,
    text: `${UIRegistrationTypes.CROWN_SOCIAL_SERVICE_TAX}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT,
    registrationTypeAPI: APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT,
    text: `${UIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.TRANSITION_FINANCING_STATEMENT,
    registrationTypeAPI: APIRegistrationTypes.TRANSITION_FINANCING_STATEMENT,
    text: `${UIRegistrationTypes.TRANSITION_FINANCING_STATEMENT}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.TRANSITION_SALE_OF_GOODS,
    registrationTypeAPI: APIRegistrationTypes.TRANSITION_SALE_OF_GOODS,
    text: `${UIRegistrationTypes.TRANSITION_SALE_OF_GOODS}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.TRANSITION_TAX_LIEN,
    registrationTypeAPI: APIRegistrationTypes.TRANSITION_TAX_LIEN,
    text: `${UIRegistrationTypes.TRANSITION_TAX_LIEN}`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIRegistrationTypes.TRANSITION_MH,
    registrationTypeAPI: APIRegistrationTypes.TRANSITION_MH,
    text: `${UIRegistrationTypes.TRANSITION_MH}`
  }
]

export const RegistrationTypes: Array<RegistrationTypeIF> = [
  ...RegistrationTypesMiscellaneousCC,
  {
    class: 'registration-list-divider',
    disabled: true,
    divider: true,
    group: 0,
    registrationTypeUI: null,
    registrationTypeAPI: null,
    text: 'divider1'
  },
  ...RegistrationTypesMiscellaneousOT,
  {
    class: 'registration-list-divider',
    disabled: true,
    divider: true,
    group: 0,
    registrationTypeUI: null,
    registrationTypeAPI: null,
    text: 'divider2'
  },
  ...RegistrationTypesStandard
]

// Use this when displaying reg type information?
export const AllRegistrationTypes: Array<RegistrationTypeIF> = [
  ...RegistrationTypesMiscellaneousCC,
  ...RegistrationTypesMiscellaneousOT,
  ...RegistrationTypesStandard,
  ...LegacyRegistrationTypes
]
