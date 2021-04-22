
// New registration life and trust indenture interface.
export interface LengthTrustIF {
  valid: boolean,
  trustIndenture: boolean,
  lifeInfinite: boolean,
  lifeYears: number // 1..25 if not lifeInfinite, otherwise 0.
}
