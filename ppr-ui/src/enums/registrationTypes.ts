export enum APIRegistrationTypes {
  // standard
  SECURITY_AGREEMENT = 'SA',
  SECURITY_ACT_NOTICE = 'SE',
  REPAIRERS_LIEN = 'RL',
  MARRIAGE_MH = 'FR',
  SALE_OF_GOODS = 'SG',
  LAND_TAX_LIEN = 'LT',
  MANUFACTURED_HOME_LIEN = 'MH',
  FORESTRY_CONTRACTOR_LIEN = 'FL',
  FORESTRY_CONTRACTOR_CHARGE = 'FA',
  FORESTRY_SUBCONTRACTOR_LIEN = 'FS',
  // miscellaneous registration cc
  CARBON_TAX = 'CT',
  EXCISE_TAX = 'ET',
  FOREST = 'FO',
  INCOME_TAX = 'IT',
  INSURANCE_PREMIUM_TAX = 'IP',
  LOGGING_TAX = 'LO',
  MINERAL_LAND_TAX = 'MD',
  MOTOR_FUEL_TAX = 'FT',
  PETROLEUM_NATURAL_GAS_TAX = 'PG',
  PROPERTY_TRANSFER_TAX = 'PT',
  PROVINCIAL_SALES_TAX = 'PS',
  RURAL_PROPERTY_TAX = 'RA',
  SCHOOL_ACT = 'SC',
  SPECULATION_VACANCY_TAX = 'SV',
  TOBACCO_TAX = 'TO',
  OTHER = 'OT',
  // miscellaneous registration other
  LIEN_UNPAID_WAGES = 'WL',
  HERITAGE_CONSERVATION_NOTICE = 'HN',
  MANUFACTURED_HOME_NOTICE = 'MN',
  MANUFACTURED_HOME_REGISTRATION = 'MHR',
  MAINTENANCE_LIEN = 'ML',
  PROCEEDS_CRIME_NOTICE = 'PN',
  // Existing legacy registrations types that can no longer be created.
  MISC_MINERAL_RESOURCE = 'MR',
  CROWN_MINING_TAX = 'MI',
  CROWN_CORP_CAPITAL_TAX = 'CC',
  CROWN_CONSUMPTION_TRANSITION_TAX = 'DP',
  CROWN_HOTEL_ROOM_TAX = 'HR',
  CROWN_SOCIAL_SERVICE_TAX = 'SS',
  TRANSITION_SECURITY_AGREEMENT = 'TA',
  TRANSITION_FINANCING_STATEMENT = 'TF',
  TRANSITION_SALE_OF_GOODS = 'TG',
  TRANSITION_TAX_LIEN = 'TL',
  TRANSITION_MH = 'TM',
  TRANSFER_OF_SALE = 'TRANS',
  TRANSFER_DUE_TO_DEATH = 'TRAND',
  NON_RESIDENTIAL_EXEMPTION = 'EXEMPTION_NON_RES',
  RESIDENTIAL_EXEMPTION = 'EXEMPTION_RES',
  TRANSPORT_PERMIT = 'PERMIT',
  TRANSPORT_PERMIT_CANCEL = 'CANCEL_PERMIT',
  // Admin Registrations
  REGISTERED_LOCATION_CHANGE = 'STAT',
  MHR_CORRECTION_STAFF = 'REGC_STAFF',
  MHR_CORRECTION_CLIENT = 'REGC_CLIENT',
  MHR_PUBLIC_AMENDMENT = 'PUBA',
  MHR_RE_REGISTRATION = 'EXRE'
}

