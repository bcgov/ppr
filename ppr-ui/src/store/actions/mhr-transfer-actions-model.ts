import { ActionIF, SubmittingPartyIF } from '@/interfaces'

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

export const setMhrTransferSubmittingParty: ActionIF = ({ commit }, submittingPartyInfo: SubmittingPartyIF): void => {
  commit('mutateMhrTransferSubmittingParty', submittingPartyInfo)
}

export const setMhrTransferAttentionReference: ActionIF = ({ commit }, attentionReference: string): void => {
  commit('mutateMhrTransferAttentionReference', attentionReference)
}
