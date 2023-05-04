export enum ApiTransferTypes {
  SALE_OR_GIFT = 'TRANS',
  SURVIVING_JOINT_TENANT = 'TRAND',
  TO_EXECUTOR_UNDER_25K_WILL = 'TRANS_AFFIDAVIT',
  TO_ADMIN_NO_WILL = 'TRANS_ADMIN',
  TO_EXECUTOR_PROBATE_WILL = 'TRANS_WILL'
}

export enum UITransferTypes {
  SALE_OR_GIFT = 'Transfer Due to Sale or Gift',
  SURVIVING_JOINT_TENANT = 'Transfer to Surviving Joint Tenant(s)',
  TO_EXECUTOR_UNDER_25K_WILL = 'Transfer to Executor - Estate under $25,000 with Will',
  TO_ADMIN_NO_WILL = 'Transfer to Administrator - Grant of Administration',
  TO_EXECUTOR_PROBATE_WILL = 'Transfer to Executor - Grant of Probate with Will'
}

export enum SupportingDocumentsOptions {
  PROBATE_GRANT = 'PROBATE_GRANT',
  DEATH_CERT = 'DEATH_CERT',
  AFFIDAVIT = 'AFFIDAVIT',
  ADMIN_GRANT = 'ADMIN_GRANT'
}