export enum UIRegistrationTypes {
  // standard
  SECURITY_AGREEMENT = 'Security Agreement',
  SECURITY_ACT_NOTICE = 'Securities Order or Proceedings Notice',
  REPAIRERS_LIEN = 'Repairers Lien',
  MARRIAGE_MH = 'Marriage / Separation Agreement affecting Manufactured Home under Family Law Act',
  SALE_OF_GOODS = 'Possession under S.30 of the Sale of Goods Act',
  LAND_TAX_LIEN = 'Land Tax Deferment Lien on a Manufactured Home',
  MANUFACTURED_HOME_LIEN = 'Tax Lien under S.27/28 of the Manufactured Home Act',
  MANUFACTURED_HOME_REGISTRATION = 'Manufactured Home Registration',
  FORESTRY_CONTRACTOR_LIEN = 'Forestry - Contractor Lien',
  FORESTRY_CONTRACTOR_CHARGE = 'Forestry - Contractor Charge',
  FORESTRY_SUBCONTRACTOR_LIEN = 'Forestry - Sub-contractor Charge',
  // miscellaneous registration cc
  CARBON_TAX = 'Crown Charge - Carbon Tax Act',
  EXCISE_TAX = 'Crown Charge - Excise Tax Act',
  FOREST = 'Crown Charge - Forest Act',
  INCOME_TAX = 'Crown Charge - Income Tax Act',
  INSURANCE_PREMIUM_TAX = 'Crown Charge - Insurance Premium Tax Act',
  LOGGING_TAX = 'Crown Charge - Logging Tax Act',
  MINERAL_LAND_TAX = 'Crown Charge - Mineral Land Tax Act',
  MOTOR_FUEL_TAX = 'Crown Charge - Motor Fuel Tax Act',
  PROPERTY_TRANSFER_TAX = 'Crown Charge - Property Transfer Tax Act',
  PETROLEUM_NATURAL_GAS_TAX = 'Crown Charge - Petroleum and Natural Gas Act',
  PROVINCIAL_SALES_TAX = 'Crown Charge - Provincial Sales Tax Act',
  RURAL_PROPERTY_TAX = 'Crown Charge - Taxation (Rural Area) Act',
  SCHOOL_ACT = 'Crown Charge - School Act',
  SPECULATION_VACANCY_TAX = 'Crown Charge - Speculation and Vacancy Tax Act',
  TOBACCO_TAX = 'Crown Charge - Tobacco Tax Act',
  OTHER = 'Crown Charge - Other',
  // miscellaneous registration other
  LIEN_UNPAID_WAGES = 'Lien for Unpaid Wages',
  HERITAGE_CONSERVATION_NOTICE = 'Heritage Conservation Notice',
  MANUFACTURED_HOME_NOTICE = 'Manufactured Home Notice',
  MHR_CORRECTION = 'Registry Correction',
  MHR_CORRECTION_STAFF = 'Staff Error or Omission',
  MHR_CORRECTION_CLIENT = 'Client Error or Omission',
  MHR_PUBLIC_AMENDMENT = 'Public Amendment',
  MAINTENANCE_LIEN = 'Maintenance Lien',
  PROCEEDS_CRIME_NOTICE = 'Proceeds of Crime Notice',
  // Existing legacy registrations types that can no longer be created.
  MISC_MINERAL_RESOURCE = 'Mineral Resource Tax Act',
  CROWN_MINING_TAX = 'Mining Tax Act',
  CROWN_CORP_CAPITAL_TAX = 'Corporation Capital Tax Act',
  CROWN_CONSUMPTION_TRANSITION_TAX = 'Consumption, Transition Tax Act',
  CROWN_HOTEL_ROOM_TAX = 'Hotel Room Tax Act',
  CROWN_SOCIAL_SERVICE_TAX = 'Social Service Tax Act',
  TRANSITION_SECURITY_AGREEMENT = 'Security Agreement Transition',
  TRANSITION_FINANCING_STATEMENT = 'PPSA Transition',
  TRANSITION_SALE_OF_GOODS = 'Sales of Goods Transition',
  TRANSITION_TAX_LIEN = 'Tax Lien Transition Social Service/Hotel Room',
  TRANSITION_MH = 'M.H. Transition',
  TRANSFER_OF_SALE = 'Sale or Gift',
  TRANSFER_DUE_TO_DEATH = 'Sale or Gift due to death',
  NON_RESIDENTIAL_EXEMPTION = 'Non-Residential Exemption',
  RESIDENTIAL_EXEMPTION = 'Residential Exemption',
  TRANSPORT_PERMIT = 'Transport Permit',

