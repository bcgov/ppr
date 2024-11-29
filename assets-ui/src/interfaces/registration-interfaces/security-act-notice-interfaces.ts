import { ActionTypes, SaNoticeTypes } from '@/enums'
import { CourtOrderIF } from '@/interfaces'

export interface AddEditSaNoticeIF {
  noticeId?: number
  amendNoticeId?: number // to associate amended notice to removed notice
  securitiesActNoticeType: SaNoticeTypes
  effectiveDateTime: string
  securitiesActOrders?: Array<CourtOrderIF>
  action?: ActionTypes
}
