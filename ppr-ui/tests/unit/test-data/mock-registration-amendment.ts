import { ActionTypes, APIAmendmentTypes, APIVehicleTypes, DraftTypes, RegistrationFlowType } from '@/enums'
import {
  CourtOrderIF,
  CertifyIF,
  DebtorNameIF,
  DraftIF,
  GeneralCollateralIF,
  PartyIF,
  VehicleCollateralIF,
  StateModelIF,
  AmendmentStatementIF, MhrTransferValidationStateIF, MhrTransferIF
} from '@/interfaces'
import {
  mockedAddress1,
  mockedRegisteringParty1,
  mockedSelectSecurityAgreement
} from './mock-registration-new'

const mockedDebtorName: DebtorNameIF = {
  businessName: 'TEST DEBTOR INC.'
}

// Mock data to set in state model for unit tests.
export const mockedAmendmentCourtOrder: CourtOrderIF = {
  courtName: 'court name',
  courtRegistry: 'court registry',
  fileNumber: 'file#',
  orderDate: '2021-09-03T18:00:00+00:00',
  effectOfOrder: 'effect of order'
}

export const mockedAmendmentCertified: CertifyIF = {
  valid: true,
  certified: true,
  legalName: 'Authorizing Name',
  registeringParty: mockedRegisteringParty1
}

export const mockedGeneralCollateralAdd: GeneralCollateralIF[] = [
  {
    addedDateTime: '2021-09-16T05:56:20Z',
    descriptionAdd: 'ADD TEST GENERAL COLLATERAL'
  },
  {
    collateralId: 100000,
    addedDateTime: '2021-09-16T05:56:20Z',
    description: 'UNCHANGED TEST GENERAL COLLATERAL'
  }
]
export const mockedGeneralCollateralDelete: GeneralCollateralIF[] = [
  {
    descriptionDelete: 'NEW DELETE TEST GENERAL COLLATERAL'
  },
  {
    collateralId: 100000,
    addedDateTime: '2021-09-16T05:56:20Z',
    descriptionDelete: 'PREVIOUSLY DELETE TEST GENERAL COLLATERAL'
  },
  {
    collateralId: 300000,
    addedDateTime: '2021-09-16T05:56:20Z',
    description: 'UNCHANGED TEST GENERAL COLLATERAL'
  }
]
export const mockedGeneralCollateralEdit: GeneralCollateralIF[] = [
  {
    collateralId: 0,
    addedDateTime: '2021-09-16T05:56:20Z',
    descriptionAdd: 'ADD TEST GENERAL COLLATERAL',
    descriptionDelete: 'DELETE TEST GENERAL COLLATERAL'
  },
  {
    collateralId: 300000,
    addedDateTime: '2021-09-16T05:56:20Z',
    description: 'UNCHANGED TEST GENERAL COLLATERAL'
  }
]

export const mockedVehicleCollateralAdd: VehicleCollateralIF[] = [
  {
    id: 1,
    type: APIVehicleTypes.MOTOR_VEHICLE,
    serialNumber: 'KM8J3CA46JU622994',
    year: 2018,
    make: 'HYUNDAI',
    model: 'TUSCON ADDED',
    action: ActionTypes.ADDED
  },
  {
    id: 100000,
    vehicleId: 100000,
    type: APIVehicleTypes.BOAT,
    serialNumber: '123456789',
    year: 2010,
    make: 'CREST LINER',
    model: '1700 VISION UNCHANGED'
  }
]
export const mockedVehicleCollateralDelete: VehicleCollateralIF[] = [
  {
    id: 100000,
    vehicleId: 100000,
    type: APIVehicleTypes.MOTOR_VEHICLE,
    serialNumber: 'KM8J3CA46JU622994',
    year: 2018,
    make: 'HYUNDAI',
    model: 'TUSCON REMOVED',
    action: ActionTypes.REMOVED
  },
  {
    id: 200000,
    vehicleId: 200000,
    type: APIVehicleTypes.BOAT,
    serialNumber: '123456789',
    year: 2010,
    make: 'CREST LINER',
    model: '1700 VISION UNCHANGED'
  }
]
export const mockedVehicleCollateralEdit: VehicleCollateralIF[] = [
  {
    id: 100000,
    vehicleId: 100000,
    type: APIVehicleTypes.MOTOR_VEHICLE,
    serialNumber: 'KM8J3CA46JU622994',
    year: 2018,
    make: 'HYUNDAI',
    model: 'TUSCON EDITED',
    action: ActionTypes.EDITED
  },
  {
    id: 200000,
    vehicleId: 200000,
    type: APIVehicleTypes.BOAT,
    serialNumber: '123456789',
    year: 2010,
    make: 'CREST LINER',
    model: '1700 VISION UNCHANGED'
  }
]

