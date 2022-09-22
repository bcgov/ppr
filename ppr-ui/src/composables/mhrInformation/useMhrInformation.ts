import { MhrTransferIF } from '@/interfaces'

export const useMhrInformation = () => {
  const initMhrTransfer = (): MhrTransferIF => {
    return {
      mhrNumber: '',
      ownerGroups: [],
      owners: [],
      submittingParty: {}
    }
  }

  return {
    initMhrTransfer
  }
}
