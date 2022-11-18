import { ProductCode, RegistrationFlowType } from '@/enums'
import {
  AccountInformationIF,
  AddCollateralIF,
  AddPartiesIF,
  CertifyIF,
  CourtOrderIF,
  DebtorNameIF,
  DraftIF,
  LengthTrustIF,
  IndividualNameIF,
  RegTableDataI,
  RegTableNewItemI,
  RegistrationSortIF,
  RegistrationTypeIF,
  SearchResponseIF,
  SearchTypeIF,
  StateIF,
  UserInfoIF,
  UserSettingsIF,
  AccountProductSubscriptionIF,
  GeneralCollateralIF,
  VehicleCollateralIF,
  RegistrationSummaryIF,
  DraftResultIF,
  ManufacturedHomeSearchResponseIF,
  ManufacturedHomeSearchResultIF,
  UserProductSubscriptionIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrTransferIF,
  MhrRegistrationIF,
  MhRegistrationSummaryIF
} from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { set } from 'lodash'

export const mutateAccountProductSubscribtion = (
  state: StateIF, productSubscriptions: AccountProductSubscriptionIF
) => {
  state.stateModel.accountProductSubscriptions = productSubscriptions
}

export const mutateUserProductSubscriptions = (state: StateIF, products: Array<UserProductSubscriptionIF>) => {
  state.stateModel.userProductSubscriptions = products
}

export const mutateUserProductSubscriptionsCodes = (state: StateIF, activeProducts: Array<ProductCode>) => {
  state.stateModel.userProductSubscriptionsCodes = activeProducts
}

export const mutateAccountInformation = (state: StateIF, accountInformation: AccountInformationIF) => {
  state.stateModel.accountInformation = accountInformation
}

export const mutateAddCollateral = (state: StateIF, addCollateral: AddCollateralIF) => {
  state.stateModel.registration.collateral = addCollateral
}

export const mutateOriginalAddCollateral = (state: StateIF, addCollateral: AddCollateralIF) => {
  state.stateModel.originalRegistration.collateral = addCollateral
}

export const mutateAddSecuredPartiesAndDebtors = (state: StateIF, addParties: AddPartiesIF) => {
  state.stateModel.registration.parties = addParties
}

export const mutateOriginalAddSecuredPartiesAndDebtors = (state: StateIF, addParties: AddPartiesIF) => {
  state.stateModel.originalRegistration.parties = addParties
}

export const mutateAmendmentDescription = (state: StateIF, description: string) => {
  state.stateModel.registration.amendmentDescription = description
}

export const mutateAuthRoles = (state: StateIF, authRoles: Array<string>) => {
  state.stateModel.authorization.authRoles = authRoles
}

export const mutateRoleSbc = (state: StateIF, isSbc: boolean) => {
  state.stateModel.authorization.isSbc = isSbc
  const roles = state.stateModel.authorization.authRoles

  if (isSbc) {
    !roles.includes('sbc') && roles.push('sbc')
  } else {
    state.stateModel.authorization.authRoles = roles.filter(role => role !== 'sbc')
  }
}

export const mutateCertifyInformation = (state: StateIF, certifyInformation: CertifyIF) => {
  state.stateModel.certifyInformation = certifyInformation
}

export const mutateCollateralShowInvalid = (state: StateIF, value: boolean) => {
  state.stateModel.registration.collateral.showInvalid = value
}

export const mutateCollateralValid = (state: StateIF, value: boolean) => {
  state.stateModel.registration.collateral.valid = value
}

export const mutateCourtOrderInformation = (state: StateIF, courtOrderInformation: CourtOrderIF) => {
  state.stateModel.registration.courtOrderInformation = courtOrderInformation
}

export const mutateDraft = (state: StateIF, draft: DraftIF) => {
  state.stateModel.registration.draft = draft
}

export const mutateGeneralCollateral = (state: StateIF, generalCollateral: GeneralCollateralIF[]) => {
  state.stateModel.registration.collateral.generalCollateral = generalCollateral
}

export const mutateStaffPayment = (state: StateIF, staffPayment: StaffPaymentIF) => {
  state.stateModel.staffPayment = staffPayment
}

