import { FeeSummaryDefaults } from '@/composables/fees/enums'
import { UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums'
import { PartyIF } from '@/interfaces'

export interface UnitNoteIF {
  documentType: UnitNoteDocTypes
  documentId?: string
  documentRegistrationNumber?: string
  documentDescription?: string
  createDateTime?: string
  effectiveDateTime?: string
  expiryDateTime?: string
  remarks?: string
  givingNoticeParty?: PartyIF
  status?: UnitNoteStatusTypes
  destroyed?: boolean
}

export interface UnitNoteInfoIF {
  header: string,
  dropdownText: string,
  dropdownIcon?: string,
  fee: FeeSummaryDefaults,
  reviewSectionNumber?: Record<string, number>,
  panelHeader?: string,
}