export const mockedSecuredPartiesAdd: PartyIF[] = [
  {
    personName: {
      last: 'ADD INDIVIDUAL PARTY',
      first: 'TEST'
    },
    emailAddress: 'test@person.com',
    address: mockedAddress1,
    action: ActionTypes.ADDED
  },
  {
    partyId: 300000,
    personName: {
      last: 'UNCHANGED INDIVIDUAL PARTY',
      first: 'TEST'
    },
    emailAddress: 'test@person.com',
    address: mockedAddress1
  }
]
export const mockedSecuredPartiesDelete: PartyIF[] = [
  {
    partyId: 100000,
    personName: {
      last: 'Delete INDIVIDUAL PARTY',
      first: 'TEST'
    },
    emailAddress: 'test@person.com',
    address: mockedAddress1,
    action: ActionTypes.REMOVED
  },
  {
    partyId: 300000,
    personName: {
      last: 'UNCHANGED INDIVIDUAL PARTY',
      first: 'TEST'
    },
    emailAddress: 'test@person.com',
    address: mockedAddress1
  }
]
export const mockedSecuredPartiesEdit: PartyIF[] = [
  {
    partyId: 100000,
    personName: {
      last: 'Edit INDIVIDUAL PARTY',
      first: 'TEST'
    },
    emailAddress: 'test@person.com',
    address: mockedAddress1,
    action: ActionTypes.EDITED
  },
  {
    partyId: 300000,
    personName: {
      last: 'UNCHANGED INDIVIDUAL PARTY',
      first: 'TEST'
    },
    emailAddress: 'test@person.com',
    address: mockedAddress1
  }
]

export const mockedDebtorsAdd: PartyIF[] = [
  {
    personName: {
      last: 'ADD INDIVIDUAL DEBTOR',
      first: 'TEST',
      middle: '1'
    },
    birthDate: '1990-06-15T16:42:00-08:00',
    address: mockedAddress1,
    action: ActionTypes.ADDED
  },
  {
    partyId: 300000,
    personName: {
      last: 'UNCHANGED DEBTOR',
      first: 'PERSON'
    },
    birthDate: '1990-06-15T16:42:00-08:00',
    address: mockedAddress1
  }
]
export const mockedDebtorsDelete: PartyIF[] = [
  {
    partyId: 100000,
    personName: {
      last: 'DELETE INDIVIDUAL DEBTOR',
      first: 'TEST',
      middle: '1'
    },
    birthDate: '1990-06-15T16:42:00-08:00',
    address: mockedAddress1,
    action: ActionTypes.REMOVED
  },
  {
    partyId: 300000,
    personName: {
      last: 'UNCHANGED DEBTOR',
      first: 'PERSON'
    },
    birthDate: '1990-06-15T16:42:00-08:00',
    address: mockedAddress1
  }
]
export const mockedDebtorsEdit: PartyIF[] = [
  {
    partyId: 100000,
    personName: {
      last: 'EDIT INDIVIDUAL DEBTOR',
      first: 'TEST',
      middle: '1'
    },
    birthDate: '1990-06-15T16:42:00-08:00',
    address: mockedAddress1,
    action: ActionTypes.EDITED
  },
  {
    partyId: 300000,
    personName: {
      last: 'UNCHANGED DEBTOR',
      first: 'PERSON'
    },
    birthDate: '1990-06-15T16:42:00-08:00',
    address: mockedAddress1
  }
]

