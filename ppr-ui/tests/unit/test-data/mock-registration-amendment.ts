import { RegistrationFlowType, APIVehicleTypes, ActionTypes } from '@/enums'
import {
  CourtOrderIF,
  GeneralCollateralIF,
  PartyIF,
  VehicleCollateralIF,
  StateModelIF
} from '@/interfaces'
import {
  mockedAddress1,
  mockedRegisteringParty1,
  mockedSelectSecurityAgreement
} from './mock-registration-new'

// Mock data to set in state model for unit tests.
export const mockedAmendmentCourtOrder: CourtOrderIF = {
  courtName: 'court name',
  courtRegistry: 'court registry',
  fileNumber: 'file#',
  orderDate: '2021-09-03T18:00:00+00:00',
  effectOfOrder: 'effect of order'
}

export const mockedGeneralCollateralAdd: GeneralCollateralIF[] = [
  {
    addedDateTime: '2021-09-16T05:56:20Z',
    descriptionAdd: 'ADD TEST GENERAL COLLATERAL'
  },
  {
    collateralId: 300000,
    addedDateTime: '2021-09-16T05:56:20Z',
    description: 'UNCHANGED TEST GENERAL COLLATERAL'
  }
]
export const mockedGeneralCollateralDelete: GeneralCollateralIF[] = [
  {
    collateralId: 100000,
    addedDateTime: '2021-09-16T05:56:20Z',
    descriptionDelete: 'DELETE TEST GENERAL COLLATERAL'
  },
  {
    collateralId: 300000,
    addedDateTime: '2021-09-16T05:56:20Z',
    description: 'UNCHANGED TEST GENERAL COLLATERAL'
  }
]
export const mockedGeneralCollateralEdit: GeneralCollateralIF[] = [
  {
    collateralId: 100000,
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
    id: 200000,
    type: APIVehicleTypes.BOAT,
    serialNumber: '123456789',
    year: 2010,
    make: 'CREST LINER',
    model: '1700 VISION UNCHANGED'
  }
]
export const mockedVehicleCollateralDelete: VehicleCollateralIF[] = [
  {
    id: 1,
    type: APIVehicleTypes.MOTOR_VEHICLE,
    serialNumber: 'KM8J3CA46JU622994',
    year: 2018,
    make: 'HYUNDAI',
    model: 'TUSCON REMOVED',
    action: ActionTypes.REMOVED
  },
  {
    id: 200000,
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
    type: APIVehicleTypes.MOTOR_VEHICLE,
    serialNumber: 'KM8J3CA46JU622994',
    year: 2018,
    make: 'HYUNDAI',
    model: 'TUSCON EDITED',
    action: ActionTypes.EDITED
  },
  {
    id: 200000,
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
    partyId: 200000,
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
    partyId: 200000,
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
    partyId: 200000,
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
    partyId: 200000,
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

export const mockedModelAmendmdmentAdd: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  authorization: {
    keycloakRoles: [],
    authRoles: []
  },
  registration: {
    amendmentDescription: 'Adding',
    collateral: {
      valid: false,
      vehicleCollateral: mockedVehicleCollateralAdd,
      generalCollateral: mockedGeneralCollateralAdd
    },
    confirmDebtorName: null,
    courtOrderInformation: null,
    creationDate: '',
    draft: {
      type: '',
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
    searchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false
  },
  userInfo: {
    contacts: [],
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  folioOrReferenceNumber: 'UT-AM-001-ADD'
}

export const mockedModelAmendmdmentDelete: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  authorization: {
    keycloakRoles: [],
    authRoles: []
  },
  registration: {
    amendmentDescription: 'Deleting',
    collateral: {
      valid: false,
      vehicleCollateral: mockedVehicleCollateralDelete,
      generalCollateral: mockedGeneralCollateralDelete
    },
    confirmDebtorName: null,
    courtOrderInformation: null,
    creationDate: '',
    draft: {
      type: '',
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
    searchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false
  },
  userInfo: {
    contacts: [],
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  folioOrReferenceNumber: 'UT-AM-002-DELETE'
}

export const mockedModelAmendmdmentEdit: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  authorization: {
    keycloakRoles: [],
    authRoles: []
  },
  registration: {
    amendmentDescription: 'Editing',
    collateral: {
      valid: false,
      vehicleCollateral: mockedVehicleCollateralEdit,
      generalCollateral: mockedGeneralCollateralEdit
    },
    confirmDebtorName: null,
    courtOrderInformation: null,
    creationDate: '',
    draft: {
      type: '',
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
    searchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false
  },
  userInfo: {
    contacts: [],
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  folioOrReferenceNumber: 'UT-AM-003-EDIT'
}

export const mockedModelAmendmdmentCourtOrder: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  authorization: {
    keycloakRoles: [],
    authRoles: []
  },
  registration: {
    amendmentDescription: 'Court Order',
    collateral: {
      valid: false,
      vehicleCollateral: [],
      generalCollateral: []
    },
    confirmDebtorName: null,
    courtOrderInformation: mockedAmendmentCourtOrder,
    creationDate: '',
    draft: {
      type: '',
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
    searchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false
  },
  userInfo: {
    contacts: [],
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  folioOrReferenceNumber: 'UT-AM-004-COURT-ORDER'
}
