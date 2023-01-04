export enum APIRegistrationTypes {
  // standard
  SECURITY_AGREEMENT = 'SA',
  REPAIRERS_LIEN = 'RL',
  MARRIAGE_MH = 'FR',
  SALE_OF_GOODS = 'SG',
  LAND_TAX_LIEN = 'LT',
  MANUFACTURED_HOME_LIEN = 'MH',
  FORESTRY_CONTRACTOR_LIEN = 'FL',
  FORESTRY_CONTRACTOR_CHARGE = 'FA',
  FORESTRY_SUBCONTRACTOR_LIEN = 'FS',
  // miscelaneous registration cc
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
  TRANSPORT_PERMIT = 'PERMIT'
}

export enum UIRegistrationTypes {
  // standard
  SECURITY_AGREEMENT = 'Security Agreement',
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
  NON_RESIDENTIAL_EXEMPTION = 'None Residential Exemption',
  RESIDENTIAL_EXEMPTION = 'Residential Exemption',
  TRANSPORT_PERMIT = 'Transport Permit'
}

export enum StatementTypes {
  AMENDMENT_STATEMENT = 'AMENDMENT',
  CHANGE_STATEMENT = 'CHANGE',
  DISHCARGE_STATEMENT = 'DISCHARGE',
  FINANCING_STATEMENT = 'FINANCING',
  RENEWAL_STATEMENT = 'RENEWAL',
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
  SECURED_PARTY_TRANSFER = 'AS' // Only adding and removing a secured party.
}

export enum UIAmendmentTypes {
  AMENDMENT = 'Amendment',
  CHANGE_COLLATERAL_ADDITION = 'Amendment - Collateral Added',
  CHANGE_COLLATERAL_SUBSTITUTION = 'Amendment - Collateral Amended',
  CHANGE_DEBTOR_RELEASE = 'Amendment - Debtors Deletede',
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
  SECURED_PARTY_TRANSFER = 'Amendment - Secured Parties Amended'
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
  REGISTER_NEW_UNIT = 'REGISTER NEW UNIT',
  SALE_OR_GIFT = 'SALE / GIFT TRANSFER',
  CONVERTED = '** CONVERTED **'
}

export enum UIMhrDescriptionTypes {
  REGISTER_NEW_UNIT = 'REGISTER NEW UNIT',
  SALE_OR_GIFT = 'SALE OR GIFT',
  CONVERTED = 'CONVERTED'
}

export enum APIMhrTypes {
  TRANSFER_OF_SALE = 'TRANS',
  TRANSFER_DUE_TO_DEATH = 'TRAND',
  NON_RESIDENTIAL_EXEMPTION = 'EXEMPTION_NON_RES',
  RESIDENTIAL_EXEMPTION = 'EXEMPTION_RES',
  MANUFACTURED_HOME_REGISTRATION = 'MHREG',
  TRANSPORT_PERMIT = 'PERMIT'
}