  //  MHR Re-registration
  MANUFACTURED_HOME_RE_REGISTRATION = 'Re-Register Manufactured Home'
}

export enum StatementTypes {
  AMENDMENT_STATEMENT = 'AMENDMENT',
  CHANGE_STATEMENT = 'CHANGE',
  DISHCARGE_STATEMENT = 'DISCHARGE',
  FINANCING_STATEMENT = 'FINANCING',
  RENEWAL_STATEMENT = 'RENEWAL'
}

export enum APIAmendmentTypes {
  AMENDMENT = 'AM', // Default, use if multiple changes or only description.
  CHANGE_COLLATERAL_ADDITION = 'AC', // legacy change filing
  CHANGE_COLLATERAL_SUBSTITUTION = 'SU', // legacy change filing
  CHANGE_DEBTOR_RELEASE = 'DR', // legacy change filing
  CHANGE_DEBTOR_TRANSFER = 'DT', // legacy change filing
  CHANGE_PARTIAL_DISCHARGE = 'PD', // legacy change filing
  CHANGE_REGISTRY_CORRECTION = 'RC', // legacy change filing
  CHANGE_SECURED_PARTY_TRANSFER = 'ST', // legacy change filing
  COURT_ORDER = 'CO', // Use if including court order information.
  COLLATERAL_ADDITION = 'AA', // Only adding collateral.
  COLLATERAL_SUBSTITUTION = 'AU', // Only adding and removing collateral.
  DEBTOR_TRANSFER = 'AD', // Only adding and removing a debtor.
  DEBTOR_RELEASE = 'AR', // Only removing a debtor.
  DISCHARGE = 'DC',
  PARTIAL_DISCHARGE = 'AP', // Only removing collateral.
  RENEWAL = 'RE',
  SECURED_PARTY_TRANSFER = 'AS', // Only adding and removing a secured party.,
  CHANGE_SECURITY_NOTICE_ADDITION = 'A1',
  CHANGE_SECURITY_NOTICE_REMOVAL = 'A2',
  CHANGE_SECURITY_NOTICE_AMENDED= 'A3'
}

export enum UIAmendmentTypes {
  AMENDMENT = 'Amendment',
  CHANGE_COLLATERAL_ADDITION = 'Amendment - Collateral Added',
  CHANGE_COLLATERAL_SUBSTITUTION = 'Amendment - Collateral Amended',
  CHANGE_DEBTOR_RELEASE = 'Amendment - Debtors Deleted',
  CHANGE_DEBTOR_TRANSFER = 'Amendment - Debtors Amended',
  CHANGE_PARTIAL_DISCHARGE = 'Amendment - Collateral Deleted',
  CHANGE_REGISTRY_CORRECTION = 'Registry Correction',
  CHANGE_SECURED_PARTY_TRANSFER = 'Amendment - Secured Parties Amended',
  COURT_ORDER = 'Amendment - Court Order',
  COLLATERAL_ADDITION = 'Amendment - Collateral Added',
  COLLATERAL_SUBSTITUTION = 'Amendment - Collateral Amended',
  DEBTOR_TRANSFER = 'Amendment - Debtors Amended',
  DEBTOR_RELEASE = 'Amendment - Debtors Deleted',
  DISCHARGE = 'Discharge',
  RENEWAL = 'Renewal',
  PARTIAL_DISCHARGE = 'Amendment - Collateral Deleted',
  SECURED_PARTY_TRANSFER = 'Amendment - Secured Parties Amended',
  CHANGE_SECURITY_NOTICE_ADDITION = 'Amendment - Notice Added',
  CHANGE_SECURITY_NOTICE_REMOVAL = 'Amendment - Notice Removed',
  CHANGE_SECURITY_NOTICE_AMENDED= 'Amendment - Notice Amended'
}

export enum UIRegistrationClassTypes {
  PPSALIEN = 'Registration Verification',
  RENEWAL = 'Renewal Verification',
  AMENDMENT = 'Amendment Verification',
  CHANGE = 'Change Verification',
  CROWNLIEN = 'Registration Verification',
  MISCLIEN = 'Registration Verification',
  COURTORDER = 'Amendment Verification',
  DISCHARGE = 'Discharge Verification'
}