export const mutateIsStaffClientPayment = (state: StateIF, isStaffClientPayment: boolean) => {
  state.stateModel.isStaffClientPayment = isStaffClientPayment
}

export const mutateLengthTrust = (state: StateIF, lengthTrust: LengthTrustIF) => {
  state.stateModel.registration.lengthTrust = lengthTrust
}

export const mutateOriginalLengthTrust = (state: StateIF, lengthTrust: LengthTrustIF) => {
  state.stateModel.originalRegistration.lengthTrust = lengthTrust
}

export const mutateNewRegistration = (state: StateIF) => {
  state.stateModel.registration.showStepErrors = false
  state.stateModel.registration.lengthTrust.valid = false
  state.stateModel.registration.lengthTrust.showInvalid = false
  state.stateModel.registration.lengthTrust.lifeInfinite = false
  state.stateModel.registration.lengthTrust.trustIndenture = false
  state.stateModel.registration.lengthTrust.lifeYears = 0
  state.stateModel.registration.lengthTrust.lienAmount = ''
  state.stateModel.registration.lengthTrust.surrenderDate = ''
  state.stateModel.registration.collateral.valid = false
  state.stateModel.registration.collateral.showInvalid = false
  state.stateModel.registration.collateral.generalCollateral = []
  state.stateModel.registration.collateral.vehicleCollateral = []
  state.stateModel.registration.parties.valid = false
  state.stateModel.registration.parties.showInvalid = false
  state.stateModel.registration.parties.registeringParty = null
  state.stateModel.registration.parties.securedParties = []
  state.stateModel.registration.parties.debtors = []
  state.stateModel.registration.draft = {
    type: null,
    financingStatement: null,
    amendmentStatement: null,
    createDateTime: null,
    lastUpdateDateTime: null
  }
  state.stateModel.registration.registrationFlowType = RegistrationFlowType.NEW
  state.stateModel.registration.confirmDebtorName = null
  state.stateModel.registration.courtOrderInformation = {
    orderDate: '',
    effectOfOrder: '',
    courtName: '',
    courtRegistry: '',
    fileNumber: ''
  }
  state.stateModel.registration.amendmentDescription = ''
  state.stateModel.certifyInformation = {
    valid: false,
    certified: false,
    legalName: ''
  }
  state.stateModel.folioOrReferenceNumber = ''
  state.stateModel.staffPayment = {
    option: -1,
    routingSlipNumber: '',
    bcolAccountNumber: '',
    datNumber: '',
    folioNumber: '',
    isPriority: false
  }
  state.stateModel.unsavedChanges = false
}

export const mutateRegistrationConfirmDebtorName = (state: StateIF, debtorName: DebtorNameIF) => {
  state.stateModel.registration.confirmDebtorName = debtorName
}

export const mutateRegistrationCreationDate = (state: StateIF, date: string) => {
  state.stateModel.registration.creationDate = date
}

export const mutateRegistrationExpiryDate = (state: StateIF, date: string) => {
  state.stateModel.registration.expiryDate = date
}

export const mutateRegistrationNumber = (state: StateIF, regNum: string) => {
  state.stateModel.registration.registrationNumber = regNum
}

export const mutateRegistrationType = (state: StateIF, registrationType: RegistrationTypeIF) => {
  state.stateModel.registration.registrationType = registrationType
}

export const mutateRegistrationFlowType = (state: StateIF, registrationFlowType: RegistrationFlowType) => {
  state.stateModel.registration.registrationFlowType = registrationFlowType
}

export const mutateRegistrationTypeOtherDesc = (state: StateIF, description: string) => {
  state.stateModel.registration.registrationTypeOtherDesc = description
}

export const mutateSearchDebtorName = (state: StateIF, debtorName: IndividualNameIF) => {
  state.stateModel.search.searchDebtorName = debtorName
}

export const mutateSearchedType = (state: StateIF, searchedType: SearchTypeIF) => {
  state.stateModel.search.searchedType = searchedType
}

