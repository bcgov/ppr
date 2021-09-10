
// New registration life and trust indenture interface.
export interface RegistrationLengthI {
  lifeInfinite: boolean,
  lifeYears: number, // 1..25 if not lifeInfinite, otherwise 0.
}