export const mockedDebtorsExisting: PartyIF[] = [{
  partyId: 100000,
  personName: {
    last: 'EXISTING DEBTOR',
    first: 'TEST',
    middle: '1'
  },
  address: mockedAddress1
}]
export const mockedSecuredPartiesExisting: PartyIF[] = [{
  partyId: 100000,
  personName: {
    last: 'EXISTING SECURED PARTY',
    first: 'TEST',
    middle: '1'
  },
  address: mockedAddress1
}]
export const mockedVehicleCollateralExisting: VehicleCollateralIF[] = [{
  id: 100000,
  vehicleId: 100000,
  type: APIVehicleTypes.MOTOR_VEHICLE,
  serialNumber: 'KM8J3CA46JU622994',
  year: 2018,
  make: 'HYUNDAI',
  model: 'TUSCON EXISTING'
}]
export const mockedGeneralCollateralExisting: GeneralCollateralIF[] = [{
  collateralId: 100000,
  addedDateTime: '2021-09-16T05:56:20Z',
  description: 'UNCHANGED TEST GENERAL COLLATERAL'
}]
export const mockedGeneralCollateralNew: GeneralCollateralIF[] = [{
  addedDateTime: '2021-09-16T05:56:20Z',
  description: 'NEW TEST GENERAL COLLATERAL'
}]
export const mockedGeneralCollateralUpdate: GeneralCollateralIF[] = [{
  collateralId: 100000,
  addedDateTime: '2021-09-16T05:56:20Z',
  description: 'ADD / DELETE TEST GENERAL COLLATERAL'
}]

export const mockedAmendmentStatement1: AmendmentStatementIF = {
  documentId: 'D0034002',
  baseRegistrationNumber: '023003B',
  description: 'Test',
  registeringParty: mockedRegisteringParty1,
  changeType: APIAmendmentTypes.AMENDMENT,
  debtorName: mockedDebtorName
}
export const mockedDraftAmendmentStatement: DraftIF = {
  type: DraftTypes.AMENDMENT_STATEMENT,
  amendmentStatement: mockedAmendmentStatement1
}

export const mockedAmendmentAdd: AmendmentStatementIF = {
  documentId: 'D0034002',
  baseRegistrationNumber: '023003B',
  description: 'Test Add',
  registeringParty: mockedRegisteringParty1,
  changeType: APIAmendmentTypes.AMENDMENT,
  debtorName: mockedDebtorName,
  addDebtors: [mockedDebtorsAdd[0]],
  deleteDebtors: [],
  addSecuredParties: [mockedSecuredPartiesAdd[0]],
  deleteSecuredParties: [],
  addGeneralCollateral: mockedGeneralCollateralNew,
  deleteGeneralCollateral: [],
  addVehicleCollateral: [mockedVehicleCollateralAdd[0]],
  deleteVehicleCollateral: []
}
export const mockedAmendmentCourtOrderInfo: AmendmentStatementIF = {
  documentId: 'D0034002',
  baseRegistrationNumber: '023003B',
  description: 'Test Add',
  registeringParty: mockedRegisteringParty1,
  changeType: APIAmendmentTypes.AMENDMENT,
  debtorName: mockedDebtorName,
  courtOrderInformation: mockedAmendmentCourtOrder,
  addDebtors: [],
  deleteDebtors: [],
  addSecuredParties: [],
  deleteSecuredParties: [],
  addGeneralCollateral: [],
  deleteGeneralCollateral: [],
  addVehicleCollateral: [],
  deleteVehicleCollateral: []
}

export const mockedAmendmentDelete: AmendmentStatementIF = {
  documentId: 'D0034002',
  baseRegistrationNumber: '023003B',
  description: 'Test Delete',
  registeringParty: mockedRegisteringParty1,
  changeType: APIAmendmentTypes.AMENDMENT,
  debtorName: mockedDebtorName,
  deleteDebtors: [mockedDebtorsDelete[0]],
  addDebtors: [],
  deleteSecuredParties: [mockedSecuredPartiesDelete[0]],
  addSecuredParties: [],
  deleteGeneralCollateral: mockedGeneralCollateralUpdate,
  addGeneralCollateral: [],
  deleteVehicleCollateral: [mockedVehicleCollateralDelete[0]],
  addVehicleCollateral: []
}

