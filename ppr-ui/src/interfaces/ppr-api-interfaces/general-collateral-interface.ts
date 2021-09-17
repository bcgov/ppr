
// General collateral interface.
export interface GeneralCollateralIF {
  added: boolean
  addedDateTime?: string
  collateralId?: number // System generated, included on success, used for amendment/change registrations.
  description: string // Max length 4000.
  legacy: boolean
}
