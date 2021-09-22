// Enums and Interfaces
import { AccountTypes, APIRegistrationTypes, RegistrationFlowType, RouteNames } from '@/enums'
import {
  AccountProductSubscriptionIF,
  AddCollateralIF,
  AddPartiesIF,
  ButtonConfigIF,
  DebtorNameIF,
  DraftIF,
  IndividualNameIF,
  LengthTrustIF,
  RegistrationTypeIF,
  SearchResponseIF,
  SearchTypeIF,
  StateIF,
  StateModelIF,
  UserSettingsIF
} from '@/interfaces'

/** The current account id. */
export const getAccountId = (state: StateIF): number => {
  return state.stateModel.accountInformation?.id
}

/** The current account label/name. */
export const getAccountLabel = (state: StateIF): string => {
  return state.stateModel.accountInformation?.label
}

export const getAccountProductSubscriptions = (
  state: StateIF
): AccountProductSubscriptionIF => {
  return state.stateModel.accountProductSubscriptions
}

/** The registration collateral object. */
export const getAddCollateral = (state: StateIF): AddCollateralIF => {
  return state.stateModel.registration.collateral
}

/** The registration collateral object of the original registration
 * (for amendments) */
export const getOriginalAddCollateral = (state: StateIF): AddCollateralIF => {
  return state.stateModel.originalRegistration.collateral
}

/** The registration parties object. */
export const getAddSecuredPartiesAndDebtors = (state: StateIF): AddPartiesIF => {
  return state.stateModel.registration.parties
}

/** The registration parties object of the original registration (for amendments). */
export const getOriginalAddSecuredPartiesAndDebtors = (state: StateIF): AddPartiesIF => {
  return state.stateModel.originalRegistration.parties
}

/** The change registration base or confirm debtor name. */
export const getConfirmDebtorName = (state: StateIF): DebtorNameIF => {
  return state.stateModel.registration.confirmDebtorName
}

/** The search value for ppr search when search type is individual debtor. */
export const getDebtorName = (state: StateIF): IndividualNameIF => {
  return state.stateModel.registration.debtorName
}

/** The current draft of a registration. */
export const getDraft = (state: StateIF): DraftIF => {
  return state.stateModel.registration.draft
}

/** The registration life and trust indenture object. */
export const getLengthTrust = (state: StateIF): LengthTrustIF => {
  return state.stateModel.registration.lengthTrust
}

/** The registration life and trust indenture object of the original registration
 * (for amendments) */
export const getOriginalLengthTrust = (state: StateIF): LengthTrustIF => {
  return state.stateModel.originalRegistration.lengthTrust
}

/** The creation date of the selected registration. */
export const getRegistrationCreationDate = (state: StateIF): String => {
  return state.stateModel.registration.creationDate
}

/** The expiry date of the selected registration. */
export const getRegistrationExpiryDate = (state: StateIF): String => {
  return state.stateModel.registration.expiryDate
}

/** The expiry date of the selected registration. */
export const getRegistrationSurrenderDate = (state: StateIF): String => {
  return state.stateModel.registration.lengthTrust?.surrenderDate
}

/** The reg number for the selected registration. */
export const getRegistrationNumber = (state: StateIF): String => {
  return state.stateModel.registration.registrationNumber
}

/** The selected registration type object. */
export const getRegistrationType = (state: StateIF): RegistrationTypeIF => {
  return state.stateModel.registration.registrationType
}

/** The selected registration flow type object. */
export const getRegistrationFlowType = (state: StateIF): RegistrationFlowType => {
  return state.stateModel.registration.registrationFlowType
}

/** The selected registration type object. */
export const getRegistrationOther = (state: StateIF): string => {
  return state.stateModel.registration.registrationTypeOtherDesc
}

/** The api response for ppr search. */
export const getSearchResults = (state: StateIF): SearchResponseIF => {
  return state.stateModel.search.searchResults
}

/** The selected search type object. */
export const getSearchedType = (state: StateIF): SearchTypeIF => {
  return state.stateModel.search.searchedType
}

/** The search value for ppr search (unless search type is individual debtor). */
export const getSearchedValue = (state: StateIF): string => {
  return state.stateModel.search.searchedValue
}

/** The list of past search responses for this account. */
export const getSearchHistory = (state: StateIF): Array<SearchResponseIF> => {
  return state.stateModel.search.searchHistory
}

/** Convenient when there is a need to access several properties. */
export const getStateModel = (state: StateIF): StateModelIF => {
  return state.stateModel
}

/** The current user's email. */
export const getUserEmail = (state: StateIF): string => {
  const userInfo = state.stateModel.userInfo
  return userInfo?.contacts[0]?.email
}

/** The current user's first name. */
export const getUserFirstName = (state: StateIF): string => {
  return state.stateModel.userInfo?.firstname || ''
}

/** The current user's last name. */
export const getUserLastName = (state: StateIF): string => {
  return state.stateModel.userInfo?.lastname || ''
}

