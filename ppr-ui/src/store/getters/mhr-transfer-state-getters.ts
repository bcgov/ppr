import { StateIF, SubmittingPartyIF } from '@/interfaces'

export const getMhrTransferDeclaredValue = (state: StateIF): number => {
  return state.stateModel.mhrTransfer.declaredValue
}

export const getMhrTransferConsideration = (state: StateIF): string => {
  return state.stateModel.mhrTransfer.consideration
}

export const getMhrTransferDate = (state: StateIF): string => {
  return state.stateModel.mhrTransfer.transferDate
}

export const getMhrTransferOwnLand = (state: StateIF): boolean => {
  return state.stateModel.mhrTransfer.ownLand
}

export const getMhrTransferSubmittingParty = (state: StateIF): SubmittingPartyIF => {
  return state.stateModel.mhrTransfer.submittingParty
}

export const getMhrTransferAttentionReference = (state: StateIF): string => {
  return state.stateModel.mhrTransfer.attentionReference
}
