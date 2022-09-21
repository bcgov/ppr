import { useGetters } from 'vuex-composition-helpers'
import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationIF,
  NewMhrRegistrationApiIF,
  MhrTransferIF
} from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'

export const useMhrInformation = () => {
  // const {
  //   getMhrRegistrationHomeDescription,
  //   getMhrRegistrationSubmittingParty,
  //   getMhrRegistrationDocumentId,
  //   getMhrAttentionReferenceNum,
  //   getMhrRegistrationLocation,
  //   getMhrRegistrationHomeOwnerGroups,
  //   getStaffPayment
  // } = useGetters<any>([
  //   'getMhrRegistrationHomeDescription',
  //   'getMhrRegistrationSubmittingParty',
  //   'getMhrRegistrationDocumentId',
  //   'getMhrAttentionReferenceNum',
  //   'getMhrRegistrationLocation',
  //   'getMhrRegistrationHomeOwnerGroups',
  //   'getCertifyInformation',
  //   'getStaffPayment'
  // ])

  const initMhrTransfer = (): MhrTransferIF => {
    return {
      mhrNumber: '',
      ownerGroups: [],
      owners: [],
      submittingParty: {}
    }
  }

  // const buildApiData = () => {
  //   const data: NewMhrRegistrationApiIF = {
  //     documentId: getMhrRegistrationDocumentId.value,
  //     submittingParty: parseSubmittingParty(),
  //     ownerGroups: parseOwnerGroups(),
  //     location: parseLocation(),
  //     description: parseDescription()
  //   }
  //
  //   if (getMhrAttentionReferenceNum.value) {
  //     data.attentionReferenceNum = getMhrAttentionReferenceNum.value
  //   }
  //
  //   return data
  // }

  return {
    initMhrTransfer
  }
}
