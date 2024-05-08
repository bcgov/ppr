import {
  APIMhrDescriptionTypes,
  APIRegistrationTypes,
  BlankSearchTypes,
  UIMhrDescriptionTypes,
  UIRegistrationTypes
} from '@/enums'
import { MhRegistrationTypeIF, RegistrationTypeIF } from '@/interfaces'

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

export const MhrCorrectionStaff: RegistrationTypeIF = {
  class: 'registration-list-item',
  disabled: false,
  divider: false,
  group: 1,
  registrationTypeUI: UIRegistrationTypes.MHR_CORRECTION_STAFF,
  registrationTypeAPI: APIRegistrationTypes.MHR_CORRECTION_STAFF,
  text:
    `Registry Correction - ${UIRegistrationTypes.MHR_CORRECTION_STAFF}`
}

export const MhrCorrectionClient: RegistrationTypeIF = {
  class: 'registration-list-item',
  disabled: false,
  divider: false,
  group: 1,
  registrationTypeUI: UIRegistrationTypes.MHR_CORRECTION_CLIENT,
  registrationTypeAPI: APIRegistrationTypes.MHR_CORRECTION_CLIENT,
  text:
    `Registry Correction - ${UIRegistrationTypes.MHR_CORRECTION_CLIENT}`
}

export const MhrPublicAmendment: RegistrationTypeIF = {
  class: 'registration-list-item',
  disabled: false,
  divider: false,
  group: 1,
  registrationTypeUI: UIRegistrationTypes.MHR_PUBLIC_AMENDMENT,
  registrationTypeAPI: APIRegistrationTypes.MHR_PUBLIC_AMENDMENT,
  text: UIRegistrationTypes.MHR_PUBLIC_AMENDMENT
}