export const mutateSearchedValue = (state: StateIF, searchedValue: string) => {
  state.stateModel.search.searchedValue = searchedValue
}

export const mutateSearching = (state: StateIF, searching: boolean) => {
  state.stateModel.search.searching = searching
}

export const mutateSearchCertified = (state: StateIF, searchCertified: boolean) => {
  state.stateModel.search.searchCertified = searchCertified
}

export const mutateSearchHistory = (state: StateIF, searchHistory: Array<SearchResponseIF>) => {
  state.stateModel.search.searchHistory = searchHistory
  state.stateModel.search.searchHistoryLength = searchHistory?.length || 0
}

export const mutateSearchResults = (state: StateIF, searchResults: SearchResponseIF) => {
  state.stateModel.search.searchResults = searchResults
}

export const mutateManufacturedHomeSearchResults = (
  state: StateIF,
  manufacturedHomeSearchResults: ManufacturedHomeSearchResponseIF
) => {
  state.stateModel.search.manufacturedHomeSearchResults = manufacturedHomeSearchResults
}

export const mutateSelectedManufacturedHomes = (state: StateIF,
  selectedManufacturedHomes: ManufacturedHomeSearchResultIF[]) => {
  state.stateModel.selectedManufacturedHomes = selectedManufacturedHomes
}

export const mutateUserInfo = (state: StateIF, userInfo: UserInfoIF) => {
  state.stateModel.userInfo = userInfo
}

export const mutateUserSettings = (state: StateIF, settings: UserSettingsIF) => {
  state.stateModel.userInfo.settings = settings
}

export const mutateVehicleCollateral = (state: StateIF, vCollateral: VehicleCollateralIF[]) => {
  state.stateModel.registration.collateral.vehicleCollateral = vCollateral
}

export const mutateAddSecuredPartiesAndDebtorStepValidity = (state: any, validity: boolean) => {
  state.stateModel.registration.parties.valid = validity
}

export const mutateAddCollateralStepValidity = (state: any, validity: boolean) => {
  state.stateModel.registration.collateral.valid = validity
}

export const mutateLengthTrustStepValidity = (state: any, validity: boolean) => {
  state.stateModel.registration.lengthTrust.valid = validity
}

export const mutateFolioOrReferenceNumber = (state: StateIF, refNumber: string) => {
  state.stateModel.folioOrReferenceNumber = refNumber
}

export const mutateShowStepErrors = (state: StateIF, show: boolean) => {
  state.stateModel.registration.showStepErrors = show
}

export const mutateRegistrationTable = (state: StateIF, regTableData: RegTableDataI) => {
  state.stateModel.registrationTable = regTableData
}

export const mutateRegistrationTableBaseRegs = (state: StateIF, baseRegs: RegistrationSummaryIF[]): void => {
  state.stateModel.registrationTable.baseRegs = baseRegs
}

export const mutateRegistrationTableCollapseAll = (state: StateIF): void => {
  // ensures that the table triggers an update when returning from a new reg / amend / draft when
  // the base reg is already expanded (otherwise the ref does not get set properly and the scroll doesn't work)
  for (let i = 0; i < state.stateModel.registrationTable.baseRegs.length; i++) {
    state.stateModel.registrationTable.baseRegs[i].expand = false
  }
}

export const mutateRegistrationTableDraftsBaseReg = (state: StateIF, drafts: DraftResultIF[]): void => {
  state.stateModel.registrationTable.draftsBaseReg = drafts
}

export const mutateRegistrationTableDraftsChildReg = (state: StateIF, drafts: DraftResultIF[]): void => {
  state.stateModel.registrationTable.draftsChildReg = drafts
}

export const mutateRegistrationTableNewItem = (state: StateIF, newItem: RegTableNewItemI) => {
  state.stateModel.registrationTable.newItem = newItem
}