export enum APIMhrDescriptionTypes {
  REGISTER_NEW_UNIT = 'MANUFACTURED HOME REGISTRATION',
  RE_REGISTER_NEW_UNIT = 'MANUFACTURED HOME RE-REGISTRATION',
  CONVERTED = 'RECORD CONVERSION',

  SALE_OR_GIFT = 'TRANSFER DUE TO SALE OR GIFT',
  TRANS_FAMILY_ACT = 'TRANSFER DUE TO FAMILY MAINTENANCE ACT',
  TRANS_INFORMAL_SALE = 'TRANSFER WITH AN INFORMAL BILL OF SALE',
  TRANS_QUIT_CLAIM = 'TRANSFER DUE TO QUIT CLAIM',
  TRANS_SEVER_GRANT = 'TRANSFER DUE TO SEVERING JOINT TENANCY',
  TRANS_RECEIVERSHIP = 'TRANSFER DUE TO RECEIVERSHIP',
  TRANS_WRIT_SEIZURE = 'TRANSFER DUE TO WRIT OF SEIZURE AND SALE',

  SURVIVING_JOINT_TENANT = 'TRANSFER TO SURVIVING JOINT TENANT(S)',
  // \u2013 is a less common dash, returned by the API, do not confuse it with ASCII char (\u002d)
  TRANSFER_EXECUTOR_PROBATE_WILL = 'TRANSFER TO EXECUTOR \u2013 GRANT OF PROBATE WITH WILL',
  TRANSFER_EXECUTOR_UNDER_25_WILL = 'TRANSFER TO EXECUTOR \u2013 ESTATE UNDER $25,000 WITH WILL',
  TRANSFER_ADMINISTRATOR = 'TRANSFER TO ADMINISTRATOR \u2013 GRANT OF ADMINISTRATION',
  RESIDENTIAL_EXEMPTION = 'RESIDENTIAL EXEMPTION',
  NON_RESIDENTIAL_EXEMPTION = 'NON-RESIDENTIAL EXEMPTION',

  ABAN = 'TRANSFER DUE TO ABANDONMENT AND SALE',
  BANK = 'TRANSFER DUE TO BANKRUPTCY',
  COU = 'TRANSFER DUE TO COURT ORDER',
  FORE = 'TRANSFER DUE TO FORECLOSURE ORDER',
  GENT = 'TRANSFER DUE TO GENERAL TRANSMISSION',
  TRANS_LAND_TITLE = 'TRANSFER DUE TO LAND TITLE',
  REIV = 'TRANSFER DUE TO REPOSSESSION \u2013 INVOLUNTARY',
  REPV = 'RETRANSFER DUE TO REPOSSESSION \u2013 VOLUNTARY',
  SZL = 'TRANSFER DUE TO SEIZURE UNDER LAND ACT',
  TAXS = 'TRANSFER DUE TO TAX SALE',
  VEST = 'TRANSFER DUE TO VESTING ORDER'
}

export enum UIMhrDescriptionTypes {
  REGISTER_NEW_UNIT = 'Manufactured Home Registration',
  CONVERTED = 'Record Conversion',

  SALE_OR_GIFT = 'Transfer Due to Sale or Gift',
  TRANS_FAMILY_ACT = 'Transfer Due to Family Maintenance Act',
  TRANS_INFORMAL_SALE = 'Transfer with an Informal Bill of Sale',
  TRANS_QUIT_CLAIM = 'Transfer Due to Quit Claim',
  TRANS_SEVER_GRANT = 'Transfer Due to Severing Joint Tenancy',
  TRANS_RECEIVERSHIP = 'Transfer Due to Receivership',
  TRANS_WRIT_SEIZURE = 'Transfer Due to Writ of Seizure and Sale',

  SURVIVING_JOINT_TENANT = 'Transfer to Surviving Joint Tenant(s)',
  TRANSFER_EXECUTOR_PROBATE_WILL = 'Transfer to Executor - Grant of Probate with Will',
  TRANSFER_EXECUTOR_UNDER_25_WILL = 'Transfer to Executor - Estate under $25,000 with Will',
  TRANSFER_ADMINISTRATOR = 'Transfer to Administrator - Grant of Administration',