export const MHRegistrationTypesOrg: Array<MhRegistrationTypeIF> = [
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
    registrationTypeUI: UIMhrDescriptionTypes.CONVERTED,
    registrationTypeAPI: APIMhrDescriptionTypes.CONVERTED,
    text: `${UIMhrDescriptionTypes.CONVERTED} (${APIMhrDescriptionTypes.CONVERTED})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.REGISTER_NEW_UNIT,
    registrationTypeAPI: APIMhrDescriptionTypes.REGISTER_NEW_UNIT,
    text: `${UIMhrDescriptionTypes.REGISTER_NEW_UNIT} (${APIMhrDescriptionTypes.REGISTER_NEW_UNIT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.SALE_OR_GIFT,
    registrationTypeAPI: APIMhrDescriptionTypes.SALE_OR_GIFT,
    text: `${UIMhrDescriptionTypes.SALE_OR_GIFT} (${APIMhrDescriptionTypes.SALE_OR_GIFT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.SURVIVING_JOINT_TENANT,
    registrationTypeAPI: APIMhrDescriptionTypes.SURVIVING_JOINT_TENANT,
    text: `${UIMhrDescriptionTypes.SURVIVING_JOINT_TENANT} (${APIMhrDescriptionTypes.SURVIVING_JOINT_TENANT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL,
    text: `${UIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL}
          (${APIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL,
    text: `${UIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL}
          (${APIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR,
    text: `${UIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR}
          (${APIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR})`
  }
]

export const MHRegistrationTypes: Array<MhRegistrationTypeIF> = [
  {
    class: 'registration-list-header',
    disabled: true,
    divider: false,
    group: 1,
    registrationTypeUI: BlankSearchTypes.BLANK1 as any,
    registrationTypeAPI: BlankSearchTypes.BLANK1 as any,
    text: 'Registrations'
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIMhrDescriptionTypes.REGISTER_NEW_UNIT,
    registrationTypeAPI: APIMhrDescriptionTypes.REGISTER_NEW_UNIT,
    text: `${UIMhrDescriptionTypes.REGISTER_NEW_UNIT} (${APIMhrDescriptionTypes.REGISTER_NEW_UNIT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 1,
    registrationTypeUI: UIMhrDescriptionTypes.CONVERTED,
    registrationTypeAPI: APIMhrDescriptionTypes.CONVERTED,
    text: `${UIMhrDescriptionTypes.CONVERTED} (${APIMhrDescriptionTypes.CONVERTED})`
  },
  {
    class: 'registration-list-header',
    disabled: true,
    divider: false,
    group: 2,
    registrationTypeUI: BlankSearchTypes.BLANK1 as any,
    registrationTypeAPI: BlankSearchTypes.BLANK1 as any,
    text: 'Bill of Sale Transfers'
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIMhrDescriptionTypes.SALE_OR_GIFT,
    registrationTypeAPI: APIMhrDescriptionTypes.SALE_OR_GIFT,
    text: `${UIMhrDescriptionTypes.SALE_OR_GIFT} (${APIMhrDescriptionTypes.SALE_OR_GIFT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIMhrDescriptionTypes.TRANS_FAMILY_ACT,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANS_FAMILY_ACT,
    text: `${UIMhrDescriptionTypes.TRANS_FAMILY_ACT} (${APIMhrDescriptionTypes.TRANS_FAMILY_ACT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIMhrDescriptionTypes.TRANS_INFORMAL_SALE,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANS_INFORMAL_SALE,
    text: `${UIMhrDescriptionTypes.TRANS_INFORMAL_SALE} (${APIMhrDescriptionTypes.TRANS_INFORMAL_SALE})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIMhrDescriptionTypes.TRANS_QUIT_CLAIM,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANS_QUIT_CLAIM,
    text: `${UIMhrDescriptionTypes.TRANS_QUIT_CLAIM} (${APIMhrDescriptionTypes.TRANS_QUIT_CLAIM})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIMhrDescriptionTypes.TRANS_RECEIVERSHIP,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANS_RECEIVERSHIP,
    text: `${UIMhrDescriptionTypes.TRANS_RECEIVERSHIP} (${APIMhrDescriptionTypes.TRANS_RECEIVERSHIP})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIMhrDescriptionTypes.TRANS_SEVER_GRANT,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANS_SEVER_GRANT,
    text: `${UIMhrDescriptionTypes.TRANS_SEVER_GRANT} (${APIMhrDescriptionTypes.TRANS_SEVER_GRANT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 2,
    registrationTypeUI: UIMhrDescriptionTypes.TRANS_WRIT_SEIZURE,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANS_WRIT_SEIZURE,
    text: `${UIMhrDescriptionTypes.TRANS_WRIT_SEIZURE} (${APIMhrDescriptionTypes.TRANS_WRIT_SEIZURE})`
  },

  {
    class: 'registration-list-header',
    disabled: true,
    divider: false,
    group: 3,
    registrationTypeUI: BlankSearchTypes.BLANK1 as any,
    registrationTypeAPI: BlankSearchTypes.BLANK1 as any,
    text: 'Transfers Due to Death'
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.SURVIVING_JOINT_TENANT,
    registrationTypeAPI: APIMhrDescriptionTypes.SURVIVING_JOINT_TENANT,
    text: `${UIMhrDescriptionTypes.SURVIVING_JOINT_TENANT} (${APIMhrDescriptionTypes.SURVIVING_JOINT_TENANT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL,
    text: `${UIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL}
          (${APIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL,
    text: `${UIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL}
          (${APIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 3,
    registrationTypeUI: UIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR,
    text: `${UIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR}
          (${APIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR})`
  },
  {
    class: 'registration-list-header',
    disabled: true,
    divider: false,
    group: 4,
    registrationTypeUI: BlankSearchTypes.BLANK1 as any,
    registrationTypeAPI: BlankSearchTypes.BLANK1 as any,
    text: 'Other Transfers'
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.ABAN,
    registrationTypeAPI: APIMhrDescriptionTypes.ABAN,
    text: `${UIMhrDescriptionTypes.ABAN} (${APIMhrDescriptionTypes.ABAN})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.BANK,
    registrationTypeAPI: APIMhrDescriptionTypes.BANK,
    text: `${UIMhrDescriptionTypes.BANK} (${APIMhrDescriptionTypes.BANK})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.COU,
    registrationTypeAPI: APIMhrDescriptionTypes.COU,
    text: `${UIMhrDescriptionTypes.COU} (${APIMhrDescriptionTypes.COU})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.FORE,
    registrationTypeAPI: APIMhrDescriptionTypes.FORE,
    text: `${UIMhrDescriptionTypes.FORE} (${APIMhrDescriptionTypes.FORE})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.GENT,
    registrationTypeAPI: APIMhrDescriptionTypes.GENT,
    text: `${UIMhrDescriptionTypes.GENT} (${APIMhrDescriptionTypes.GENT})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.TRANS_LAND_TITLE,
    registrationTypeAPI: APIMhrDescriptionTypes.TRANS_LAND_TITLE,
    text: `${UIMhrDescriptionTypes.TRANS_LAND_TITLE} (${APIMhrDescriptionTypes.TRANS_LAND_TITLE})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.REIV,
    registrationTypeAPI: APIMhrDescriptionTypes.REIV,
    text: `${UIMhrDescriptionTypes.REIV} (${APIMhrDescriptionTypes.REIV})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.REPV,
    registrationTypeAPI: APIMhrDescriptionTypes.REPV,
    text: `${UIMhrDescriptionTypes.REPV} (${APIMhrDescriptionTypes.REPV})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.SZL,
    registrationTypeAPI: APIMhrDescriptionTypes.SZL,
    text: `${UIMhrDescriptionTypes.SZL} (${APIMhrDescriptionTypes.SZL})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.TAXS,
    registrationTypeAPI: APIMhrDescriptionTypes.TAXS,
    text: `${UIMhrDescriptionTypes.TAXS} (${APIMhrDescriptionTypes.TAXS})`
  },
  {
    class: 'registration-list-item',
    disabled: false,
    divider: false,
    group: 4,
    registrationTypeUI: UIMhrDescriptionTypes.VEST,
    registrationTypeAPI: APIMhrDescriptionTypes.VEST,
    text: `${UIMhrDescriptionTypes.VEST} (${APIMhrDescriptionTypes.VEST})`
  }
]

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
