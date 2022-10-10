import { StateIF } from '@/interfaces'

export const mutateMhrTransferDeclaredValue = (state: StateIF, declaredValue: number) => {
  state.stateModel.mhrTransfer.declaredValue = declaredValue
}

export const mutateMhrTransferConsideration = (state: StateIF, consideration: string) => {
  state.stateModel.mhrTransfer.consideration = consideration
}

export const mutateMhrTransferDate = (state: StateIF, transferDate: string) => {
  state.stateModel.mhrTransfer.transferDate = transferDate
}

export const mutateMhrTransferOwnLand = (state: StateIF, isOwnLand: boolean) => {
  state.stateModel.mhrTransfer.ownLand = isOwnLand
}
