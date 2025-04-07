import type { APIRegistrationTypes, MhApiStatusTypes } from '@/enums'
import type {
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
  draftNumber?: string
  submittingParty: SubmittingPartyIF
  status?: MhApiStatusTypes
  location?: MhrRegistrationHomeLocationIF
  description?: MhrRegistrationDescriptionIF
  deleteOwnerGroups?: Array<MhrHomeOwnerGroupIF>
  addOwnerGroups?: Array<MhrHomeOwnerGroupIF>
  ownLand?: boolean
}
