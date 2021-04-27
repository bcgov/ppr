
// Fee information interface.
export interface FeeIF {
  feeCode: string,
  description?: string,
  hint?: string,
  quantityMin: number,
  quantityMax: number,
  feeAmount: number
}
