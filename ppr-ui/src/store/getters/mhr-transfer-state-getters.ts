import {
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
  StateIF,
  SubmittingPartyIF,
  TransferTypeSelectIF
} from '@/interfaces'

// Home Owners
export const getMhrTransferHomeOwners = (state: StateIF): MhrRegistrationHomeOwnerIF[] => {
  const owners = []
  state.stateModel.mhrTransfer.ownerGroups.forEach(group => {
    if (group.owners.length === 0) {
      // Groups with no owners should have at least one 'placeholder' owner
      // to be properly displayed in Group Table
      owners.push({ groupId: group.groupId })
    } else {
      group.owners.forEach(owner => owners.push({ ...owner, groupId: group.groupId }))
    }
  })
  return owners
}

export const getMhrTransferCurrentHomeOwners = (state: StateIF): MhrRegistrationHomeOwnerGroupIF[] => {
  const ownerGroups = []

  state.stateModel.mhrTransfer.currentOwnerGroups.forEach(group => {
    ownerGroups.push(group)
  })
  return ownerGroups
}

export const getMhrTransferHomeOwnerGroups = (state: StateIF): MhrRegistrationHomeOwnerGroupIF[] => {
  return state.stateModel.mhrTransfer.ownerGroups
}

export const getMhrTransferCurrentHomeOwnerGroups = (state: StateIF): MhrRegistrationHomeOwnerGroupIF[] => {
  return state.stateModel.mhrTransfer.currentOwnerGroups
}

// Ownership Transfers
export const getMhrTransferType = (state: StateIF): TransferTypeSelectIF => {
  return state.stateModel.mhrTransfer.transferType
}

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
