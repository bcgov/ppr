
// General collateral interface.
export interface GeneralCollateralIF {
  description: string, // Max length 4000.
  collateralId?: number // System generated, included on success, used for amendment/change registrations.
}
