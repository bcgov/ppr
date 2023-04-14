// Enums and Interfaces
import { AccountTypes, APIRegistrationTypes, ProductCode, RegistrationFlowType, RouteNames } from '@/enums'
import {
  AccountIF,
  AccountModelIF,
  AccountProductSubscriptionIF,
  AddCollateralIF,
  AddPartiesIF,
  ButtonConfigIF,
  CertifyIF,
  CourtOrderIF,
  DebtorNameIF,
  DraftIF,
  DraftResultIF,
  GeneralCollateralIF,
  HomeSectionIF,
  IndividualNameIF,
  LengthTrustIF,
  ManufacturedHomeSearchResponseIF,
  ManufacturedHomeSearchResultIF,
  MhRegistrationSummaryIF,
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
  MhrValidationStateIF,
  RegistrationSortIF,
  RegistrationSummaryIF,
  RegistrationTypeIF,
  RegTableDataI,
  RegTableNewItemI,
  SearchResponseIF,
  SearchTypeIF,
  StateIF,
  StateModelIF,
  SubmittingPartyIF,
  UserInfoIF,
  UserProductSubscriptionIF,
  UserSettingsIF,
  VehicleCollateralIF
} from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { HomeLocation, HomeOwners, MhrReviewConfirm, SubmittingParty, YourHome } from '@/views'
import { useMhrValidations } from '@/composables'
import { toRefs } from '@vue/composition-api'
import { MhrSectVal } from '@/composables/mhrRegistration/enums'
import { getFeatureFlag } from '@/utils'
import { MHRButtonFooterConfig, RegistrationButtonFooterConfig } from '@/resources/buttoneFooterConfig'

export const getAccountModel = (state: AccountIF): AccountModelIF => {
  return state.account
}

/** Convenient when there is a need to access several properties. */
export const getStateModel = (state: StateIF): StateModelIF => {
  return state.stateModel
}

/** The current account id. */
export const getCurrentUser = (state: StateIF): UserInfoIF => {
  return state.stateModel.userInfo
}

/** The current account id. */
export const getAccountId = (state: StateIF): number => {
  return state.stateModel.accountInformation?.id
}

/** Whether the current account is a premium account. */
export const isPremiumAccount = (state: StateIF): boolean => {
  return (state.stateModel.accountInformation?.accountType === AccountTypes.PREMIUM)
}

/** Whether the user has 'staff' keycloak role. */
export const isRoleStaff = (state: StateIF): boolean => {
  return (
    state.stateModel.authorization?.authRoles.includes('staff') ||
    isRoleStaffSbc(state)
  )
}

export const isRoleStaffBcol = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('helpdesk')
}

export const isRoleStaffReg = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('ppr_staff')
}

export const isRoleStaffSbc = (state: StateIF): boolean => {
  return state.stateModel.authorization?.isSbc
}

export const isRoleQualifiedSupplier = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('mhr_transfer_sale')
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

export const getUserProductSubscriptions = (state: StateIF): Array<UserProductSubscriptionIF> => {
  return state.stateModel.userProductSubscriptions
}

export const getUserProductSubscriptionsCodes = (state: StateIF): Array<ProductCode> => {
  return state.stateModel.userProductSubscriptionsCodes
}

/** The registration collateral object. */
export const getAddCollateral = (state: StateIF): AddCollateralIF => {
  return state.stateModel.registration.collateral
}

