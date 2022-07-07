import { APIRegistrationTypes } from '@/enums'

export const useGeneralCollateral = () => {
  const hasGeneralCollateral = (registrationType: APIRegistrationTypes): boolean => {
    const ghArray = [
      APIRegistrationTypes.SECURITY_AGREEMENT,
      APIRegistrationTypes.SALE_OF_GOODS,
      APIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
      APIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
      APIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN,
      APIRegistrationTypes.INSURANCE_PREMIUM_TAX,
      APIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
      APIRegistrationTypes.FOREST,
      APIRegistrationTypes.LOGGING_TAX,
      APIRegistrationTypes.CARBON_TAX,
      APIRegistrationTypes.RURAL_PROPERTY_TAX,
      APIRegistrationTypes.PROVINCIAL_SALES_TAX,
      APIRegistrationTypes.INCOME_TAX,
      APIRegistrationTypes.MOTOR_FUEL_TAX,
      APIRegistrationTypes.EXCISE_TAX,
      APIRegistrationTypes.LIEN_UNPAID_WAGES,
      APIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
      APIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
      APIRegistrationTypes.MAINTENANCE_LIEN,
      APIRegistrationTypes.OTHER,
      APIRegistrationTypes.MINERAL_LAND_TAX,
      APIRegistrationTypes.PROPERTY_TRANSFER_TAX,
      APIRegistrationTypes.SCHOOL_ACT,
      APIRegistrationTypes.MISC_MINERAL_RESOURCE,
      APIRegistrationTypes.CROWN_MINING_TAX,
      APIRegistrationTypes.CROWN_CORP_CAPITAL_TAX,
      APIRegistrationTypes.CROWN_CONSUMPTION_TRANSITION_TAX,
      APIRegistrationTypes.CROWN_HOTEL_ROOM_TAX,
      APIRegistrationTypes.CROWN_SOCIAL_SERVICE_TAX,
      APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT,
      APIRegistrationTypes.TRANSITION_FINANCING_STATEMENT,
      APIRegistrationTypes.TRANSITION_SALE_OF_GOODS,
      APIRegistrationTypes.TRANSITION_TAX_LIEN,
      APIRegistrationTypes.TRANSITION_MH,
      APIRegistrationTypes.TOBACCO_TAX,
      APIRegistrationTypes.SPECULATION_VACANCY_TAX
    ]
    return ghArray.includes(registrationType)
  }

  const hasGeneralCollateralText = (registrationType: APIRegistrationTypes): boolean => {
    const gcList = [
      APIRegistrationTypes.INSURANCE_PREMIUM_TAX,
      APIRegistrationTypes.LOGGING_TAX,
      APIRegistrationTypes.CARBON_TAX,
      APIRegistrationTypes.PROVINCIAL_SALES_TAX,
      APIRegistrationTypes.INCOME_TAX,
      APIRegistrationTypes.MOTOR_FUEL_TAX,
      APIRegistrationTypes.EXCISE_TAX,
      APIRegistrationTypes.TOBACCO_TAX,
      APIRegistrationTypes.SPECULATION_VACANCY_TAX
    ]
    return gcList.includes(registrationType)
  }

  return {
    hasGeneralCollateral,
    hasGeneralCollateralText
  }
}
