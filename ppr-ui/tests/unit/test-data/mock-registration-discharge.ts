import { APIRegistrationTypes } from '@/enums'
import { DischargeRegistrationIF, FinancingStatementIF } from '@/interfaces'
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
  expiryDate: '2026-07-20T17:21:17+00:00',
  type: APIRegistrationTypes.SECURITY_AGREEMENT,
  registeringParty: mockedRegisteringParty1,
  securedParties: mockedSecuredParties1,
  debtors: mockedDebtors1,
  vehicleCollateral: mockedVehicleCollateral1,
  generalCollateral: mockedGeneralCollateral2,
  lifeYears: 5,
  trustIndenture: false,
  lifeInfinite: false
}

export const mockedDischargeResponse: DischargeRegistrationIF = {
  debtorName: mockedDebtorNames[0],
  baseRegistrationNumber: '123456B',
  clientReferenceId: 'UT-100001',
  createDateTime: '2021-07-20T17:21:17+00:00',
  registeringParty: mockedRegisteringParty1,
  dischargeRegistrationNumber: '223456B'
}