/** The amendment registration description. */
export const getAmendmentDescription = (state: StateIF): string => {
  return state.stateModel.registration.amendmentDescription
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

/** The certify information for the registration confirmation. */
export const getCertifyInformation = (state: StateIF): CertifyIF => {
  return state.stateModel.certifyInformation
}

/** The registration court order information object. */
export const getCourtOrderInformation = (state: StateIF): CourtOrderIF => {
  return state.stateModel.registration.courtOrderInformation
}

/** The current Dashboard tab selected. */
export const getCurrentRegistrationsTab = (state: StateIF): Number => {
  return state.stateModel.currentRegistrationsTab
}

/** The current draft of a registration. */
export const getDraft = (state: StateIF): DraftIF => {
  return state.stateModel.registration.draft
}

/** The list of registration general collateral */
export const getGeneralCollateral = (state: StateIF): GeneralCollateralIF[] => {
  return state.stateModel.registration.collateral.generalCollateral
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

/** Is true during an MHR Registration. */
export const isMhrRegistration = (state: StateIF): boolean => {
  return state.stateModel.registration?.registrationType?.registrationTypeAPI ===
    APIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION
}

/** The selected registration flow type object. */
export const getRegistrationFlowType = (state: StateIF): RegistrationFlowType => {
  return state.stateModel.registration.registrationFlowType
}

/** The selected registration type object. */
export const getRegistrationOther = (state: StateIF): string => {
  return state.stateModel.registration.registrationTypeOtherDesc
}

/** The . */
export const getRegistration = (state: StateIF): string => {
  return state.stateModel.registration.registrationTypeOtherDesc
}

/** The search value for ppr search when search type is individual debtor. */
export const getSearchDebtorName = (state: StateIF): IndividualNameIF => {
  return state.stateModel.search.searchDebtorName
}

/** The api response for ppr search. */
export const getSearchResults = (state: StateIF): SearchResponseIF => {
  return state.stateModel.search.searchResults
}

export const getManufacturedHomeSearchResults = (state: StateIF): ManufacturedHomeSearchResponseIF => {
  return state.stateModel.search.manufacturedHomeSearchResults
}

export const getSelectedManufacturedHomes = (state: StateIF): ManufacturedHomeSearchResultIF[] => {
  return state.stateModel.selectedManufacturedHomes
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

export const getSearchHistoryLength = (state: StateIF): Number => {
  return state.stateModel.search.searchHistoryLength
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

export const hasPprRole = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('ppr')
}

export const hasMhrRole = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('mhr')
}

export const hasPprEnabled = (state: StateIF): boolean => {
  return getUserProductSubscriptionsCodes(state).includes(ProductCode.PPR)
}

export const hasMhrEnabled = (state: StateIF): boolean => {
  return getUserProductSubscriptionsCodes(state).includes(ProductCode.MHR) && getFeatureFlag('mhr-ui-enabled')
}

/** The current user's service fee (applicable for non billable users). */
export const getUserServiceFee = (state: StateIF): number => {
  return state.stateModel.userInfo?.feeSettings?.serviceFee || 1.50
}

/** All the current user info. */
export const getUserSettings = (state: StateIF): UserSettingsIF => {
  return state.stateModel.userInfo?.settings
}

/** The current user's username. */
export const getUserUsername = (state: StateIF): string => {
  return state.stateModel.userInfo?.username || ''
}

/** The list of registration vehicle collateral */
export const getVehicleCollateral = (state: StateIF): VehicleCollateralIF[] => {
  return state.stateModel.registration.collateral.vehicleCollateral
}

/** Whether the user has unsaved changes in their current flow or not. */
export const hasUnsavedChanges = (state: StateIF): Boolean => {
  return state.stateModel.unsavedChanges
}

/** Whether the current account is a non billable account. */
export const isNonBillable = (state: StateIF): boolean => {
  return state.stateModel.userInfo?.feeSettings?.isNonBillable || false
}

/** Whether the app is processing a search request or not. */
export const isSearching = (state: StateIF): boolean => {
  return state.stateModel.search.searching
}

/** Whether the staff certify a search. */
export const isSearchCertified = (state: StateIF): boolean => {
  return state.stateModel.search.searchCertified
}

/** The folio or reference number. */
export const getFolioOrReferenceNumber = (state: StateIF): string => {
  return state.stateModel.folioOrReferenceNumber || ''
}

/** The staff payment. */
export const getStaffPayment = (state: StateIF): StaffPaymentIF => {
  return state.stateModel.staffPayment
}

/** Is true when staff is doing a mhr search on behalf of a client. */
export const getIsStaffClientPayment = (state: StateIF): boolean => {
  return state.stateModel.isStaffClientPayment
}

/** Whether the app should show the step errors */
export const showStepErrors = (state: StateIF): boolean => {
  return state.stateModel.registration.showStepErrors
}

/**
 * Returns the array of steps.
 */
export const getSteps = (state: any, getters: any): Array<any> => {
  return getters.isMhrRegistration
    ? getters.getMhrSteps
    : getters.getPprSteps
}

export const getPprSteps = (state: any, getters: any): Array<any> => {
  const regType: RegistrationTypeIF = getRegistrationType(state)
  let lengthTrustText = 'Registration<br />Length'
  if (regType?.registrationTypeAPI === APIRegistrationTypes.SECURITY_AGREEMENT) {
    lengthTrustText = 'Length and<br />Trust Indenture'
  }
  if (regType?.registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN) {
    lengthTrustText = 'Amount and Date<br /> of Surrender'
  }
  return [{
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
}

export const getMhrSteps = (state: any, getters: any): Array<any> => {
  return [{
    id: 'step-1-btn',
    step: 1,
    icon: 'mdi-home',
    text: 'Describe <br />your Home',
    to: RouteNames.YOUR_HOME,
    disabled: getters.isBusySaving,
    valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel(state)))
      .getStepValidation(MhrSectVal.YOUR_HOME_VALID),
    component: YourHome
  },
  {
    id: 'step-2-btn',
    step: 2,
    icon: 'mdi-account',
    text: 'Submitting <br />Party',
    to: RouteNames.SUBMITTING_PARTY,
    disabled: getters.isBusySaving,
    valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel(state)))
      .getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID),
    component: SubmittingParty
  },
  {
    id: 'step-3-btn',
    step: 3,
    icon: '$vuetify.icons.values.HomeOwnersIcon', // Vuetify custom SVG icon
    text: 'List Home <br />Owners',
    to: RouteNames.HOME_OWNERS,
    disabled: getters.isBusySaving,
    valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel(state)))
      .getStepValidation(MhrSectVal.HOME_OWNERS_VALID),
    component: HomeOwners
  },
  {
    id: 'step-4-btn',
    step: 4,
    icon: '$vuetify.icons.values.HomeLocationIcon', // Vuetify custom SVG icon
    text: 'Location <br />of Home',
    to: RouteNames.HOME_LOCATION,
    disabled: getters.isBusySaving,
    valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel(state)))
      .getStepValidation(MhrSectVal.LOCATION_VALID),
    component: HomeLocation
  },
  {
    id: 'step-5-btn',
    step: 5,
    icon: 'mdi-text-box-check-outline', // 'mdi-text-box-multiple'
    text: 'Review <br />and Confirm',
    to: RouteNames.MHR_REVIEW_CONFIRM,
    disabled: getters.isBusySaving,
    valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel(state)))
      .getStepValidation(MhrSectVal.REVIEW_CONFIRM_VALID),
    component: MhrReviewConfirm
  }]
}

