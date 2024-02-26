import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeLocationIF,
  SubmittingPartyIF
} from '@/interfaces'
import { APIRegistrationTypes } from '@/enums'
export interface MhrRegistrationIF {
  draftNumber: string
  documentId?: string
  registrationType?: APIRegistrationTypes
  clientReferenceId: string
  declaredValue: string
  submittingParty: SubmittingPartyIF
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  attentionReference: string
  isManualLocationInfo: boolean
  ownLand: boolean
  location: MhrRegistrationHomeLocationIF
  description: MhrRegistrationDescriptionIF
}

export interface NewMhrRegistrationApiIF {
  draftNumber?: string
  documentId?: string
  clientReferenceId?: string
  declaredValue?: string
  submittingParty: SubmittingPartyIF,
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  location: MhrRegistrationHomeLocationIF
  description: MhrRegistrationDescriptionIF
  attentionReference?: string
  isManualLocationInfo?: boolean
  ownLand?: boolean
  notes?: [
    {
      documentType: string
      documentId: string
      createDateTime: string
      remarks: string
      contactName: string
      contactAddress: {
        street: string
        city: string
        region: string
        postalCode: string
        country: string
      }
    }
  ]
}
