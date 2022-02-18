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
    OTHER = 'OT',
    // miscelaneous registration other
    LIEN_UNPAID_WAGES = 'WL',
    HERITAGE_CONSERVATION_NOTICE = 'HN',
    MANUFACTURED_HOME_NOTICE = 'MN',
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
    TRANSITION_MH = 'TM'
}

export enum UIRegistrationTypes {
    // standard
    SECURITY_AGREEMENT = 'Security Agreement',
    REPAIRERS_LIEN = 'Repairers Lien',
    MARRIAGE_MH = 'Marriage / Separation Agreement affecting Manufactured Home under Family Law Act',
    SALE_OF_GOODS = 'Possession under S.30 of the Sale of Goods Act',
    LAND_TAX_LIEN = 'Land Tax Deferment Lien on a Manufactured Home',
    MANUFACTURED_HOME_LIEN = 'Tax Lien under S.27/28 of the Manufactured Home Act',
    FORESTRY_CONTRACTOR_LIEN = 'Forestry - Contractor Lien',
    FORESTRY_CONTRACTOR_CHARGE = 'Forestry - Contractor Charge',
    FORESTRY_SUBCONTRACTOR_LIEN = 'Forestry - Sub-contractor Charge',
    // miscelaneous registration cc
    CARBON_TAX = 'Carbon Tax Act',
    EXCISE_TAX = 'Excise Tax Act',
    FOREST = 'Forest Act',
    INCOME_TAX = 'Income Tax Act',
    INSURANCE_PREMIUM_TAX = 'Insurance Premium Tax Act',
    LOGGING_TAX = 'Logging Tax Act',
    MINERAL_LAND_TAX = 'Mineral Land Tax Act',
    MOTOR_FUEL_TAX = 'Motor Fuel Tax Act',
    PROPERTY_TRANSFER_TAX = 'Property Transfer Tax Act',
    PETROLEUM_NATURAL_GAS_TAX = 'Petroleum and Natural Gas Act',
    PROVINCIAL_SALES_TAX = 'Provincial Sales Tax Act',
    RURAL_PROPERTY_TAX = 'Rural Property Tax Act',
    SCHOOL_ACT = 'School Act',
    OTHER = 'Other...',
    // miscelaneous registration other
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
    TRANSITION_MH = 'M.H. Transition'
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
    CHANGE_COLLATERAL_ADDITION = 'Collateral Addition',
    CHANGE_COLLATERAL_SUBSTITUTION = 'Collateral Substitution',
    CHANGE_DEBTOR_RELEASE = 'Debtor Release',
    CHANGE_DEBTOR_TRANSFER = 'Debtor Transfer',
    CHANGE_PARTIAL_DISCHARGE = 'Partial Discharge',
    CHANGE_REGISTRY_CORRECTION = 'Registry Correction',
    CHANGE_SECURED_PARTY_TRANSFER = 'Secured Party Transfer',
    COURT_ORDER = 'Court Order',
    COLLATERAL_ADDITION = 'Collateral Addition',
    COLLATERAL_SUBSTITUTION = 'Collateral Substitution',
    DEBTOR_TRANSFER = 'Debtor Transfer',
    DEBTOR_RELEASE = 'Debtor Release',
    DISCHARGE = 'Discharge',
    RENEWAL = 'Renewal',
    PARTIAL_DISCHARGE = 'Partial Discharge',
    SECURED_PARTY_TRANSFER = 'Secured Party Transfer'
}
