import { UIRegistrationTypes } from '@/enums'
import { FeeSummaryDefaults, FeeSummaryTypes } from '../enums'
import { FeeSummaryI, RegistrationLengthI } from '../interfaces'
import { defaultFeeSummaries } from '../resources'
import { isInt } from '@/utils'
import { getFinancingFee } from '@/composables/fees/factories'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { unitNotes } from '@/resources/mhr-transfers/unit-notes'

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
    UIRegistrationTypes.SCHOOL_ACT,
    UIRegistrationTypes.TOBACCO_TAX,
    UIRegistrationTypes.SPECULATION_VACANCY_TAX
  ]
  // it will not be in the UIRegistrationTypes enum list if 'Other' was selected
  return hfArray.includes(val) || !Object.values(UIRegistrationTypes).includes(val)
}

export const hasNoChargeAmendment = (val: UIRegistrationTypes): boolean => {
  const hfArray = [
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
    UIRegistrationTypes.MINERAL_LAND_TAX,
    UIRegistrationTypes.PROPERTY_TRANSFER_TAX,
    UIRegistrationTypes.OTHER,
    UIRegistrationTypes.SCHOOL_ACT,
    UIRegistrationTypes.LIEN_UNPAID_WAGES,
    UIRegistrationTypes.LAND_TAX_LIEN,
    UIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
    UIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
    UIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
    UIRegistrationTypes.MAINTENANCE_LIEN,
    UIRegistrationTypes.CROWN_MINING_TAX,
    UIRegistrationTypes.MISC_MINERAL_RESOURCE,
    UIRegistrationTypes.CROWN_CORP_CAPITAL_TAX,
    UIRegistrationTypes.CROWN_CONSUMPTION_TRANSITION_TAX,
    UIRegistrationTypes.CROWN_HOTEL_ROOM_TAX,
    UIRegistrationTypes.CROWN_SOCIAL_SERVICE_TAX,
    UIRegistrationTypes.TRANSITION_TAX_LIEN,
    UIRegistrationTypes.TOBACCO_TAX,
    UIRegistrationTypes.SPECULATION_VACANCY_TAX
  ]
  // it will not be in the UIRegistrationTypes enum list if 'Other' was selected
  return hfArray.includes(val) || !Object.values(UIRegistrationTypes).includes(val)
}

export function getFeeSummary (
  feeType: FeeSummaryTypes,
  registrationType: UIRegistrationTypes,
  registrationLength: RegistrationLengthI,
  isStaff: boolean = false,
  isStaffClientPayment: boolean = false
): FeeSummaryI {
  const {
    getMhrUnitNoteType
  } = storeToRefs(useStore())

  if (feeType === FeeSummaryTypes.MHSEARCH) {
    if (isStaff && isStaffClientPayment) return { ...defaultFeeSummaries[FeeSummaryDefaults.SEARCH_10] }
    if (isStaff) return { ...defaultFeeSummaries[FeeSummaryDefaults.NO_FEE] }
    return { ...defaultFeeSummaries[FeeSummaryDefaults.SEARCH_7] }
  }
  if (feeType === FeeSummaryTypes.NEW_MHR) {
    return { ...defaultFeeSummaries[FeeSummaryDefaults.DEFAULT_50] }
  }
  if (feeType === FeeSummaryTypes.MHR_COMBINED_SEARCH) {
    if (isStaff && isStaffClientPayment) return { ...defaultFeeSummaries[FeeSummaryDefaults.SEARCH_15] }
    if (isStaff) return { ...defaultFeeSummaries[FeeSummaryDefaults.NO_FEE] }
    return { ...defaultFeeSummaries[FeeSummaryDefaults.SEARCH_12] }
  }
  if (feeType === FeeSummaryTypes.MHR_TRANSFER) {
    return { ...defaultFeeSummaries[FeeSummaryDefaults.DEFAULT_50] }
  }
  if (feeType === FeeSummaryTypes.DISCHARGE) {
    return { ...defaultFeeSummaries[FeeSummaryDefaults.NO_FEE] }
  }
  if (feeType === FeeSummaryTypes.AMEND) {
    if (hasNoChargeAmendment(registrationType)) {
      return { ...defaultFeeSummaries[FeeSummaryDefaults.NO_FEE] }
    }
    return { ...defaultFeeSummaries[FeeSummaryDefaults.AMEND] }
  }
  if (feeType === FeeSummaryTypes.MHR_UNIT_NOTE) {
    const unitNoteFeeSummary = unitNotes[getMhrUnitNoteType.value].fee
    return { ...defaultFeeSummaries[unitNoteFeeSummary] }
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
    const feeInfoYears = getFinancingFee(false)
    if ((registrationLength.lifeYears) && ((!isInt(registrationLength.lifeYears) ||
      registrationLength.lifeYears < 1 || registrationLength.lifeYears > feeInfoYears.quantityMax))) {
      return 'Select a valid registration length'
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
