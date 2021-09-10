import { FeeCodes } from '../enums'

// Fee information interface.
export interface FeeI {
  feeCode: FeeCodes,
  description?: string,
  hint?: string,
  quantityMin: number,
  quantityMax: number,
  feeAmount: number
}