export const mockedAmendmentEdit: AmendmentStatementIF = {
  documentId: 'D0034002',
  baseRegistrationNumber: '023003B',
  description: 'Test Edit',
  registeringParty: mockedRegisteringParty1,
  changeType: APIAmendmentTypes.AMENDMENT,
  addTrustIndenture: true,
  debtorName: mockedDebtorName,
  addDebtors: [mockedDebtorsEdit[0]],
  deleteDebtors: [mockedDebtorsEdit[0]],
  addSecuredParties: [mockedSecuredPartiesEdit[0]],
  deleteSecuredParties: [mockedSecuredPartiesEdit[0]],
  addGeneralCollateral: mockedGeneralCollateralUpdate,
  deleteGeneralCollateral: mockedGeneralCollateralUpdate,
  addVehicleCollateral: [mockedVehicleCollateralEdit[0]],
  deleteVehicleCollateral: [mockedVehicleCollateralEdit[0]]
}

export const mockedAmendmentResponse: AmendmentStatementIF = {
  documentId: '',
  baseRegistrationNumber: '023003B',
  description: 'Test Edit',
  registeringParty: mockedRegisteringParty1,
  changeType: APIAmendmentTypes.AMENDMENT,
  addTrustIndenture: true,
  debtorName: mockedDebtorName,
  addDebtors: [mockedDebtorsEdit[0]],
  deleteDebtors: [mockedDebtorsEdit[0]],
  addSecuredParties: [mockedSecuredPartiesEdit[0]],
  deleteSecuredParties: [mockedSecuredPartiesEdit[0]],
  addGeneralCollateral: mockedGeneralCollateralUpdate,
  deleteGeneralCollateral: mockedGeneralCollateralUpdate,
  addVehicleCollateral: [mockedVehicleCollateralEdit[0]],
  deleteVehicleCollateral: [mockedVehicleCollateralEdit[0]],
  amendmentRegistrationNumber: '023003B',
  createDateTime: '2021-09-03T21:00:00+00:00',
  payment: {
    invoiceId: '12535',
    receipt: '/api/v1/payment-requests/12535/receipts'
  }
}

export const mockedDraftAmendmentAdd: DraftIF = {
  type: DraftTypes.AMENDMENT_STATEMENT,
  amendmentStatement: mockedAmendmentAdd
}
export const mockedDraftAmendmentDelete: DraftIF = {
  type: DraftTypes.AMENDMENT_STATEMENT,
  amendmentStatement: mockedAmendmentDelete
}
export const mockedDraftAmendmentEdit: DraftIF = {
  type: DraftTypes.AMENDMENT_STATEMENT,
  amendmentStatement: mockedAmendmentEdit
}
export const mockedDraftAmendmentCourtOrder: DraftIF = {
  type: DraftTypes.AMENDMENT_STATEMENT,
  amendmentStatement: mockedAmendmentCourtOrderInfo
}

