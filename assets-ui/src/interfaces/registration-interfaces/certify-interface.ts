import { PartyIF } from '@/interfaces'

// New registration authorizing/certify check interface.
export interface CertifyIF {
  valid: boolean,
  certified: boolean,
  legalName: string,
  registeringParty?: PartyIF
}
