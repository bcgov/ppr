import { UIRegistrationTypes } from '@/enums'
import { FeeSummaryDefaults, FeeSummaryTypes } from '../enums'
import { FeeSummaryI, RegistrationLengthI } from '../interfaces'
import { defaultFeeSummaries } from '../resources'

export const hasNoCharge = (val: UIRegistrationTypes): boolean => {
  const hfArray = [
    UIRegistrationTypes.LAND_TAX_LIEN,
    UIRegistrationTypes.MANUFACTURED_HOME_LIEN,
    UIRegistrationTypes.LAND_TAX_LIEN,
    UIRegistrationTypes.MANUFACTURED_HOME_LIEN,
    UIRegistrationTypes.INSURANCE_PREMIUM_TAX,
    UIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
    UIRegistrationTypes.FOREST,
    UIRegistrationTypes.LOGGING_TAX,
    UIRegistrationTypes.CARBON_TAX,
    UIRegistrationTypes.RURAL_PROPERTY_TAX,
    UIRegistrationTypes.PROVINCIAL_SALES_TAX,
    UIRegistrationTypes.INCOME_TAX,
    UIRegistrationTypes.MOTOR_FUEL_TAX,
    UIRegistrationTypes.EXCISE_TAX,
    UIRegistrationTypes.LIEN_UNPAID_WAGES,
    UIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
    UIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
    UIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
    UIRegistrationTypes.MAINTENANCE_LIEN,
    UIRegistrationTypes.OTHER,
    UIRegistrationTypes.MINERAL_LAND_TAX,
    UIRegistrationTypes.PROPERTY_TRANSFER_TAX,
    UIRegistrationTypes.SCHOOL_ACT
  ]
  // it will not be in the UIRegistrationTypes enum list if 'Other' was selected
  return hfArray.includes(val) || !Object.values(UIRegistrationTypes).includes(val)
}

export function getFeeSummary (
  feeType: FeeSummaryTypes,
  registrationType: UIRegistrationTypes,
  registrationLength: RegistrationLengthI
): FeeSummaryI {
  if (feeType === FeeSummaryTypes.DISCHARGE) {
    return { ...defaultFeeSummaries[FeeSummaryDefaults.NO_FEE] }
  }
  if (feeType === FeeSummaryTypes.AMMEND) {
    // FUTURE: update this to the right one when doing amend work
    return { ...defaultFeeSummaries[FeeSummaryDefaults.NO_FEE] }
  }
  if ((feeType === FeeSummaryTypes.NEW) || (feeType === FeeSummaryTypes.RENEW)) {
    if (hasNoCharge(registrationType)) {
      return { ...defaultFeeSummaries[FeeSummaryDefaults.NO_FEE] }
    }
    if (registrationType === UIRegistrationTypes.REPAIRERS_LIEN) {
      return { ...defaultFeeSummaries[FeeSummaryDefaults.DEFAULT_5] }
    }
    if (registrationType === UIRegistrationTypes.MARRIAGE_MH) {
      return { ...defaultFeeSummaries[FeeSummaryDefaults.DEFAULT_10] }
    }
    // selected infinite
    if (registrationLength.lifeInfinite) {
      return { ...defaultFeeSummaries[FeeSummaryDefaults.DEFAULT_500] }
    }
    // selected years
    const selectYearsFeeSummary = { ...defaultFeeSummaries[FeeSummaryDefaults.SELECT_5] }
    selectYearsFeeSummary.quantity = registrationLength?.lifeYears || 0
    return selectYearsFeeSummary
  }
  // should not get here
  console.error('No fee summary implemented for this flow')
  return { ...defaultFeeSummaries[FeeSummaryDefaults.NO_FEE] }
}

export function getFeeHint (
  feeType: FeeSummaryTypes,
  registrationType: UIRegistrationTypes,
  registrationLength: RegistrationLengthI
): string {
  if ([FeeSummaryTypes.NEW, FeeSummaryTypes.RENEW].includes(feeType)) {
    if (hasNoCharge(registrationType) || registrationType === UIRegistrationTypes.MARRIAGE_MH) {
      return 'Infinite Registration (default)'
    }
    if (registrationType === UIRegistrationTypes.REPAIRERS_LIEN) {
      return '180 Day Registration (default)'
    }
    if (registrationLength.lifeInfinite) {
      return 'Infinite Registration'
    }
    if (registrationLength.lifeYears === 1) {
      return '1 Year @ $5.00/year'
    }
    if (registrationLength.lifeYears > 1) {
      return `${registrationLength.lifeYears} Years @ $5.00/year`
    }
    if (feeType === FeeSummaryTypes.RENEW) {
      return 'Select registration renewal length'
    }
    // selected years is 0
    return 'Select registration length'
  }
  return ''
}
