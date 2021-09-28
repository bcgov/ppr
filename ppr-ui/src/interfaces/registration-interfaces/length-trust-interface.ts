import { ActionTypes } from '@/enums'

// New registration life and trust indenture interface.
export interface LengthTrustIF {
  valid: boolean,
  trustIndenture: boolean,
  lifeInfinite: boolean,
  lifeYears: number, // 1..25 if not lifeInfinite, otherwise 0.
  showInvalid?: boolean, // show the invalid component
  surrenderDate?: string, // RL only in ISO date format
  lienAmount?: string, // RL only.
  action?: ActionTypes // Amendment only, local state indicates trust indenture changed.
}
