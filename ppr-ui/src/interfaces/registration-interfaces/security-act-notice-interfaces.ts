import { ActionTypes, SaNoticeTypes } from '@/enums'
import { CourtOrderIF } from '@/interfaces'

export interface AddEditSaNoticeIF {
  noticeId?: number
  securitiesActNoticeType: SaNoticeTypes
  effectiveDateTime: string
  securitiesActOrders?: Array<CourtOrderIF>
  action?: ActionTypes
}
