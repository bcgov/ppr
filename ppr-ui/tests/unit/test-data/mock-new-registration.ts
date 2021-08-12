import { APIRegistrationTypes, DraftTypes, UIRegistrationTypes, APIVehicleTypes } from '@/enums'
import {
  AddPartiesIF,
  AddCollateralIF,
  AddressIF,
  DraftIF,
  FinancingStatementIF,
  GeneralCollateralIF,
  ErrorIF,
  LengthTrustIF,
  PaymentIF,
  PartyIF,
  RegistrationTypeIF,
  VehicleCollateralIF,
  SearchPartyIF
} from '@/interfaces'

export const mockedSelectSecurityAgreement: RegistrationTypeIF = {
  class: 'registration-list-item',
  divider: false,
  disabled: false,
  group: 3,
  registrationTypeUI: UIRegistrationTypes.SECURITY_AGREEMENT,
  registrationTypeAPI: APIRegistrationTypes.SECURITY_AGREEMENT,
  text: `${UIRegistrationTypes.SECURITY_AGREEMENT} (${APIRegistrationTypes.SECURITY_AGREEMENT})`
}

export const mockedRepairersLien: RegistrationTypeIF = {
  class: 'registration-list-item',
  divider: false,
  disabled: false,
  group: 3,
  registrationTypeUI: UIRegistrationTypes.REPAIRERS_LIEN,
  registrationTypeAPI: APIRegistrationTypes.REPAIRERS_LIEN,
  text: ''
}

export const mockedSaleOfGoods: RegistrationTypeIF = {
  class: 'registration-list-item',
  divider: false,
  disabled: false,
  group: 3,
  registrationTypeUI: UIRegistrationTypes.SALE_OF_GOODS,
  registrationTypeAPI: APIRegistrationTypes.SALE_OF_GOODS,
  text: ''
}

export const mockedMarriageMH: RegistrationTypeIF = {
  class: 'registration-list-item',
  divider: false,
  disabled: false,
  group: 3,
  registrationTypeUI: UIRegistrationTypes.MARRIAGE_MH,
  registrationTypeAPI: APIRegistrationTypes.MARRIAGE_MH,
  text: ''
}

export const mockedError: ErrorIF = {
  statusCode: 500,
  message: 'mock error'
}

export const mockedAddress1: AddressIF = {
  street: '1234 Fort St.',
  streetAdditional: '2nd floor',
  city: 'Victoria',
  region: 'BC',
  country: 'CA',
  postalCode: 'V8R1L2',
  deliveryInstructions: ''
}

export const mockedGeneralCollateral1: string = 'TEST1 GENERAL COLLATERAL'

export const mockedGeneralCollateral2: Array<GeneralCollateralIF> = [
  {
    description: 'TEST1 GENERAL COLLATERAL'
  }
]

export const mockedVehicleCollateral1: Array<VehicleCollateralIF> = [
  {
    id: 1,
    type: APIVehicleTypes.MOTOR_VEHICLE,
    serialNumber: 'KM8J3CA46JU622994',
    year: 2018,
    make: 'HYUNDAI',
    model: 'TUSCON'
  },
  {
    id: 2,
    type: APIVehicleTypes.BOAT,
    serialNumber: '123456789',
    year: 2010,
    make: 'CREST LINER',
    model: '1700 VISION'
  }
]

export const mockedPayment1: PaymentIF = {
  invoiceId: '2198743',
  receipt: '/pay/api/v1/payment-requests/2198743/receipts'
}

export const mockedRegisteringParty1: PartyIF = {
  businessName: 'ABC REGISTERING COMPANY LTD.',
  address: mockedAddress1
}

export const mockedSecuredParties1: Array<PartyIF> = [
  {
    businessName: 'SECURED PARTY COMPANY LTD.',
    emailAddress: 'test@company.com',
    address: mockedAddress1
  }
]

export const mockedSecuredParties2: Array<PartyIF> = [
  {
    personName: {
      last: 'INDIVIDUAL PARTY',
      first: 'TEST'
    },
    emailAddress: 'test@person.com',
    address: mockedAddress1
  }
]

