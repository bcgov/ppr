export enum ErrorCategories {
  ACCOUNT_ACCESS = 'account-access',
  ACCOUNT_SETTINGS = 'account-settings',
  CREATE_DOCUMENT_ACCESS_REQUEST = 'create-document-access-request',
  DOCUMENT_DOWNLOAD = 'document-download',
  DOCUMENT_ID = 'document-id',
  DRAFT_DELETE = 'draft-delete',
  DRAFT_LOAD = 'draft-load',
  ENTITY_BASIC = 'entity-basic',
  FEE_INFO = 'fee-info',
  HISTORY_REGISTRATIONS = 'history-registrations',
  HISTORY_SEARCHES = 'history-searches',
  PRODUCT_ACCESS = 'product-access',
  REGISTRATION_CREATE = 'registration-create',
  REGISTRATION_DELETE = 'registration-delete',
  REGISTRATION_LOAD = 'registration-load',
  REGISTRATION_SAVE = 'registration-save',
  REGISTRATION_TRANSFER = 'registration-transfer',
  REGISTRATION_TRANSFER_SAVE = 'registration-transfer-save',
  TRANSFER_DRAFT_STALE = 'transfer-draft-stale',
  TRANSFER_OUT_OF_DATE_OWNERS = 'transfer-out-of-date-owners',
  REPORT_GENERATION = 'report-generation',
  SEARCH = 'search',
  SEARCH_COMPLETE = 'search-complete',
  SEARCH_UPDATE = 'search-update',
  LTSA_REQUEST = 'ltsa-request',
  MHR_UNIT_NOTE_FILING = 'mhr-unit-note-filing',
  EXEMPTION_SAVE = 'exemption-save',
  TRANSPORT_PERMIT_FILING = 'mhr-transport-permit-filing',
  USER_ACCESS_PRODUCT_REQUEST = 'user-access-product-request'
}

/**
 * RootCause Api Error Enum
 * These string snippets/values should derive directly from api error responses.
 * **/
export enum ErrorRootCauses {
  OUT_OF_DATE_DRAFT = 'The draft for this registration is out of date',
  // Potential Future update: Api specific messaging for outdated owners
  OUT_OF_DATE_OWNERS = `^.*The owner group with ID \\d+ is not active and cannot be changed.*$`
}
