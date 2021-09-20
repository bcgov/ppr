
// General collateral interface.
export interface GeneralCollateralIF {
  addedDateTime?: string
  collateralId?: number // System generated, included on success, used for amendment/change registrations.
  description?: string // Max length 4000.
  descriptionAdd?: string // Max length 4000.
  descriptionDelete?: string // Max length 4000.
}
