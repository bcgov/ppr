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
  HomeSectionIF,
  MhrRegistrationHomeOwnersIF,
  MhrRegistrationHomeOwnerGroupIF
} from '@/interfaces'
import { ActionIF } from '@/interfaces/store-interfaces/action-interface'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'

export const resetNewRegistration: ActionIF = ({ commit }): void => {
  commit('mutateNewRegistration')
}

export const resetRegTableData: ActionIF = ({ commit }): void => {
  commit('mutateRegistrationTableReset')
}

export const setAccountProductSubscribtion: ActionIF = (
  { commit },
  productSubscriptions: AccountProductSubscriptionIF
): void => {
  commit('mutateAccountProductSubscribtion', productSubscriptions)
}

export const setUserProductSubscriptions: ActionIF = ({ commit }, products: Array<UserProductSubscriptionIF>): void => {
  commit('mutateUserProductSubscriptions', products)
}

export const setUserProductSubscriptionsCodes: ActionIF = ({ commit }, activeProducts: Array<ProductCode>): void => {
  commit('mutateUserProductSubscriptionsCodes', activeProducts)
}

export const setAccountInformation: ActionIF = ({ commit }, account: AccountInformationIF): void => {
  commit('mutateAccountInformation', account)
}

export const setAddCollateral: ActionIF = ({ commit }, addCollateral: AddCollateralIF): void => {
  commit('mutateAddCollateral', addCollateral)
  commit('mutateUnsavedChanges', true)
}

export const setOriginalAddCollateral: ActionIF = ({ commit }, addCollateral: AddCollateralIF): void => {
  commit('mutateOriginalAddCollateral', addCollateral)
}

export const setAddSecuredPartiesAndDebtors: ActionIF = ({ commit }, addParties: AddPartiesIF): void => {
  commit('mutateAddSecuredPartiesAndDebtors', addParties)
  commit('mutateUnsavedChanges', true)
}

export const setOriginalAddSecuredPartiesAndDebtors: ActionIF = ({ commit }, addParties: AddPartiesIF): void => {
  commit('mutateOriginalAddSecuredPartiesAndDebtors', addParties)
}

export const setAmendmentDescription: ActionIF = ({ commit }, description: string): void => {
  commit('mutateAmendmentDescription', description)
  commit('mutateUnsavedChanges', true)
}

export const setAuthRoles: ActionIF = ({ commit }, authRoles: Array<string>): void => {
  commit('mutateAuthRoles', authRoles)
}

export const setRoleSbc: ActionIF = ({ commit }, isSbc: boolean): void => {
  commit('mutateRoleSbc', isSbc)
}

export const setCertifyInformation: ActionIF = ({ commit }, certifyInformation: CertifyIF): void => {
  commit('mutateCertifyInformation', certifyInformation)
}

export const setStaffPayment: ActionIF = ({ commit }, staffPayment: StaffPaymentIF): void => {
  commit('mutateStaffPayment', staffPayment)
}

export const setIsStaffClientPayment: ActionIF = ({ commit }, isStaffClientPayment: boolean): void => {
  commit('mutateIsStaffClientPayment', isStaffClientPayment)
}

export const setCollateralShowInvalid = ({ commit }, show: boolean): void => {
  commit('mutateCollateralShowInvalid', show)
}

export const setCollateralValid = ({ commit }, valid: boolean): void => {
  commit('mutateCollateralValid', valid)
}

export const setCourtOrderInformation: ActionIF = ({ commit }, courtOrderInformation: CourtOrderIF): void => {
  commit('mutateCourtOrderInformation', courtOrderInformation)
  commit('mutateUnsavedChanges', true)
}

export const setDraft: ActionIF = ({ commit }, draft: DraftIF): void => {
  commit('mutateDraft', draft)
}

export const setGeneralCollateral: ActionIF = ({ commit }, generalCollateral: GeneralCollateralIF[]): void => {
  commit('mutateGeneralCollateral', generalCollateral)
  commit('mutateUnsavedChanges', true)
}

export const setLengthTrust: ActionIF = ({ commit }, lengthTrust: LengthTrustIF): void => {
  commit('mutateLengthTrust', lengthTrust)
  commit('mutateUnsavedChanges', true)
}