export const mockedModelAmendmdmentAdd: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  userProductSubscriptions: [],
  userProductSubscriptionsCodes: [],
  authorization: {
    authRoles: [],
    isSbc: false
  },
  certifyInformation: mockedAmendmentCertified,
  staffPayment: null,
  registration: {
    amendmentDescription: 'Adding',
    collateral: {
      valid: false,
      vehicleCollateral: mockedVehicleCollateralAdd,
      generalCollateral: mockedGeneralCollateralAdd
    },
    confirmDebtorName: mockedDebtorName,
    courtOrderInformation: null,
    creationDate: '',
    draft: {
      type: null,
      financingStatement: null,
      amendmentStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    },
    expiryDate: '',
    lengthTrust: {
      valid: false,
      showInvalid: false,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    registrationNumber: '0023001B',
    registrationType: mockedSelectSecurityAgreement(),
    registrationFlowType: RegistrationFlowType.AMENDMENT,
    registrationTypeOtherDesc: null,
    showStepErrors: false,
    parties: {
      valid: false,
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredPartiesAdd,
      debtors: mockedDebtorsAdd
    }
  },
  mhrRegistration: null,
  registrationTable: null,
  originalRegistration: {
    collateral: {
      valid: true,
      vehicleCollateral: [],
      generalCollateral: []
    },
    lengthTrust: {
      valid: true,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    parties: {
      valid: true,
      registeringParty: null,
      securedParties: [],
      debtors: []
    }
  },
  search: {
    searchDebtorName: null,
    searchHistory: null,
    searchHistoryLength: null,
    searchResults: null,
    manufacturedHomeSearchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false,
    searchCertified: false
  },
  userInfo: {
    contacts: [],
    feeSettings: {
      isNonBillable: false,
      serviceFee: 1.50
    },
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      defaultDropDowns: true,
      defaultTableFilters: true,
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  folioOrReferenceNumber: 'UT-AM-001-ADD',
  unsavedChanges: false,
  selectedManufacturedHomes: null,
  isStaffClientPayment: null,
  mhrSearchResultSelectAllLien: false,
  mhrInformation: null,
  mhrTransferValidationState: null,
  mhrTransfer: null
}

export const mockedModelAmendmdmentDelete: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  userProductSubscriptions: [],
  userProductSubscriptionsCodes: [],
  authorization: {
    authRoles: [],
    isSbc: false
  },
  certifyInformation: mockedAmendmentCertified,
  staffPayment: null,
  registration: {
    amendmentDescription: 'Deleting',
    collateral: {
      valid: false,
      vehicleCollateral: mockedVehicleCollateralDelete,
      generalCollateral: mockedGeneralCollateralDelete
    },
    confirmDebtorName: mockedDebtorName,
    courtOrderInformation: null,
    creationDate: '',
    draft: {
      type: null,
      financingStatement: null,
      amendmentStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    },
    expiryDate: '',
    lengthTrust: {
      valid: false,
      showInvalid: false,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    registrationNumber: '0023001B',
    registrationType: mockedSelectSecurityAgreement(),
    registrationFlowType: RegistrationFlowType.AMENDMENT,
    registrationTypeOtherDesc: null,
    showStepErrors: false,
    parties: {
      valid: false,
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredPartiesDelete,
      debtors: mockedDebtorsDelete
    }
  },
  mhrRegistration: null,
  registrationTable: null,
  originalRegistration: {
    collateral: {
      valid: true,
      vehicleCollateral: [],
      generalCollateral: []
    },
    lengthTrust: {
      valid: true,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    parties: {
      valid: true,
      registeringParty: null,
      securedParties: [],
      debtors: []
    }
  },
  search: {
    searchDebtorName: null,
    searchHistory: null,
    searchHistoryLength: null,
    searchResults: null,
    manufacturedHomeSearchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false,
    searchCertified: false
  },
  userInfo: {
    contacts: [],
    feeSettings: {
      isNonBillable: false,
      serviceFee: 1.50
    },
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      defaultDropDowns: true,
      defaultTableFilters: true,
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  folioOrReferenceNumber: 'UT-AM-002-DELETE',
  unsavedChanges: false,
  selectedManufacturedHomes: null,
  isStaffClientPayment: null,
  mhrSearchResultSelectAllLien: false,
  mhrInformation: null,
  mhrTransferValidationState: null,
  mhrTransfer: null
}

export const mockedModelAmendmdmentEdit: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  userProductSubscriptions: [],
  userProductSubscriptionsCodes: [],
  authorization: {
    authRoles: [],
    isSbc: false
  },
  certifyInformation: mockedAmendmentCertified,
  staffPayment: null,
  registration: {
    amendmentDescription: 'Editing',
    collateral: {
      valid: false,
      vehicleCollateral: mockedVehicleCollateralEdit,
      generalCollateral: mockedGeneralCollateralEdit
    },
    confirmDebtorName: mockedDebtorName,
    courtOrderInformation: null,
    creationDate: '',
    draft: {
      type: null,
      financingStatement: null,
      amendmentStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    },
    expiryDate: '',
    lengthTrust: {
      valid: false,
      showInvalid: false,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: true,
      lienAmount: '',
      surrenderDate: '',
      action: ActionTypes.EDITED
    },
    registrationNumber: '0023001B',
    registrationType: mockedSelectSecurityAgreement(),
    registrationFlowType: RegistrationFlowType.AMENDMENT,
    registrationTypeOtherDesc: null,
    showStepErrors: false,
    parties: {
      valid: false,
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredPartiesEdit,
      debtors: mockedDebtorsEdit
    }
  },
  mhrRegistration: null,
  registrationTable: null,
  originalRegistration: {
    collateral: {
      valid: true,
      vehicleCollateral: [],
      generalCollateral: []
    },
    lengthTrust: {
      valid: true,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    parties: {
      valid: true,
      registeringParty: null,
      securedParties: [],
      debtors: []
    }
  },
  search: {
    searchDebtorName: null,
    searchHistory: null,
    searchHistoryLength: null,
    searchResults: null,
    manufacturedHomeSearchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false,
    searchCertified: false
  },
  userInfo: {
    contacts: [],
    feeSettings: {
      isNonBillable: false,
      serviceFee: 1.50
    },
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      defaultDropDowns: true,
      defaultTableFilters: true,
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  folioOrReferenceNumber: 'UT-AM-003-EDIT',
  unsavedChanges: false,
  selectedManufacturedHomes: null,
  isStaffClientPayment: null,
  mhrSearchResultSelectAllLien: false,
  mhrInformation: null,
  mhrTransferValidationState: null,
  mhrTransfer: null
}

export const mockedModelAmendmdmentCourtOrder: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  userProductSubscriptions: [],
  userProductSubscriptionsCodes: [],
  authorization: {
    authRoles: [],
    isSbc: false
  },
  certifyInformation: mockedAmendmentCertified,
  staffPayment: null,
  registration: {
    amendmentDescription: 'Court Order',
    collateral: {
      valid: false,
      vehicleCollateral: [],
      generalCollateral: []
    },
    confirmDebtorName: mockedDebtorName,
    courtOrderInformation: mockedAmendmentCourtOrder,
    creationDate: '',
    draft: {
      type: null,
      financingStatement: null,
      amendmentStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    },
    expiryDate: '',
    lengthTrust: {
      valid: false,
      showInvalid: false,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    registrationNumber: '0023001B',
    registrationType: mockedSelectSecurityAgreement(),
    registrationFlowType: RegistrationFlowType.AMENDMENT,
    registrationTypeOtherDesc: null,
    showStepErrors: false,
    parties: {
      valid: false,
      registeringParty: mockedRegisteringParty1,
      securedParties: [],
      debtors: []
    }
  },
  mhrRegistration: null,
  registrationTable: null,
  originalRegistration: {
    collateral: {
      valid: true,
      vehicleCollateral: [],
      generalCollateral: []
    },
    lengthTrust: {
      valid: true,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    parties: {
      valid: true,
      registeringParty: null,
      securedParties: [],
      debtors: []
    }
  },
  search: {
    searchDebtorName: null,
    searchHistory: null,
    searchHistoryLength: null,
    searchResults: null,
    manufacturedHomeSearchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false,
    searchCertified: false
  },
  userInfo: {
    contacts: [],
    feeSettings: {
      isNonBillable: false,
      serviceFee: 1.50
    },
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      defaultDropDowns: true,
      defaultTableFilters: true,
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  folioOrReferenceNumber: 'UT-AM-004-COURT-ORDER',
  unsavedChanges: false,
  selectedManufacturedHomes: null,
  isStaffClientPayment: null,
  mhrSearchResultSelectAllLien: false,
  mhrInformation: null,
  mhrTransferValidationState: null,
  mhrTransfer: null
}