  ABAN = 'Transfer Due to Abandonment and Sale',
  BANK = 'Transfer Due to Bankruptcy',
  COU = 'Transfer Due to Court Order',
  FORE = 'Transfer Due to Foreclosure Order',
  GENT = 'Transfer Due to General Transmission',
  TRANS_LAND_TITLE = 'Transfer Due to Land Title',
  REIV = 'Transfer Due to Repossession - Involuntary',
  REPV = 'Transfer Due to Repossession - Voluntary',
  SZL = 'Transfer Due to Seizure under Land Act',
  TAXS = 'Transfer Due to Tax Sale',
  VEST = 'Transfer Due to Vesting Order'
}

export enum APIMhrTypes {
  TRANSFER_OF_SALE = 'TRANS',
  TRANSFER_DUE_TO_DEATH = 'TRAND',
  NON_RESIDENTIAL_EXEMPTION = 'EXEMPTION_NON_RES',
  RESIDENTIAL_EXEMPTION = 'EXEMPTION_RES',
  MANUFACTURED_HOME_REGISTRATION = 'MHREG',
  TRANSPORT_PERMIT = 'PERMIT',
  REGISTRY_STAFF_ADMIN = 'REG_STAFF_ADMIN'
}

/**
 * Map MHR Registration Descriptions to the Document Types (eg. for MHR table filtering)
 */
export const mapMhrDescriptionToCodes = {
  [APIMhrDescriptionTypes.REGISTER_NEW_UNIT]: 'REG_101',
  [APIMhrDescriptionTypes.CONVERTED]: 'CONV',

  [APIMhrDescriptionTypes.SALE_OR_GIFT]: 'TRAN',
  [APIMhrDescriptionTypes.TRANS_FAMILY_ACT]: 'TRANS_FAMILY_ACT',
  [APIMhrDescriptionTypes.TRANS_INFORMAL_SALE]: 'TRANS_INFORMAL_SALE',
  [APIMhrDescriptionTypes.TRANS_QUIT_CLAIM]: 'TRANS_QUIT_CLAIM',
  [APIMhrDescriptionTypes.TRANS_SEVER_GRANT]: 'TRANS_SEVER_GRANT',
  [APIMhrDescriptionTypes.TRANS_RECEIVERSHIP]: 'TRANS_RECEIVERSHIP',
  [APIMhrDescriptionTypes.TRANS_WRIT_SEIZURE]: 'TRANS_WRIT_SEIZURE',
  [APIMhrDescriptionTypes.SURVIVING_JOINT_TENANT]: 'DEAT',

  [APIMhrDescriptionTypes.TRANSFER_EXECUTOR_PROBATE_WILL]: 'WILL',
  [APIMhrDescriptionTypes.TRANSFER_EXECUTOR_UNDER_25_WILL]: 'AFFE',
  [APIMhrDescriptionTypes.TRANSFER_ADMINISTRATOR]: 'LETA',
  [APIMhrDescriptionTypes.RESIDENTIAL_EXEMPTION]: 'EXRS',
  [APIMhrDescriptionTypes.NON_RESIDENTIAL_EXEMPTION]: 'EXNR',

  [APIMhrDescriptionTypes.ABAN]: 'ABAN',
  [APIMhrDescriptionTypes.BANK]: 'BANK',
  [APIMhrDescriptionTypes.COU]: 'COU',
  [APIMhrDescriptionTypes.FORE]: 'FORE',
  [APIMhrDescriptionTypes.GENT]: 'GENT',
  [APIMhrDescriptionTypes.TRANS_LAND_TITLE]: 'TRANS_LAND_TITLE',
  [APIMhrDescriptionTypes.REIV]: 'REIV',
  [APIMhrDescriptionTypes.REPV]: 'REPV',
  [APIMhrDescriptionTypes.SZL]: 'SZL',
  [APIMhrDescriptionTypes.TAXS]: 'TAXS',
  [APIMhrDescriptionTypes.VEST]: 'VEST'
}
