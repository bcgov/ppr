import { SaNoticeTypes } from '@/enums'
import { CourtOrderIF } from '@/interfaces'

export interface AddEditSaNoticeIF {
  securitiesActNoticeType: SaNoticeTypes
  effectiveDateTime: string
  securitiesActOrders?: Array<CourtOrderIF>
}
