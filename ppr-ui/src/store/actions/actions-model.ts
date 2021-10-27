import { RegistrationFlowType } from '@/enums'
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
  RegistrationTypeIF,
  SearchResponseIF,
  SearchTypeIF,
  UserInfoIF,
  UserSettingsIF,
  AccountProductSubscriptionIF,
  GeneralCollateralIF,
  VehicleCollateralIF
} from '@/interfaces'
import { ActionIF } from '@/interfaces/store-interfaces/action-interface'

export const resetNewRegistration: ActionIF = ({ commit }): void => {
  commit('mutateNewRegistration')
}

export const setAccountProductSubscribtion: ActionIF = (
  { commit },
  productSubscriptions: AccountProductSubscriptionIF
): void => {
  commit('mutateAccountProductSubscribtion', productSubscriptions)
}

export const setAccountInformation: ActionIF = ({ commit }, account: AccountInformationIF): void => {
  commit('mutateAccountInformation', account)
}

export const setAddCollateral: ActionIF = ({ commit }, addCollateral: AddCollateralIF): void => {
  commit('mutateAddCollateral', addCollateral)
}

export const setOriginalAddCollateral: ActionIF = ({ commit }, addCollateral: AddCollateralIF): void => {
  commit('mutateOriginalAddCollateral', addCollateral)
}

export const setAddSecuredPartiesAndDebtors: ActionIF = ({ commit }, addParties: AddPartiesIF): void => {
  commit('mutateAddSecuredPartiesAndDebtors', addParties)
}

export const setOriginalAddSecuredPartiesAndDebtors: ActionIF = ({ commit }, addParties: AddPartiesIF): void => {
  commit('mutateOriginalAddSecuredPartiesAndDebtors', addParties)
}

export const setAmendmentDescription: ActionIF = ({ commit }, description: string): void => {
  commit('mutateAmendmentDescription', description)
}

export const setAuthRoles: ActionIF = ({ commit }, authRoles: Array<string>): void => {
  commit('mutateAuthRoles', authRoles)
}

export const setCertifyInformation: ActionIF = ({ commit }, certifyInformation: CertifyIF): void => {
  commit('mutateCertifyInformation', certifyInformation)
}

export const setCollateralShowInvalid = ({ commit }, show: boolean): void => {
  commit('mutateCollateralShowInvalid', show)
}

export const setCollateralValid = ({ commit }, valid: boolean): void => {
  commit('mutateCollateralValid', valid)
}

export const setCourtOrderInformation: ActionIF = ({ commit }, courtOrderInformation: CourtOrderIF): void => {
  commit('mutateCourtOrderInformation', courtOrderInformation)
}

export const setDraft: ActionIF = ({ commit }, draft: DraftIF): void => {
  commit('mutateDraft', draft)
}

export const setGeneralCollateral: ActionIF = ({ commit }, generalCollateral: GeneralCollateralIF[]): void => {
  commit('mutateGeneralCollateral', generalCollateral)
}

export const setKeycloakRoles: ActionIF = ({ commit }, keycloakRoles): void => {
  commit('mutateKeycloakRoles', keycloakRoles)
}

export const setLengthTrust: ActionIF = ({ commit }, lengthTrust: LengthTrustIF): void => {
  commit('mutateLengthTrust', lengthTrust)
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
  commit('mutateSearchHistory', searchHistory)
}

export const setSearchResults: ActionIF = ({ commit }, searchResults: SearchResponseIF): void => {
  commit('mutateSearchResults', searchResults)
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
}

export const setShowStepErrors: ActionIF = ({ commit }, show: boolean): void => {
  commit('mutateShowStepErrors', show)
}
