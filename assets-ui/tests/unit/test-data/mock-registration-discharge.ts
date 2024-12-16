import { APIRegistrationTypes } from '@/enums'
import { DischargeRegistrationIF, FinancingStatementIF, RenewRegistrationIF } from '@/interfaces'
import {
  mockedDebtors1,
  mockedGeneralCollateral2,
  mockedRegisteringParty1,
  mockedSecuredParties1,
  mockedVehicleCollateral1
} from './mock-registration-new'
import { mockedDebtorNames } from './mock-debtor-names'

export const mockedFinancingStatementComplete: FinancingStatementIF = {
  baseRegistrationNumber: '123456B',
  clientReferenceId: 'UT-100001',
  createDateTime: '2021-07-20T17:21:17+00:00',
  expiryDate: '2026-07-20T06:59:59+00:00',
  type: APIRegistrationTypes.SECURITY_AGREEMENT,
  registeringParty: mockedRegisteringParty1,
  securedParties: mockedSecuredParties1,
  debtors: mockedDebtors1,
  vehicleCollateral: mockedVehicleCollateral1,
  generalCollateral: mockedGeneralCollateral2,
  lifeYears: 5,
  trustIndenture: false,
  lifeInfinite: false,
  payment: {
    invoiceId: '',
    receipt: ''
  }
}

export const mockedAmendmentStatementComplete: FinancingStatementIF = {
  baseRegistrationNumber: '123456B',
  clientReferenceId: 'UT-100001',
  createDateTime: '2021-07-20T17:21:17+00:00',
  expiryDate: '2026-07-20T06:59:59+00:00',
  type: APIRegistrationTypes.SECURITY_AGREEMENT,
  registeringParty: mockedRegisteringParty1,
  securedParties: mockedSecuredParties1,
  debtors: mockedDebtors1,
  vehicleCollateral: mockedVehicleCollateral1,
  generalCollateral: mockedGeneralCollateral2,
  lifeYears: 5,
  trustIndenture: false,
  lifeInfinite: false,
  payment: {
    invoiceId: '',
    receipt: ''
  }
}

export const mockedDischargeResponse: DischargeRegistrationIF = {
  debtorName: mockedDebtorNames[0],
  baseRegistrationNumber: '123456B',
  clientReferenceId: 'UT-100001',
  createDateTime: '2021-07-20T17:21:17+00:00',
  registeringParty: mockedRegisteringParty1,
  dischargeRegistrationNumber: '223456B',
  payment: {
    invoiceId: '',
    receipt: ''
  }
}

export const mockedRenewalResponse: RenewRegistrationIF = {
  debtorName: mockedDebtorNames[0],
  baseRegistrationNumber: '123456B',
  clientReferenceId: 'UT-100001',
  createDateTime: '2021-07-20T17:21:17+00:00',
  registeringParty: mockedRegisteringParty1,
  expiryDate: '2025-08-01T06:59:59+00:00',
  renewalRegistrationNumber: '123457B',
  payment: {
    invoiceId: '',
    receipt: ''
  }
}