export const setOriginalLengthTrust: ActionIF = ({ commit }, lengthTrust: LengthTrustIF): void => {
  commit('mutateOriginalLengthTrust', lengthTrust)
}

export const setRegistrationConfirmDebtorName: ActionIF = ({ commit }, debtorName: DebtorNameIF): void => {
  commit('mutateRegistrationConfirmDebtorName', debtorName)
}

export const setRegistrationCreationDate: ActionIF = ({ commit }, date: string): void => {
  commit('mutateRegistrationCreationDate', date)
}

export const setRegistrationExpiryDate: ActionIF = ({ commit }, date: string): void => {
  commit('mutateRegistrationExpiryDate', date)
}

export const setRegistrationNumber: ActionIF = ({ commit }, regNum: string): void => {
  commit('mutateRegistrationNumber', regNum)
}

export const setRegistrationType: ActionIF = ({ commit }, registrationType: RegistrationTypeIF): void => {
  commit('mutateRegistrationType', registrationType)
}

export const setRegistrationFlowType: ActionIF = ({ commit }, registrationFlowType: RegistrationFlowType): void => {
  commit('mutateRegistrationFlowType', registrationFlowType)
}

export const setRegistrationTypeOtherDesc: ActionIF = ({ commit }, description: string): void => {
  commit('mutateRegistrationTypeOtherDesc', description)
}

export const setSearchDebtorName: ActionIF = ({ commit }, debtorName: IndividualNameIF): void => {
  commit('mutateSearchDebtorName', debtorName)
}

export const setSearchHistory: ActionIF = ({ commit }, searchHistory: Array<SearchResponseIF>): void => {
  // need to set .loadingPDF so that the loader circle triggers when set
  //  - if it starts as undefined it wont trigger on change
  for (let i = 0; i < searchHistory?.length || 0; i++) { searchHistory[i].loadingPDF = false }
  commit('mutateSearchHistory', searchHistory)
}

export const setSearchResults: ActionIF = ({ commit }, searchResults: SearchResponseIF): void => {
  commit('mutateSearchResults', searchResults)
}

export const setManufacturedHomeSearchResults: ActionIF =
  ({ commit },
    manufacturedHomeSearchResults: ManufacturedHomeSearchResponseIF
  ): void => {
    commit('mutateManufacturedHomeSearchResults', manufacturedHomeSearchResults)
  }

export const setSelectedManufacturedHomes: ActionIF = ({ commit },
  selectedManufacturedHomes: ManufacturedHomeSearchResultIF[]): void => {
  commit('mutateSelectedManufacturedHomes', selectedManufacturedHomes)
}

export const setSearchedType: ActionIF = ({ commit }, searchedType: SearchTypeIF): void => {
  commit('mutateSearchedType', searchedType)
}

export const setSearchedValue: ActionIF = ({ commit }, searchedValue: string): void => {
  commit('mutateSearchedValue', searchedValue)
}

export const setSearching: ActionIF = ({ commit }, searching: boolean): void => {
  commit('mutateSearching', searching)
}

export const setSearchCertified: ActionIF = ({ commit }, searchCertified: boolean): void => {
  commit('mutateSearchCertified', searchCertified)
}

export const setShowPaymentConfirmation: ActionIF = ({ commit }, showDialog: boolean): void => {
  commit('mutateShowPaymentConfirmation', showDialog)
}

export const setShowSelectConfirmation: ActionIF = ({ commit }, showDialog: boolean): void => {
  commit('mutateShowSelectConfirmation', showDialog)
}

export const setUserInfo: ActionIF = ({ commit }, userInfo: UserInfoIF): void => {
  commit('mutateUserInfo', userInfo)
}

export const setUserSettings: ActionIF = ({ commit }, settings: UserSettingsIF): void => {
  commit('mutateUserSettings', settings)
}

export const setVehicleCollateral: ActionIF = ({ commit }, vCollateral: VehicleCollateralIF[]): void => {
  commit('mutateVehicleCollateral', vCollateral)
  commit('mutateUnsavedChanges', true)
}

export const setAddSecuredPartiesAndDebtorsStepValidity = ({ commit }, validity) => {
  commit('mutateAddSecuredPartiesAndDebtorsStepValidity', validity)
}

export const setAddCollateralStepValidity = ({ commit }, validity) => {
  commit('mutateAddCollateralStepValidity', validity)
}

