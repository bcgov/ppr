import {
  ActionIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrTransferIF,
  SubmittingPartyIF,
  TransferTypeSelectIF
} from '@/interfaces'
import { ApiTransferTypes } from '@/enums/transferTypes'

export const setEmptyMhrTransfer: ActionIF = ({ commit }, emptyMhrTransfer: MhrTransferIF): void => {
  commit('mutateEmptyMhrTransfer', emptyMhrTransfer)
}

export const setMhrTransferHomeOwnerGroups: ActionIF = (
  { commit },
  groups: MhrRegistrationHomeOwnerGroupIF[]
): void => {
  commit('mutateMhrTransferHomeOwnerGroups', groups)
  commit('mutateUnsavedChanges', true)
}

// Set a snapshot of the MH Registration home owner groups
export const setMhrTransferCurrentHomeOwnerGroups: ActionIF = (
  { commit },
  groups: MhrRegistrationHomeOwnerGroupIF[]
): void => {
  commit('mutateMhrTransferCurrentHomeOwnerGroups', groups)
}

export const setMhrTransferType: ActionIF = ({ commit }, transferType: TransferTypeSelectIF): void => {
  commit('mutateMhrTransferType', transferType)
}

export const setMhrTransferDeclaredValue: ActionIF = ({ commit }, declaredValue: number): void => {
  commit('mutateMhrTransferDeclaredValue', declaredValue)
}

export const setMhrTransferConsideration: ActionIF = ({ commit }, consideration: string): void => {
  commit('mutateMhrTransferConsideration', consideration)
}

export const setMhrTransferDate: ActionIF = ({ commit }, transferDate: string): void => {
  commit('mutateMhrTransferDate', transferDate)
}

export const setMhrTransferOwnLand: ActionIF = ({ commit }, isOwnLand: boolean): void => {
  commit('mutateMhrTransferOwnLand', isOwnLand)
}

export const setMhrTransferSubmittingPartyKey: ActionIF = ({ commit }, { key, value }): void => {
  commit('mutateMhrTransferSubmittingPartyKey', { key, value })
}

export const setMhrTransferSubmittingParty: ActionIF = ({ commit }, submittingPartyInfo: SubmittingPartyIF): void => {
  commit('mutateMhrTransferSubmittingParty', submittingPartyInfo)
}

export const setMhrTransferAttentionReference: ActionIF = ({ commit }, attentionReference: string): void => {
  commit('mutateMhrTransferAttentionReference', attentionReference)
}
