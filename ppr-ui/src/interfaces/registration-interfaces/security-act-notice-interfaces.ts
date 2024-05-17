import { SaNoticeTypes } from '@/enums'
import { CourtOrderIF } from '@/interfaces'

export interface AddEditSaNoticeIF {
  securitiesActNoticeType: SaNoticeTypes
  effectiveDate: string
  securitiesActOrders?: Array<CourtOrderIF>
}