export const mockedDebtors1: Array<PartyIF> = [
  {
    personName: {
      last: 'INDIVIDUAL DEBTOR',
      first: 'TEST',
      middle: '1'
    },
    birthDate: '1990-06-15T16:42:00-08:00',
    address: mockedAddress1
  }
]

export const mockedDebtors2: Array<PartyIF> = [
  {
    businessName: 'SOMEBODYS BUSINESS',
    address: mockedAddress1
  }
]

export const mockedNewRegStep1: LengthTrustIF = {
  valid: false,
  lifeYears: 5,
  lifeInfinite: false,
  trustIndenture: true
}

export const mockedNewRegStep2: AddPartiesIF = {
  valid: false,
  registeringParty: mockedRegisteringParty1,
  securedParties: mockedSecuredParties1,
  debtors: mockedDebtors1
}

export const mockedNewRegStep3: AddCollateralIF = {
  valid: false,
  vehicleCollateral: mockedVehicleCollateral1,
  generalCollateral: 'TEST GENERAL COLLATERAL'
}

export const mockedFinancingStatementAll: FinancingStatementIF = {
  type: APIRegistrationTypes.SECURITY_AGREEMENT,
  clientReferenceId: 'UT-100001',
  registeringParty: mockedRegisteringParty1,
  securedParties: mockedSecuredParties1,
  debtors: mockedDebtors1,
  vehicleCollateral: mockedVehicleCollateral1,
  generalCollateral: mockedGeneralCollateral2,
  lifeYears: 5,
  trustIndenture: false,
  lifeInfinite: false
}

export const mockedFinancingStatementStep1: FinancingStatementIF = {
  type: APIRegistrationTypes.SECURITY_AGREEMENT,
  clientReferenceId: 'UT-100002',
  registeringParty: null,
  securedParties: [],
  debtors: [],
  vehicleCollateral: [],
  generalCollateral: [],
  lifeYears: 5,
  trustIndenture: false,
  lifeInfinite: false
}

export const mockedFinancingStatementStep2: FinancingStatementIF = {
  type: APIRegistrationTypes.SECURITY_AGREEMENT,
  clientReferenceId: 'UT-100004',
  registeringParty: mockedRegisteringParty1,
  securedParties: mockedSecuredParties1,
  debtors: mockedDebtors1,
  vehicleCollateral: [],
  generalCollateral: [],
  trustIndenture: true,
  lifeInfinite: true
}

export const mockedFinancingStatementStep3: FinancingStatementIF = {
  type: APIRegistrationTypes.SECURITY_AGREEMENT,
  clientReferenceId: 'UT-100005',
  registeringParty: mockedRegisteringParty1,
  securedParties: [],
  debtors: [],
  vehicleCollateral: mockedVehicleCollateral1,
  generalCollateral: mockedGeneralCollateral2,
  trustIndenture: true,
  lifeYears: 2,
  lifeInfinite: false
}

export const mockedDraftFinancingStatementAll: DraftIF = {
  type: DraftTypes.FINANCING_STATEMENT,
  financingStatement: mockedFinancingStatementAll
}
export const mockedDraftFinancingStatementStep1: DraftIF = {
  type: DraftTypes.FINANCING_STATEMENT,
  financingStatement: mockedFinancingStatementStep1
}
export const mockedDraftFinancingStatementStep2: DraftIF = {
  type: DraftTypes.FINANCING_STATEMENT,
  financingStatement: mockedFinancingStatementStep2
}
export const mockedDraftFinancingStatementStep3: DraftIF = {
  type: DraftTypes.FINANCING_STATEMENT,
  financingStatement: mockedFinancingStatementStep3
}

export const mockedPartyCodeSearchResponse: Array<SearchPartyIF> = [{
  businessName: 'SOMEBODYS BUSINESS',
  code: '123',
  address: mockedAddress1
},
{
  businessName: 'SOMEBODYS PARTY',
  code: '456',
  address: mockedAddress1
}]
