import { LocationChangeTypes } from "@/enums"
import { MhrRegistrationHomeLocationIF, SubmittingPartyIF } from "@/interfaces"

export interface MhrTransportPermitIF {
  clientReferenceId?: string
  documentId?: string
  submittingParty: SubmittingPartyIF,
  locationChangeType: LocationChangeTypes,
  newLocation: MhrRegistrationHomeLocationIF,
  ownLand: boolean,
  landStatusConfirmation?: boolean,
  amendment?: boolean
}
