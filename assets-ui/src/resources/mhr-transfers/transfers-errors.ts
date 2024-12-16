import { ApiTransferTypes } from '@/enums'

/* eslint-disable max-len */
export const transfersErrors = {
  ownersMustBeDeceased: 'All individuals must be deceased and businesses dissolved or cancelled.',
  // Executors, Administrators and Trustees Owner Types
  eatOwnersMustBeDeleted: 'All executors, administrators, or bankruptcy trustees must be deleted.',
  // Transfer to Executor
  ownersMustBeDeceasedAndExecutorAdded: 'All individuals must be deceased and businesses dissolved or cancelled and ' +
    'an executor added.',
  mustContainOneExecutor: 'Must contain at least one executor.',
  mustContainOneExecutorInGroup: 'Group must contain at least one executor.',

  // Transfer to Administrator
  ownersMustBeDeceasedAndAdminAdded: 'All individuals must be deceased and businesses dissolved or cancelled and an' +
    ' administrator added.',
  mustContainOneAdmin: 'Must contain at least one administrator.',
  mustContainOneAdminInGroup: 'Group must contain at least one administrator.',

  noSupportingDocSelected: {
    [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
      'You must delete a deceased owner using Grant of Probate with Will, or delete an executor, before adding an executor',
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'You must delete a deceased owner using Affidavit of Executor before adding an executor',
    [ApiTransferTypes.TO_ADMIN_NO_WILL]:
      'You must delete a deceased owner using Grant of Administration, or delete an administrator, before adding an administrator'
  },
  declaredHomeValueMax: {
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'Declared value of home must not exceed $25,000 for this transfer type'
  },
  allOwnersHaveDeathCerts: {
    [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
      'One of the deceased owners must have a Grant of Probate with Will.',
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'One of the deceased owners must have an Affidavit of Executor with Death Certificate.',
    [ApiTransferTypes.TO_ADMIN_NO_WILL]:
      'One of the deceased owners must have a Grant of Administration.'
  }
}