/**
 * Returns the array of new registration buttons.
 */
export const getFooterButtonConfig = (state: any, getters: any): Array<ButtonConfigIF> => {
  return getters.isMhrRegistration ? MHRButtonFooterConfig : RegistrationButtonFooterConfig
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

/** Return values used for the registration table. */
export const getRegTableData = (state: StateIF): RegTableDataI => {
  return state.stateModel.registrationTable
}

/** Returns registration table base regs */
export const getRegTableBaseRegs = (state: StateIF): RegistrationSummaryIF[] => {
  return state.stateModel.registrationTable.baseRegs
}

/** Returns Manufacture Home Registration table base regs */
export const getMhRegTableBaseRegs = (state: StateIF): MhRegistrationSummaryIF[] => {
  return state.stateModel.registrationTable.baseMhRegs
}

/** Returns registration table base reg drafts */
export const getRegTableDraftsBaseReg = (state: StateIF): DraftResultIF[] => {
  return state.stateModel.registrationTable.draftsBaseReg
}

/** Returns registration table child reg drafts */
export const getRegTableDraftsChildReg = (state: StateIF): DraftResultIF[] => {
  return state.stateModel.registrationTable.draftsChildReg
}

/** Returns registration table new item info */
export const getRegTableNewItem = (state: StateIF): RegTableNewItemI => {
  return state.stateModel.registrationTable.newItem
}

/** Returns user session registration table sort options */
export const getRegTableSortOptions = (state: StateIF): RegistrationSortIF => {
  return state.stateModel.registrationTable.sortOptions
}

/** Returns registration table sort page number */
export const getRegTableSortPage = (state: StateIF): number => {
  return state.stateModel.registrationTable.sortPage
}

/** Returns registration table total base reg rows, including base reg drafts */
export const getRegTableTotalRowCount = (state: StateIF): number => {
  return state.stateModel.registrationTable.totalRowCount
}

export const hasMorePages = (state: StateIF): boolean => {
  return state.stateModel.registrationTable.sortHasMorePages
}

export const getMhrHomeSections = (state: StateIF): Array<HomeSectionIF> => {
  return state.stateModel.mhrRegistration.description.sections
}

// MHR Getters
export const getMhrDraftNumber = (state: StateIF): string => {
  return state.stateModel.mhrRegistration.draftNumber
}

export const getMhrRegistrationManufacturerName = (state: StateIF): string => {
  return state.stateModel.mhrRegistration.description.manufacturer
}

export const getMhrRegistrationYearOfManufacture = (state: StateIF): number => {
  return state.stateModel.mhrRegistration.description.baseInformation.year
}

export const getMhrRegistrationIsYearApproximate = (state: StateIF): boolean => {
  return state.stateModel.mhrRegistration.description.baseInformation.circa
}

export const getMhrRegistrationHomeMake = (state: StateIF): string => {
  return state.stateModel.mhrRegistration.description.baseInformation.make
}

export const getMhrRegistrationHomeModel = (state: StateIF): string => {
  return state.stateModel.mhrRegistration.description.baseInformation.model
}

export const getMhrRegistrationOtherInfo = (state: StateIF): string => {
  return state.stateModel.mhrRegistration.description.otherRemarks
}

export const getMhrRegistrationHomeDescription = (state: StateIF): MhrRegistrationDescriptionIF => {
  return state.stateModel.mhrRegistration.description
}

export const getMhrRegistrationSubmittingParty = (state: StateIF): SubmittingPartyIF => {
  return state.stateModel.mhrRegistration.submittingParty
}
export const getMhrRegistrationHomeOwners = (state: StateIF): MhrRegistrationHomeOwnerIF[] => {
  const owners = []
  state.stateModel.mhrRegistration.ownerGroups.forEach(group => {
    if (group.owners.length === 0) {
      // Groups with no owners should have at least one 'placeholder' owner
      // to be properly displayed in Group Table
      owners.push({ groupId: group.groupId })
    } else {
      group.owners.forEach(owner => owners.push({ ...owner, groupId: group.groupId }))
    }
  })
  return owners
}

export const getMhrRegistrationDocumentId = (state: StateIF): string => {
  return state.stateModel.mhrRegistration.documentId
}

export const getMhrAttentionReferenceNum = (state: StateIF): any => {
  return state.stateModel.mhrRegistration.attentionReferenceNum
}

export const getMhrRegistrationLocation = (state: StateIF): MhrRegistrationHomeLocationIF => {
  return state.stateModel.mhrRegistration.location
}

export const getIsManualLocation = (state: StateIF): boolean => {
  return state.stateModel.mhrRegistration.isManualLocationInfo
}

export const getMhrRegistrationHomeOwnerGroups = (state: StateIF): MhrRegistrationHomeOwnerGroupIF[] => {
  return state.stateModel.mhrRegistration.ownerGroups
}

export const getMhrRegistrationValidationModel = (state: StateIF): MhrValidationStateIF => {
  return state.stateModel.mhrValidationState
}

export const getMhrInformation = (state: StateIF): MhRegistrationSummaryIF => {
  return state.stateModel.mhrInformation
}

export const hasLien = (state: StateIF): boolean => {
  // Current state is to verify the property exists. Future state may be more granular dependent on type.
  return !!state.stateModel.mhrInformation.lienRegistrationType
}
