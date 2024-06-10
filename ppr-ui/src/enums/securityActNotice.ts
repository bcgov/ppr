/** Security Act Notice Types: Aligned with API definitions **/
export enum SaNoticeTypes {
  NOTICE_OF_LIEN = 'LIEN',
  NOTICE_OF_PROCEEDINGS = 'PROCEEDINGS'
}

export enum SaNoticeTypesUI {
  NOTICE_OF_LIEN = 'Notice of Lien and Charge',
  NOTICE_OF_PROCEEDINGS = 'Notice of Proceedings'
}

export const saNoticeTypeMapping: Record<SaNoticeTypes, SaNoticeTypesUI> = {
  [SaNoticeTypes.NOTICE_OF_LIEN]: SaNoticeTypesUI.NOTICE_OF_LIEN,
  [SaNoticeTypes.NOTICE_OF_PROCEEDINGS]: SaNoticeTypesUI.NOTICE_OF_PROCEEDINGS
}
