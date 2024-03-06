import { APIRegistrationTypes, MhApiStatusTypes } from '@/enums'
import {
  MhrHomeOwnerGroupIF,
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  SubmittingPartyIF
} from '@/interfaces'

/**
 * Interface describing the various admin registrations.
 * Most content blocks are optional, as the correction type filings only include CHANGED information.
 */
export interface AdminRegistrationIF {
  clientReferenceId?: string
  attentionReference?: string
  documentType: APIRegistrationTypes
  documentId: string
  submittingParty: SubmittingPartyIF
  statusType?: MhApiStatusTypes
  location?: MhrRegistrationHomeLocationIF
  description?: MhrRegistrationDescriptionIF
  deleteOwnerGroups?: Array<MhrHomeOwnerGroupIF>
  addOwnerGroups?: Array<MhrHomeOwnerGroupIF>
}
