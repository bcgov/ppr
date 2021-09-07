import { FeeCodes } from "@/enums";

// Fee information interface.
export interface FeeIF {
  feeCode: FeeCodes,
  description?: string,
  hint?: string,
  quantityMin: number,
  quantityMax: number,
  feeAmount: number
}
