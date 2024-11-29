import { LocationChangeTypes } from "@/enums"
import { MhrRegistrationHomeLocationIF, SubmittingPartyIF } from "@/interfaces"

export interface MhrTransportPermitIF {
  documentId?: string
  clientReferenceId?: string
  attentionReference?: string
  moveCompleted?: boolean
  submittingParty: SubmittingPartyIF,
  locationChangeType: LocationChangeTypes,
  newLocation: MhrRegistrationHomeLocationIF,
  previousLocation?: MhrRegistrationHomeLocationIF, // used when cancelling the permits
  ownLand: boolean,
  landStatusConfirmation?: boolean,
  amendment?: boolean
  registrationStatus?: string // UI only prop for Amended badge
}
