import { AddressIF } from '@/composables/address/interfaces'
import {ActionTypes, ApiHomeTenancyTypes, HomeOwnerPartyTypes} from '@/enums'

export interface MhrRegistrationHomeOwnerIF {
  ownerId?: number // optional property used for editing a home owner
  groupId?: number
  action?: ActionTypes
  individualName?: {
    first: string
    middle: string
    last: string
  },
  suffix?: string
  organizationName?: string
  phoneNumber: string
  phoneExtension: string
  address: AddressIF
  deathCertificateNumber?: string
  deathDateTime?: string
  partyType?: HomeOwnerPartyTypes
  type?: ApiHomeTenancyTypes
}
