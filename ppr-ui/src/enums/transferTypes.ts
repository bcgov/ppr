export enum ApiTransferTypes {
  // Bill Of Sale Transfers
  SALE_OR_GIFT = 'TRANS',
  TRANS_FAMILY_ACT = 'TRANS_FAMILY_ACT',
  TRANS_INFORMAL_SALE = 'TRANS_INFORMAL_SALE',
  TRANS_QUIT_CLAIM = 'TRANS_QUIT_CLAIM',
  TRANS_RECEIVERSHIP = 'TRANS_RECEIVERSHIP',
  TRANS_SEVER_GRANT = 'TRANS_SEVER_GRANT',
  TRANS_WRIT_POSSESSION = 'TRANS_WRIT_POSSESSION',

  // Transfers Due to Death
  SURVIVING_JOINT_TENANT = 'TRAND',
  TO_EXECUTOR_UNDER_25K_WILL = 'TRANS_AFFIDAVIT',
  TO_ADMIN_NO_WILL = 'TRANS_ADMIN',
  TO_EXECUTOR_PROBATE_WILL = 'TRANS_WILL',

  // Other Transfers
  ABAN = 'ABAN',
  BANK = 'BANK',
  COU = 'COU',
  FORE = 'FORE',
  GENT = 'GENT',
  TRANS_LAND_TITLE = 'TRANS_LAND_TITLE',
  REIV = 'REIV',
  REPV = 'REPV',
  SZL = 'SZL',
  TAXS = 'TAXS',
  VEST = 'VEST'
}

export enum UITransferTypes {
  // Bill Of Sale Transfers
  SALE_OR_GIFT = 'Transfer Due to Sale or Gift',
  TRANS_FAMILY_ACT = 'Transfer Due to Family Maintenance Act',
  TRANS_INFORMAL_SALE = 'Transfer with an Informal Bill of Sale',
  TRANS_QUIT_CLAIM = 'Transfer Due to Quit Claim',
  TRANS_SEVER_GRANT = 'Transfer Due to Severing Joint Tenancy',
  TRANS_RECEIVERSHIP = 'Transfer Due to Receivership',
  TRANS_WRIT_POSSESSION = 'Transfer Due to Writ of Seizure and Sale',

  // Transfers Due to Death
  SURVIVING_JOINT_TENANT = 'Transfer to Surviving Joint Tenant(s)',
  TO_EXECUTOR_UNDER_25K_WILL = 'Transfer to Executor - Estate under $25,000 with Will',
  TO_ADMIN_NO_WILL = 'Transfer to Administrator - Grant of Administration',
  TO_EXECUTOR_PROBATE_WILL = 'Transfer to Executor - Grant of Probate with Will',

  // Other Transfers
  ABAN = 'Transfer Due to Abandonment and Sale',
  BANK = 'Transfer Due to Bankruptcy',
  COU = 'Transfer Due to Court Order',
  FORE = 'Transfer Due to Foreclosure Order',
  GENT = 'Transfer Due to General Transmission',
  TRANS_LAND_TITLE = 'Transfer Due to Land Title',
  REIV = 'Transfer Due to Repossession - Involuntary',
  REPV = 'Transfer Due to Repossession - Voluntary',
  SZL = 'Transfer Due to Seizure under Land Act',
  TAXS = 'Transfer Due to Tax Sale',
  VEST = 'Transfer Due to Vesting Order'
}

export enum SupportingDocumentsOptions {
  PROBATE_GRANT = 'PROBATE_GRANT',
  DEATH_CERT = 'DEATH_CERT',
  AFFIDAVIT = 'AFFIDAVIT',
  ADMIN_GRANT = 'ADMIN_GRANT'
}
