import { FeeCodes } from '../enums'
import { FeeI } from '../interfaces'

const SERVICE_FEE: number = 1.50

const SEARCH_FEE: FeeI = {
  feeCode: FeeCodes.SEARCH,
  description: 'Default search fee.',
  hint: '',
  quantityMin: 1,
  quantityMax: 1,
  feeAmount: 8.00
}

const FINANCING_INFINITE_FEE: FeeI = {
  feeCode: FeeCodes.FINANCING_INFINITE,
  description: 'Default infinite life new registration fee.',
  hint: 'Select registration length',
  quantityMin: 1,
  quantityMax: 1,
  feeAmount: 500.00
}

const FINANCING_YEAR_FEE: FeeI = {
  feeCode: FeeCodes.FINANCING_INFINITE,
  description: 'Default new registration fee for 1 year.',
  hint: 'Select registration length',
  quantityMin: 1,
  quantityMax: 25,
  feeAmount: 5.00
}

export function getSearchFee (): FeeI {
  return SEARCH_FEE
}

export function getSearchFeeAmount (includeServiceFee: boolean): number {
  return (SEARCH_FEE.feeAmount + (includeServiceFee ? SERVICE_FEE : 0.0))
}

export function getFinancingFee (infinite: boolean): FeeI {
  return infinite ? FINANCING_INFINITE_FEE : FINANCING_YEAR_FEE
}

export function getFinancingFeeAmount (years: number, infinite: boolean, includeServiceFee: boolean): number {
  if (infinite) {
    return (FINANCING_INFINITE_FEE.feeAmount + (includeServiceFee ? SERVICE_FEE : 0.0))
  }
  return (FINANCING_YEAR_FEE.feeAmount * years + (includeServiceFee ? SERVICE_FEE : 0.0))
}

export function getServiceFee (): number {
  return SERVICE_FEE
}