/** The current user's roles. */
export const getUserRoles = (state: StateIF): Array<string> => {
  return state.stateModel.authorization?.authRoles
}

/** The current user's roles. */
export const getUserSettings = (state: StateIF): UserSettingsIF => {
  return state.stateModel.userInfo?.settings
}

/** The current user's username. */
export const getUserUsername = (state: StateIF): string => {
  return state.stateModel.userInfo?.username || ''
}

/** Whether the user is authorized to edit. */
export const isAuthEdit = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('edit')
}

/** Whether the user is authorized to view. */
export const isAuthView = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('view')
}

/** Whether the current account is a premium account. */
export const isPremiumAccount = (state: StateIF): boolean => {
  return (state.stateModel.accountInformation?.accountType === AccountTypes.PREMIUM)
}

/** Whether the user has 'staff' keycloak role. */
export const isRoleStaff = (state: StateIF): boolean => {
  return state.stateModel.authorization?.keycloakRoles.includes('staff')
}

/** Whether the app is processing a search request or not. */
export const isSearching = (state: StateIF): boolean => {
  return state.stateModel.search.searching
}

/** The folio or reference number. */
export const getFolioOrReferenceNumber = (state: StateIF): string => {
  return state.stateModel.folioOrReferenceNumber || ''
}

/** Whether the app should show the step errors */
export const showStepErrors = (state: StateIF): boolean => {
  return state.stateModel.registration.showStepErrors
}

/**
 * Returns the array of steps.
 */
export const getSteps = (state: any, getters: any): Array<any> => {
  const regType:RegistrationTypeIF = getRegistrationType(state)
  var lengthTrustText = 'Registration<br />Length'
  if (regType.registrationTypeAPI === APIRegistrationTypes.SECURITY_AGREEMENT) {
    lengthTrustText = 'Length and<br />Trust Indenture'
  }
  if (regType.registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN) {
    lengthTrustText = 'Amount and Date<br /> of Surrender'
  }
  const steps: Array<any> = [{
    id: 'step-1-btn',
    step: 1,
    icon: 'mdi-calendar-clock',
    text: lengthTrustText,
    to: RouteNames.LENGTH_TRUST,
    disabled: getters.isBusySaving,
    valid: state.stateModel.registration.lengthTrust.valid,
    component: 'length-trust'
  },
  {
    id: 'step-2-btn',
    step: 2,
    icon: 'mdi-account-multiple-plus',
    text: 'Add Secured Parties<br />and Debtors',
    to: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
    disabled: getters.isBusySaving,
    valid: state.stateModel.registration.parties.valid,
    component: 'add-securedparties-debtors'
  },
  {
    id: 'step-3-btn',
    step: 3,
    icon: 'mdi-car',
    text: 'Add Collateral',
    to: RouteNames.ADD_COLLATERAL,
    disabled: getters.isBusySaving,
    valid: state.stateModel.registration.collateral.valid,
    component: 'add-collateral'
  },
  {
    id: 'step-4-btn',
    step: 4,
    icon: 'mdi-text-box-check-outline', // 'mdi-text-box-multiple'
    text: 'Review <br />and Confirm',
    to: RouteNames.REVIEW_CONFIRM,
    disabled: getters.isBusySaving,
    valid: getters.isRegistrationValid,
    component: 'review-confirm'
  }]
  return steps
}

/**
 * Returns the array of new financing statement registration buttons.
 */
export const getFinancingButtons = (state: any): Array<ButtonConfigIF> => {
  const buttons: Array<ButtonConfigIF> = [{
    stepName: RouteNames.LENGTH_TRUST,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: false,
    showNext: true,
    backRouteName: '',
    nextText: 'Add Secured Parties and Debtors',
    nextRouteName: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS
  },
  {
    stepName: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.LENGTH_TRUST,
    nextText: 'Add Collateral',
    nextRouteName: RouteNames.ADD_COLLATERAL
  },
  {
    stepName: RouteNames.ADD_COLLATERAL,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
    nextText: 'Review and Confirm',
    nextRouteName: RouteNames.REVIEW_CONFIRM
  },
  {
    stepName: RouteNames.REVIEW_CONFIRM,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.ADD_COLLATERAL,
    nextText: 'Register and Pay',
    nextRouteName: RouteNames.DASHBOARD
  }]
  return buttons
}

/**
 * Returns the maximum step number.
 */
export const getMaxStep = (state: any, getters: any): number => {
  return getters.getSteps ? getters.getSteps.filter(step => step.step !== -1).length : -1
}

/**
 * Whether app is busy saving or resuming.
 */
export const isBusySaving = (state: any): boolean => {
  return false // (state.stateModel.isSaving || state.stateModel.isSavingResuming || state.stateModel.isFilingPaying)
}

/**
 * Whether all the registration steps are valid.
 */
export const isRegistrationValid = (state: any): boolean => {
  return (state.stateModel.registration.lengthTrust.valid && state.stateModel.registration.parties.valid &&
    state.stateModel.registration.collateral.valid)
}