export const mutateRegistrationTableReset = (state: StateIF): void => {
  state.stateModel.registrationTable.baseRegs = []
  state.stateModel.registrationTable.draftsBaseReg = []
  state.stateModel.registrationTable.draftsChildReg = []
  state.stateModel.registrationTable.newItem = {
    addedReg: '',
    addedRegParent: '',
    addedRegSummary: null,
    prevDraft: ''
  }
  state.stateModel.registrationTable.sortHasMorePages = true
  state.stateModel.registrationTable.sortOptions = {
    endDate: null,
    folNum: '',
    orderBy: 'createDateTime',
    orderVal: 'desc',
    regBy: '',
    regNum: '',
    regParty: '',
    regType: '',
    secParty: '',
    startDate: null,
    status: ''
  }
  state.stateModel.registrationTable.sortPage = 1
  state.stateModel.registrationTable.totalRowCount = 0
}

export const mutateRegistrationTableSortHasMorePages = (state: StateIF, hasMorePages: boolean): void => {
  state.stateModel.registrationTable.sortHasMorePages = hasMorePages
}

export const mutateRegistrationTableSortOptions = (state: StateIF, options: RegistrationSortIF) => {
  state.stateModel.registrationTable.sortOptions = options
}

export const mutateRegistrationTableSortPage = (state: StateIF, page: number): void => {
  state.stateModel.registrationTable.sortPage = page
}

export const mutateRegistrationTableTotalRowCount = (state: StateIF, count: number): void => {
  state.stateModel.registrationTable.totalRowCount = count
}

export const mutateUnsavedChanges = (state: StateIF, unsavedChanges: Boolean) => {
  state.stateModel.unsavedChanges = unsavedChanges
}

export const mutateCurrentRegistrationsTab = (state: StateIF, currentRegistrationsTab: Number) => {
  state.stateModel.currentRegistrationsTab = currentRegistrationsTab
}

// MHR Registration
export const mutateEmptyMhr = (state: StateIF, emptyMhr: MhrRegistrationIF) => {
  state.stateModel.mhrRegistration = emptyMhr
}

export const mutateMhrHomeDescription = (state: StateIF, { key, value }) => {
  state.stateModel.mhrRegistration.description[key] = value
}

export const mutateMhrBaseInformation = (state: StateIF, { key, value }) => {
  state.stateModel.mhrRegistration.description.baseInformation[key] = value
}

export const mutateMhrSubmittingParty = (state: StateIF, { key, value }) => {
  set(state.stateModel.mhrRegistration.submittingParty, key, value)
}

export const mutateMhrRegistrationDocumentId = (state: StateIF, value: string) => {
  state.stateModel.mhrRegistration.documentId = value
}

export const mutateMhrAttentionReferenceNum = (state: StateIF, value) => {
  state.stateModel.mhrRegistration.attentionReferenceNum = value
}

export const mutateMhrLocation = (state: StateIF, { key, value }) => {
  state.stateModel.mhrRegistration.location[key] = value
}

export const mutateCivicAddress = (state: StateIF, { key, value }) => {
  state.stateModel.mhrRegistration.location.address[key] = value
}

export const mutateMhrHomeOwnerGroups = (
  state: StateIF,
  groups: Array<MhrRegistrationHomeOwnerGroupIF>
) => {
  state.stateModel.mhrRegistration.ownerGroups = groups
}

export const mutateMhrTableHistory = (state: StateIF, value: MhRegistrationSummaryIF[]) => {
  state.stateModel.registrationTable.baseMhRegs = value
}

// MHR Information
export const mutateMhrInformation = (state: StateIF, mhrInfo: MhRegistrationSummaryIF) => {
  state.stateModel.mhrInformation = mhrInfo
}

// MHR Transfer
export const mutateEmptyMhrTransfer = (state: StateIF, emptyMhrTransfer: MhrTransferIF) => {
  state.stateModel.mhrTransfer = emptyMhrTransfer
}

export const mutateMhrTransferHomeOwnerGroups = (
  state: StateIF,
  groups: Array<MhrRegistrationHomeOwnerGroupIF>
) => {
  state.stateModel.mhrTransfer.ownerGroups = groups
}

export const mutateMhrTransferCurrentHomeOwnerGroups = (
  state: StateIF,
  groups: Array<MhrRegistrationHomeOwnerGroupIF>
) => {
  state.stateModel.mhrTransfer.currentOwnerGroups = groups
}