export const setLengthTrustStepValidity = ({ commit }, validity) => {
  commit('mutateLengthTrustStepValidity', validity)
}

export const setFolioOrReferenceNumber: ActionIF = ({ commit }, refNumber: string): void => {
  commit('mutateFolioOrReferenceNumber', refNumber)
  commit('mutateUnsavedChanges', true)
}

export const setShowStepErrors: ActionIF = ({ commit }, show: boolean): void => {
  commit('mutateShowStepErrors', show)
}

export const setRegTableData: ActionIF = ({ commit }, regTableData: RegTableDataI): void => {
  commit('mutateRegistrationTable', regTableData)
}

export const setRegTableBaseRegs: ActionIF = ({ commit }, baseRegs: RegistrationSummaryIF[]): void => {
  commit('mutateRegistrationTableBaseRegs', baseRegs)
}

export const setRegTableCollapsed: ActionIF = ({ commit }): void => {
  commit('mutateRegistrationTableCollapseAll')
}

export const setRegTableDraftsBaseReg: ActionIF = ({ commit }, drafts: DraftResultIF[]): void => {
  commit('mutateRegistrationTableDraftsBaseReg', drafts)
}

export const setRegTableDraftsChildReg: ActionIF = ({ commit }, drafts: DraftResultIF[]): void => {
  commit('mutateRegistrationTableDraftsChildReg', drafts)
}

export const setRegTableNewItem: ActionIF = ({ commit }, newItem: RegTableNewItemI): void => {
  commit('mutateRegistrationTableNewItem', newItem)
}

export const setRegTableSortHasMorePages: ActionIF = ({ commit }, hasMorePages: boolean): void => {
  commit('mutateRegistrationTableSortHasMorePages', hasMorePages)
}

export const setRegTableSortOptions: ActionIF = ({ commit }, options: RegistrationSortIF): void => {
  commit('mutateRegistrationTableSortOptions', options)
}

export const setRegTableSortPage: ActionIF = ({ commit }, page: number): void => {
  commit('mutateRegistrationTableSortPage', page)
}

export const setRegTableTotalRowCount: ActionIF = ({ commit }, count: number): void => {
  commit('mutateRegistrationTableTotalRowCount', count)
}

export const setUnsavedChanges: ActionIF = ({ commit }, unsavedChanges: Boolean): void => {
  commit('mutateUnsavedChanges', unsavedChanges)
}

// MHR Registration
export const setMhrHomeDescription: ActionIF = ({ commit }, { key, value }): void => {
  commit('mutateMhrHomeDescription', { key, value })
  commit('mutateUnsavedChanges', true)
}

export const setMhrHomeBaseInformation: ActionIF = ({ commit }, { key, value }): void => {
  commit('mutateMhrBaseInformation', { key, value })
  commit('mutateUnsavedChanges', true)
}

export const setMhrSubmittingParty: ActionIF = ({ commit }, { key, value }): void => {
  commit('mutateMhrSubmittingParty', { key, value })
  commit('mutateUnsavedChanges', true)
}

export const setMhrRegistrationHomeOwners: ActionIF = ({ commit }, owners: MhrRegistrationHomeOwnersIF[]): void => {
  commit('mutateMhrHomeOwners', owners)
}

export const setMhrRegistrationDocumentId: ActionIF = ({ commit }, value: string): void => {
  commit('mutateMhrRegistrationDocumentId', value)
  commit('mutateUnsavedChanges', true)
}

export const setMhrAttentionReferenceNum: ActionIF = ({ commit }, value): void => {
  commit('mutateMhrAttentionReferenceNum', value)
  commit('mutateUnsavedChanges', true)
}

export const setMhrLocation: ActionIF = ({ commit }, { key, value }): void => {
  commit('mutateMhrLocation', { key, value })
  commit('mutateUnsavedChanges', true)
}

export const setCivicAddress: ActionIF = ({ commit }, { key, value }): void => {
  commit('mutateCivicAddress', { key, value })
  commit('mutateUnsavedChanges', true)
}

export const setMhrRegistrationHomeOwnerGroups: ActionIF = (
  { commit },
  groups: MhrRegistrationHomeOwnerGroupIF[]
): void => {
  commit('mutateMhrHomeOwnerGroups', groups)
  commit('mutateUnsavedChanges', true)
}
