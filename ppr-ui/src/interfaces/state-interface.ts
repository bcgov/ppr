import type { AccountModelIF, StateModelIF } from '@/interfaces'

// State model example
export interface StateIF {
  stateModel: StateModelIF
  account?: AccountModelIF
}
