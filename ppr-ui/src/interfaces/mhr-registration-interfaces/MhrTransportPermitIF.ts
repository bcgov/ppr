import { LocationChangeTypes } from "@/enums"
import { MhrRegistrationHomeLocationIF, SubmittingPartyIF } from "@/interfaces"

export interface MhrTransportPermitIF {
  documentId?: string
  clientReferenceId?: string
  attentionReference?: string
  submittingParty: SubmittingPartyIF,
  locationChangeType: LocationChangeTypes,
  newLocation: MhrRegistrationHomeLocationIF,
  ownLand: boolean,
  landStatusConfirmation?: boolean,
  amendment?: boolean
}
