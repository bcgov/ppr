import { MhrRegistrationHomeOwnerGroupIF, MhrTransferIF, StateIF, SubmittingPartyIF } from '@/interfaces'
import { set } from 'lodash'

export const mutateEmptyMhrTransfer = (state: StateIF, emptyMhrTransfer: MhrTransferIF) => {
  state.stateModel.mhrTransfer = emptyMhrTransfer
}

// Home Owners
export const mutateMhrTransferHomeOwnerGroups = (
  state: StateIF,
  groups: Array<MhrRegistrationHomeOwnerGroupIF>
) => {
  state.stateModel.mhrTransfer.ownerGroups = groups
}

export const mutateMhrTransferCurrentHomeOwnerGroups = (
  state: StateIF,
  groups: Array<MhrRegistrationHomeOwnerGroupIF>
) => {
  state.stateModel.mhrTransfer.currentOwnerGroups = groups
}

// Ownership Transfer
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

export const mutateMhrTransferSubmittingPartyKey = (state: StateIF, { key, value }) => {
  set(state.stateModel.mhrTransfer.submittingParty, key, value)
}

export const mutateMhrTransferSubmittingParty = (state: StateIF, submittingPartyInfo: SubmittingPartyIF) => {
  state.stateModel.mhrTransfer.submittingParty = submittingPartyInfo
}

export const mutateMhrTransferAttentionReference = (state: StateIF, attentionReference: string) => {
  state.stateModel.mhrTransfer.attentionReference = attentionReference
}
