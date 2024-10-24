import { defineStore } from 'pinia'
import { stateModel } from '@/store/state'
import { find, omit } from 'lodash'
import {
  AccountInformationIF,
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
  MhrRegistrationIF,
  MhrTransferIF,
  MhrValidationStateIF,
  MhrValidationManufacturerStateIF,
  RegistrationSortIF,
  RegistrationSummaryIF,
  RegistrationTypeIF,
  RegTableDataI,
  RegTableNewItemI,
  SearchResponseIF,
  SearchTypeIF,
  StateModelIF,
  SubmittingPartyIF,
  TransferTypeSelectIF,
  UserInfoIF,
  UserProductSubscriptionIF,
  UserSettingsIF,
  VehicleCollateralIF,
  UnitNoteStoreActionIF,
  UnitNoteRegistrationIF,
  PartyIF,
  UserAccessValidationIF,
  AccountInfoIF,
  UserAccessAuthorizationIF,
  ExemptionIF,
  ExemptionValidationIF,
  StaffPaymentIF,
  AddressIF,
  MhrTransportPermitIF,
  MhrRegistrationHomeLocationWithoutAddressIF,
  ExemptionNoteIF,
  AddEditSaNoticeIF
} from '@/interfaces'
import {
  AccountTypes,
  APIRegistrationTypes,
  AuthRoles,
  LocationChangeTypes,
  MhApiStatusTypes,
  MhrSubTypes,
  ProductCode,
  RegistrationFlowType,
  RouteNames,
  SettingOptions,
  UnitNoteDocTypes
} from '@/enums'
import { computed, ComputedRef, ref, toRefs } from 'vue'
import { useMhrCorrections, useMhrValidations } from '@/composables'
import { MhrSectVal } from '@/composables/mhrRegistration/enums'
import { getFeatureFlag } from '@/utils'
import {
  ExemptionDetails,
  ExemptionReview,
  HomeLocation,
  HomeOwners,
  MhrReviewConfirm,
  QsInformation,
  QsReviewConfirm,
  SubmittingParty,
  YourHome
} from '@/views'
import {
  MHRButtonFooterConfig, MHRCorrectionButtonFooterConfig,
  MHRManufacturerButtonFooterConfig,
  RegistrationButtonFooterConfig
} from '@/resources/buttonFooterConfig'
import { CancelUnitNoteIF, UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'

export const useStore = defineStore('assetsStore', () => {
  // State Model
  const state = ref({ ...stateModel })

  /** PPR Getters **/

  const getStateModel = computed((): StateModelIF => {
    return state.value
  })
  const getAccountModel = computed((): AccountModelIF => {
    return null // account
  })
  const isRoleStaffSbc = computed((): boolean => {
    return state.value.authorization?.isSbc
  })
  /** Whether the user has 'staff' keycloak role. */
  const isRoleStaff = computed((): boolean => {
    return (state.value.authorization?.authRoles.includes(AuthRoles.STAFF) || isRoleStaffSbc.value)
  })
  /** Whether the user has 'manufacturer' keycloak role and active product. */
  const isRoleManufacturer = computed((): boolean => {
    return (state.value.authorization?.authRoles.includes(AuthRoles.MHR_REGISTER) &&
      state.value.authorization?.authRoles.includes(AuthRoles.MHR_PAYMENT) &&
      state.value.authorization?.authRoles.includes(AuthRoles.MHR_TRANSPORT) &&
      state.value.authorization?.authRoles.includes(AuthRoles.MHR_TRANSFER_SALE) &&
      !state.value.authorization?.authRoles.includes(AuthRoles.PPR_STAFF) &&
      getUserProductSubscriptionsCodes.value.includes(ProductCode.MANUFACTURER)
    )
  })
  /** Convenient when there is a need to access several properties. */
  const getCurrentUser = computed((): UserInfoIF => {
    return state.value.userInfo
  })
  /** The current account id. */
  const getAccountId = computed((): number => {
    return state.value.accountInformation?.id
  })
  const isRoleStaffBcol = computed((): boolean => {
    return state.value.authorization?.authRoles.includes(AuthRoles.HELPDESK)
  })
  const isPremiumAccount = computed((): boolean => {
    return (state.value.accountInformation?.accountType === AccountTypes.PREMIUM)
  })
  const isRoleStaffReg = computed((): boolean => {
    return state.value.authorization?.authRoles.includes(AuthRoles.PPR_STAFF)
  })
  /** Whether the user has one of the approved 'qualified supplier' product subscriptions. */
  const isRoleQualifiedSupplier = computed((): boolean => {
    return !state.value.authorization?.authRoles.includes(AuthRoles.STAFF) &&
      getUserProductSubscriptionsCodes.value?.some(code =>
        [ProductCode.LAWYERS_NOTARIES, ProductCode.MANUFACTURER, ProductCode.DEALERS].includes(code)
      )
  })
  const isRoleQualifiedSupplierLawyersNotaries = computed((): boolean => {
    return state.value.authorization?.authRoles.includes(AuthRoles.MHR_TRANSFER_SALE) &&
      getUserProductSubscriptionsCodes.value.includes(ProductCode.LAWYERS_NOTARIES)
  })
  const isRoleQualifiedSupplierHomeDealer = computed((): boolean => {
    return getUserProductSubscriptionsCodes.value.includes(ProductCode.DEALERS)
  })
  /** The current account label/name. */
  const getAccountLabel = computed((): string => {
    return state.value.accountInformation?.label
  })
  const getAccountProductSubscriptions = computed((): AccountProductSubscriptionIF => {
    return state.value.accountProductSubscriptions
  })
  const getUserProductSubscriptions = computed((): UserProductSubscriptionIF[] => {
    return state.value.userProductSubscriptions
  })
  const getUserProductSubscriptionsCodes = computed<ProductCode[]>((): ProductCode[] => {
    return state.value.userProductSubscriptionsCodes
  })
  /** The registration collateral object. */
  const getAddCollateral = computed((): AddCollateralIF => {
    return state.value.registration.collateral
  })
  /** The registration collateral object of the original registration
   * (for amendments) */
  const getOriginalAddCollateral = computed<AddCollateralIF>(() => {
    return state.value.originalRegistration.collateral
  })
  /** The amendment registration description. */
  const getAmendmentDescription = computed((): string => {
    return state.value.registration.amendmentDescription
  })
  /** The registration parties object. */
  const getAddSecuredPartiesAndDebtors = computed<AddPartiesIF>(() => {
    return state.value.registration.parties
  })
  /** The registration parties object of the original registration (for amendments). */
  const getOriginalAddSecuredPartiesAndDebtors = computed<AddPartiesIF>(() => {
    return state.value.originalRegistration.parties
  })
  const getConfirmDebtorName = computed<DebtorNameIF>(() => {
    return state.value.registration.confirmDebtorName
  })
  const getCertifyInformation = computed<CertifyIF>(() => {
    return state.value.certifyInformation
  })
  const getCourtOrderInformation = computed<CourtOrderIF>(() => {
    return state.value.registration.courtOrderInformation
  })
  const getCurrentRegistrationsTab = computed<number>((): number => {
    return state.value.currentRegistrationsTab
  })
  const getDraft = computed<DraftIF>(() => {
    return state.value.registration.draft
  })
  const getGeneralCollateral = computed<GeneralCollateralIF[]>(() => {
    return state.value.registration.collateral.generalCollateral
  })
  const getLengthTrust = computed<LengthTrustIF>(() => {
    return state.value.registration.lengthTrust
  })
  const getOriginalLengthTrust = computed<LengthTrustIF>(() => {
    return state.value.originalRegistration.lengthTrust
  })
  const getSecuritiesActNotices = computed<Array<AddEditSaNoticeIF>>(() => {
    return state.value.registration.securitiesActNotices
  })
  const getOriginalSecuritiesActNotices = computed<Array<AddEditSaNoticeIF>>(() => {
    return state.value.originalRegistration.securitiesActNotices
  })
  const getRegistrationCreationDate = computed<string>(() => {
    return state.value.registration.creationDate
  })
  const getRegistrationExpiryDate = computed<string>(() => {
    return state.value.registration.expiryDate
  })
  const getRegistrationSurrenderDate = computed<string>(() => {
    return state.value.registration.lengthTrust?.surrenderDate
  })
  const getRegistrationNumber = computed<string>(() => {
    return state.value.registration.registrationNumber
  })
  /** The selected registration type object. */
  const getRegistrationType = computed<RegistrationTypeIF>((): RegistrationTypeIF => {
    return state.value.registration.registrationType
  })
  const isMhrRegistration = computed<boolean>(() => {
    return [
      APIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION,
      APIRegistrationTypes.MHR_CORRECTION_STAFF,
      APIRegistrationTypes.MHR_CORRECTION_CLIENT,
      APIRegistrationTypes.MHR_PUBLIC_AMENDMENT
    ].includes(state.value.registration?.registrationType?.registrationTypeAPI)
  })
  const isMhrStaffRegistration = computed<boolean>(() => {
    return isMhrRegistration.value && isRoleStaff.value
  })
  const isMhrManufacturerRegistration = computed<boolean>(() => {
    return isMhrRegistration.value && isRoleManufacturer.value
  })
  const isMhrRegistrationReviewValid = computed<boolean>(() => {
    return isMhrManufacturerRegistration.value
      ? isMhrManufacturerRegistrationReviewValid.value
      : isMhrStaffRegistrationReviewValid.value
  })
  /** Is true when all steps are valid as well as staff payment and authorization are valid */
  const isMhrStaffRegistrationReviewValid = computed<boolean>(() => {
    const modelRef = toRefs(getMhrRegistrationValidationModel.value)
    return state.value.mhrValidationState.reviewConfirmValid.authorizationValid &&
      state.value.mhrValidationState.reviewConfirmValid?.staffPaymentValid &&
      useMhrValidations(modelRef).getStepValidation(MhrSectVal.YOUR_HOME_VALID) &&
      useMhrValidations(modelRef).getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID) &&
      useMhrValidations(modelRef).getStepValidation(MhrSectVal.HOME_OWNERS_VALID) &&
      useMhrValidations(modelRef).getStepValidation(MhrSectVal.LOCATION_VALID) &&
      (isMhrReRegistration.value ? true : useMhrCorrections().hasMadeMhrCorrections.value)
  })
  const isMhrManufacturerRegistrationReviewValid = computed<boolean>(() => {
    const modelRef = toRefs(getMhrRegistrationValidationModel.value)
    return state.value.mhrValidationManufacturerState.reviewConfirmValid.authorizationValid &&
      state.value.mhrValidationManufacturerState.reviewConfirmValid?.attentionValid &&
      state.value.mhrValidationManufacturerState.reviewConfirmValid?.refNumValid &&
      useMhrValidations(modelRef).getStepValidation(MhrSectVal.YOUR_HOME_VALID)
  })
  /** The selected registration flow type object. */
  const getRegistrationFlowType = computed<RegistrationFlowType>(() => {
    return state.value.registration.registrationFlowType
  })
  /** The selected registration type object. */
  const getRegistrationOther = computed<string>((): string => {
    return state.value.registration.registrationTypeOtherDesc as unknown as string
  })
  const getRegistration = computed<string>(() => {
    return state.value.registration.registrationTypeOtherDesc
  })
  /** The search value for ppr search when search type is individual debtor. */
  const getSearchDebtorName = computed<IndividualNameIF>(() => {
    return state.value.search.searchDebtorName
  })
  /** The api response for ppr search. */
  const getSearchResults = computed<SearchResponseIF>(() => {
    return state.value.search.searchResults
  })
  const getManufacturedHomeSearchResults = computed<ManufacturedHomeSearchResponseIF>(() => {
    return state.value.search.manufacturedHomeSearchResults
  })
  const getSelectedManufacturedHomes = computed<ManufacturedHomeSearchResultIF[]>(() => {
    return state.value.selectedManufacturedHomes
  })
  /** The selected search type object. */
  const getSearchedType = computed<SearchTypeIF>(() => {
    return state.value.search.searchedType
  })
  const getSearchedValue = computed<string>(() => {
    return state.value.search.searchedValue
  })
  /** The list of past search responses for this account. */
  const getSearchHistory = computed<SearchResponseIF[]>(() => {
    return state.value.search.searchHistory
  })
  const getSearchHistoryLength = computed<number>((): number => {
    return state.value.search.searchHistoryLength
  })
  const getUserEmail = computed<string>(() => {
    return (!!state.value.userInfo?.contacts?.length && state.value.userInfo?.contacts[0]?.email) || ''
  })
  const getUserFirstName = computed<string>(() => {
    return state.value.userInfo?.firstname || ''
  })
  const getUserLastName = computed<string>(() => {
    return state.value.userInfo?.lastname || ''
  })
  const getUserRoles = computed<string[]>(() => {
    return state.value.authorization?.authRoles
  })
  const hasPprRole = computed<boolean>(() => {
    return state.value.authorization?.authRoles.includes('ppr')
  })
  const hasMhrRole = computed<boolean>(() => {
    return state.value.authorization?.authRoles.includes('mhr')
  })
  const hasPprEnabled = computed<boolean>(() => {
    return getUserProductSubscriptionsCodes.value.includes(ProductCode.PPR)
  })
  const hasMhrEnabled = computed<boolean>(() => {
    return getUserProductSubscriptionsCodes.value.includes(ProductCode.MHR) && getFeatureFlag('mhr-ui-enabled')
  })
  const hasMhrReIssuePermitEnabled = computed<boolean>(() => {
    return getFeatureFlag('mhr-re-issue-permit-enabled')
  })
  const hasDrsEnabled = computed<boolean>(() => {
    return isRoleStaffReg.value && getFeatureFlag('drs-integration-enabled')
  })
  const getUserServiceFee = computed<number>(() => {
    return state.value.userInfo?.feeSettings?.serviceFee || 1.50
  })
  const getUserSettings = computed<UserSettingsIF>(() => {
    return state.value.userInfo?.settings
  })
  // Get a specific User Profile preference from Misc Preferences array
  const getUserMiscSettingsByKey = (settingKey: SettingOptions) => {
    return find(state.value.userInfo?.settings?.miscellaneousPreferences,
      { accountId: getAccountId.value })?.[settingKey] || null
  }
  const getUserUsername = computed<string>(() => {
    return state.value.userInfo?.username || ''
  })
  const getVehicleCollateral = computed<VehicleCollateralIF[]>(() => {
    return state.value.registration.collateral.vehicleCollateral
  })
  const hasUnsavedChanges = computed<boolean>(() => {
    return state.value.unsavedChanges
  })
  const isNonBillable = computed<boolean>(() => {
    return state.value.userInfo?.feeSettings?.isNonBillable || false
  })
  const isSearching = computed<boolean>(() => {
    return state.value.search.searching
  })
  const isSearchCertified = computed<boolean>(() => {
    return state.value.search.searchCertified
  })
  const getFolioOrReferenceNumber = computed<string>(() => {
    return state.value.folioOrReferenceNumber || ''
  })
  const getStaffPayment = computed<StaffPaymentIF>(() => {
    return state.value.staffPayment
  })
  const getIsStaffClientPayment = computed<boolean>(() => {
    return state.value.isStaffClientPayment
  })
  const getMhrGenerateDocId = computed<string>(() => {
    return state.value.generateDocId
  })
  const showStepErrors = computed<boolean>(() => {
    return state.value.registration.showStepErrors
  })
  const getPprSteps = computed(() => {
    const regType = getRegistrationType.value
    let lengthTrustText = 'Registration<br />Length'
    if (regType?.registrationTypeAPI === APIRegistrationTypes.SECURITY_AGREEMENT) {
      lengthTrustText = 'Length and<br />Trust Indenture'
    }
    if (regType?.registrationTypeAPI === APIRegistrationTypes.SECURITY_ACT_NOTICE) {
      lengthTrustText = 'Registration<br />Details'
    }
    if (regType?.registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN) {
      lengthTrustText = 'Amount and Date<br /> of Surrender'
    }

    return [
      {
        id: 'step-1-btn',
        step: 1,
        icon: 'mdi-calendar-clock',
        text: lengthTrustText,
        to: RouteNames.LENGTH_TRUST,
        disabled: false,
        valid: state.value.registration.lengthTrust.valid,
        component: 'length-trust'
      },
      {
        id: 'step-2-btn',
        step: 2,
        icon: 'mdi-account-multiple-plus',
        text: 'Add Secured Parties<br />and Debtors',
        to: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
        disabled: false,
        valid: state.value.registration.parties.valid,
        component: 'add-securedparties-debtors'
      },
      {
        id: 'step-3-btn',
        step: 3,
        icon: 'mdi-car',
        text: 'Add Collateral',
        to: RouteNames.ADD_COLLATERAL,
        disabled: false,
        valid: state.value.registration.collateral.valid,
        component: 'add-collateral'
      },
      {
        id: 'step-4-btn',
        step: 4,
        icon: 'mdi-text-box-check-outline', // 'mdi-text-box-multiple'
        text: 'Review <br />and Confirm',
        to: RouteNames.REVIEW_CONFIRM,
        disabled: false,
        valid: isRegistrationValid.value,
        component: 'review-confirm'
      }
    ]
  })
  const getMhrStaffSteps = computed(() => {
    return [
      {
        id: 'step-1-btn',
        step: 1,
        icon: 'mdi-account',
        text: 'Submitting <br />Party',
        to: RouteNames.SUBMITTING_PARTY,
        disabled: false,
        valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
          .getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID),
        component: SubmittingParty
      },
      {
        id: 'step-2-btn',
        step: 2,
        icon: 'mdi-home',
        text: 'Describe <br />your Home',
        to: RouteNames.YOUR_HOME,
        disabled: false,
        valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
          .getStepValidation(MhrSectVal.YOUR_HOME_VALID),
        component: YourHome
      },
      {
        id: 'step-3-btn',
        step: 3,
        icon: 'custom:HomeOwnersIcon', // Vuetify custom SVG icon
        text: 'List Home <br />Owners',
        to: RouteNames.HOME_OWNERS,
        disabled: false,
        valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
          .getStepValidation(MhrSectVal.HOME_OWNERS_VALID),
        component: HomeOwners
      },
      {
        id: 'step-4-btn',
        step: 4,
        icon: 'custom:HomeLocationIcon', // Vuetify custom SVG icon
        text: 'Location <br />of Home',
        to: RouteNames.HOME_LOCATION,
        disabled: false,
        valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
          .getStepValidation(MhrSectVal.LOCATION_VALID),
        component: HomeLocation
      },
      {
        id: 'step-5-btn',
        step: 5,
        icon: 'mdi-text-box-check-outline', // 'mdi-text-box-multiple'
        text: 'Review <br />and Confirm',
        to: RouteNames.MHR_REVIEW_CONFIRM,
        disabled: false,
        valid: isMhrRegistrationReviewValid.value,
        component: MhrReviewConfirm
      }
    ]
  })
  const getMhrManufacturerSteps = computed(() => {
    return [
      {
        id: 'step-1-btn',
        step: 1,
        icon: 'mdi-home',
        text: 'Describe <br />your Home',
        to: RouteNames.YOUR_HOME,
        disabled: false,
        valid: useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
          .getStepValidation(MhrSectVal.YOUR_HOME_VALID),
        component: YourHome
      },
      {
        id: 'step-2-btn',
        step: 2,
        icon: 'mdi-text-box-check-outline', // 'mdi-text-box-multiple'
        text: 'Review <br />and Confirm',
        to: RouteNames.MHR_REVIEW_CONFIRM,
        disabled: false,
        valid: isMhrRegistrationReviewValid.value,
        component: MhrReviewConfirm
      }]
  })
  const getUserAccessSteps = computed(() => {
    return [
      {
        id: 'step-1-btn',
        step: 1,
        icon: 'mdi-account-lock',
        text: 'Qualified Supplier <br />Information',
        to: RouteNames.QS_ACCESS_INFORMATION,
        disabled: false,
        valid: getMhrUserAccessValidation.value.qsInformationValid &&
          getMhrUserAccessValidation.value.qsSaConfirmValid &&
          getMhrUserAccessValidation.value.qsLocationValid,
        component: QsInformation
      },
      {
        id: 'step-2-btn',
        step: 2,
        icon: 'mdi-text-box-check-outline',
        text: 'Review <br />and Confirm',
        to: RouteNames.QS_ACCESS_REVIEW_CONFIRM,
        disabled: false,
        valid: getMhrUserAccessValidation.value.qsReviewConfirmValid,
        component: QsReviewConfirm
      }
    ]
  })
  const getMhrSteps = computed(() => {
    return isMhrManufacturerRegistration.value ? getMhrManufacturerSteps.value : getMhrStaffSteps.value
  })
  const getFooterButtonConfig = computed<ButtonConfigIF[]>(() => {
    return isMhrRegistration.value || isMhrReRegistration.value
      ? getMhrButtonFooterConfig.value
      : RegistrationButtonFooterConfig
  })
  const getMhrButtonFooterConfig = computed<ButtonConfigIF[]>(() => {
    return isMhrManufacturerRegistration.value
      ? MHRManufacturerButtonFooterConfig
      : useMhrCorrections().isMhrCorrection.value ? MHRCorrectionButtonFooterConfig : MHRButtonFooterConfig
  })
  const isBusySaving = computed<boolean>(() => {
    return false
    // (state.value.isSaving || state.value.isSavingResuming || state.value.isFilingPaying)
  })
  const isRegistrationValid = computed<boolean>(() => {
    return (
      state.value.registration.lengthTrust.valid &&
      state.value.registration.parties.valid &&
      state.value.registration.collateral.valid
    )
  })
  const getRegTableData = computed<RegTableDataI>(() => {
    return state.value.registrationTable
  })
  const getRegTableBaseRegs = computed<RegistrationSummaryIF[]>(() => {
    return state.value.registrationTable.baseRegs
  })
  const getMhRegTableBaseRegs = computed<MhRegistrationSummaryIF[]>(() => {
    return state.value.registrationTable.baseMhRegs
  })
  const getRegTableDraftsBaseReg = computed<DraftResultIF[]>(() => {
    return state.value.registrationTable.draftsBaseReg
  })
  const getRegTableDraftsChildReg = computed<DraftResultIF[]>(() => {
    return state.value.registrationTable.draftsChildReg
  })
  const getRegTableNewItem = computed<RegTableNewItemI>(() => {
    return state.value.registrationTable.newItem
  })
  const getRegTableSortOptions = computed<RegistrationSortIF>(() => {
    return state.value.registrationTable.sortOptions
  })
  const getRegTableMhSortOptions = computed<RegistrationSortIF>(() => {
    return state.value.registrationTable.mhSortOptions
  })
  const getRegTableSortPage = computed<number>(() => {
    return state.value.registrationTable.sortPage
  })
  const getRegTableTotalRowCount = computed<number>(() => {
    return state.value.registrationTable.totalRowCount
  })
  const hasMorePages = computed<boolean>(() => {
    return state.value.registrationTable.sortHasMorePages
  })
  const getMhrHomeSections = computed<HomeSectionIF[]>(() => {
    return state.value.mhrRegistration.description.sections
  })
  // MHR Getters
  const getMhrDraftNumber = computed<string>(() => {
    return state.value.mhrRegistration.draftNumber
  })
  const getMhrRegistration = computed<MhrRegistrationIF>(() => {
    return state.value.mhrRegistration
  })
  const getMhrRegistrationManufacturerName = computed<string>(() => {
    return state.value.mhrRegistration.description.manufacturer
  })
  const getMhrRegistrationYearOfManufacture = computed<number>(() => {
    return state.value.mhrRegistration.description.baseInformation.year
  })
  const getMhrRegistrationIsYearApproximate = computed<boolean>(() => {
    return state.value.mhrRegistration.description.baseInformation.circa
  })
  const getMhrRegistrationHomeMake = computed<string>(() => {
    return state.value.mhrRegistration.description.baseInformation.make
  })
  const getMhrRegistrationHomeModel = computed<string>(() => {
    return state.value.mhrRegistration.description.baseInformation.model
  })
  const getMhrRegistrationOtherInfo = computed<string>(() => {
    return state.value.mhrRegistration.description.otherRemarks
  })
  const getMhrRegistrationHomeDescription = computed<MhrRegistrationDescriptionIF>(() => {
    return state.value.mhrRegistration.description
  })
  const getMhrRegistrationSubmittingParty = computed<SubmittingPartyIF>(() => {
    return state.value.mhrRegistration.submittingParty
  })
  const getMhrRegistrationHomeOwners = computed<MhrRegistrationHomeOwnerIF[]>(() => {
    const owners = [] as MhrRegistrationHomeOwnerIF[]
    state.value.mhrRegistration.ownerGroups.forEach((group: any) => {
      if (group.owners.length === 0) {
        // Groups with no owners should have at least one 'placeholder' owner
        // to be properly displayed in Group Table
        owners.push(({ groupId: group.groupId } as MhrRegistrationHomeOwnerIF))
      } else {
        group.owners.forEach((owner: any) => owners.push({ ...owner, groupId: group.groupId }))
      }
    })
    return owners
  })
  const getMhrRegistrationDocumentId = computed<string>(() => {
    return state.value.mhrRegistration.documentId
  })
  const getMhrAttentionReference = computed<any>(() => {
    return state.value.mhrRegistration.attentionReference
  })
  const getMhrRegistrationLocation = computed<MhrRegistrationHomeLocationIF>((): MhrRegistrationHomeLocationIF => {
    return state.value.mhrRegistration.location
  })
  const getIsManualLocation = computed<boolean>(() => {
    return state.value.mhrRegistration.isManualLocationInfo
  })
  const getMhrRegistrationHomeOwnerGroups = computed<MhrRegistrationHomeOwnerGroupIF[]>(() => {
    const ownerGroups: MhrRegistrationHomeOwnerGroupIF[] = state.value.mhrRegistration.ownerGroups
    // add groupId to each owner in every group - required for HomeOwnersTable
    for (const group of ownerGroups) {
      for (const owner of group.owners) {
        owner.groupId = group.groupId
      }
    }
    return ownerGroups
  })
  const getMhrRegistrationValidationModel = computed<MhrValidationStateIF | MhrValidationManufacturerStateIF>(() => {
    return isMhrManufacturerRegistration.value
      ? state.value.mhrValidationManufacturerState
      : state.value.mhrValidationState
  })
  const getMhrInformation = computed<MhRegistrationSummaryIF>(() => {
    return state.value.mhrInformation
  })
  const hasLien = computed<boolean>(() => {
    // Current state is to verify the property exists. Future state may be more granular dependent on type.
    return !!state.value.mhrInformation.lienRegistrationType
  })
  const getLienRegistrationType = computed<string>(() => {
    return state.value.mhrInformation.lienRegistrationType
  })
  const getMhrUnitNotes: ComputedRef<Array<UnitNoteIF | CancelUnitNoteIF>> =
    computed<Array<UnitNoteIF | CancelUnitNoteIF>>(() => {
      return state.value.mhrUnitNotes
    })
  const getMhrRegistrationOwnLand = computed<boolean>(() => {
    return state.value.mhrRegistration.ownLand
  })

  // Mhr Correction
  const getMhrBaseline = computed<MhrRegistrationIF>(() => {
    return state.value.mhrBaseline
  })
  const getMhrStatusType = computed<MhApiStatusTypes>(() => {
    return state.value.mhrRegistration.statusType
  })

  const getMhrUnitNoteRegistration = computed<UnitNoteRegistrationIF>(() => {
    return state.value.mhrUnitNote
  })

  const getMhrUnitNote = computed<UnitNoteIF | CancelUnitNoteIF>(() => {
    return state.value.mhrUnitNote.note
  })

  const getMhrUnitNoteType = computed<UnitNoteDocTypes>(() => {
    return state.value.mhrUnitNote.note.documentType
  })

  const getMhrUnitNoteValidation = computed(() => {
    return state.value.mhrUnitNoteValidationState
  })

  // Re-Registration Getters
  const isMhrReRegistration = computed<boolean>(() => {
    return isRoleStaffReg.value &&
      state.value.registration?.registrationType?.registrationTypeAPI === APIRegistrationTypes.MHR_RE_REGISTRATION
  })
  const getMhrReRegistrationPreviousOwnerGroups = computed((): MhrRegistrationHomeOwnerGroupIF[] => {
    return state.value.mhrReRegistrationPreviousOwnerGroups
  })
  const getMhrReRegistrationPreviousTenancyType = computed((): string => {
    return state.value.mhrReRegistrationPreviousTenancyType
  })

  /** MHR Getters **/
  const getMhrInfoValidation = computed(() => {
    return state.value.mhrInfoValidationState
  })
  const getMhrTransferHomeOwners = computed(() => {
    const owners = [] as MhrRegistrationHomeOwnerIF[]
    state.value.mhrTransfer.ownerGroups.forEach((group) => {
      if (group.owners.length === 0) {
        owners.push(({ groupId: group.groupId } as MhrRegistrationHomeOwnerIF))
      } else {
        group.owners.forEach((owner) => owners.push({ ...owner, groupId: group.groupId }))
      }
    })
    return owners
  })
  const getMhrTransferHomeOwnerGroups = computed((): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownerGroups: MhrRegistrationHomeOwnerGroupIF[] = state.value.mhrTransfer.ownerGroups
    // add groupId to each owner in every group - required for HomeOwnersTable
    for (const group of ownerGroups) {
      for (const owner of group.owners) {
        owner.groupId = group.groupId
      }
    }
    return ownerGroups
  })
  const getMhrTransferCurrentHomeOwnerGroups = computed(() => {
    return state.value.mhrTransfer.currentOwnerGroups
  })
  const getMhrTransferDocumentId = computed(() => {
    return state.value.mhrTransfer.documentId
  })
  const getMhrTransferType = computed(() => {
    return state.value.mhrTransfer.transferType
  })
  const getMhrTransferDeclaredValue = computed(() => {
    return state.value.mhrTransfer.declaredValue
  })
  const getMhrTransferConsideration = computed(() => {
    return state.value.mhrTransfer.consideration
  })
  const getMhrTransferDate = computed(() => {
    return state.value.mhrTransfer.transferDate
  })
  const getMhrTransferOwnLand = computed(() => {
    return state.value.mhrTransfer.ownLand
  })
  const getMhrAccountSubmittingParty = computed(() => {
    return state.value.mhrTransfer.submittingParty
  })
  const getMhrTransferAttentionReference = computed(() => {
    return state.value.mhrTransfer.attentionReference
  })
  const getMhrTransferAffidavitCompleted = computed(() => {
    return state.value.mhrTransfer.isAffidavitTransferCompleted
  })
  // User Access Flow
  const getMhrSubProduct = computed((): MhrSubTypes => {
    return state.value.mhrUserAccess.mrhSubProduct
  })
  const getMhrQsInformation = computed((): PartyIF => {
    return state.value.mhrUserAccess.qsInformation
  })
  const getMhrQsHomeLocation = computed((): AddressIF  => {
    return state.value.mhrUserAccess.location.address
  })
  const getMhrQsSubmittingParty = computed((): AccountInfoIF => {
    return state.value.mhrUserAccess.qsSubmittingParty
  })
  const getMhrQsIsRequirementsConfirmed = computed((): boolean => {
    return state.value.mhrUserAccess.isRequirementsConfirmed
  })
  const getMhrQsAuthorization = computed((): UserAccessAuthorizationIF => {
    return state.value.mhrUserAccess.authorization
  })
  const getMhrUserAccessValidation = computed((): UserAccessValidationIF => {
    return state.value.mhrUserAccessValidation
  })
  // Exemptions
  const getMhrExemptionSteps = computed(() => {
    return [
      {
        id: 'step-1-btn',
        step: 1,
        icon: 'mdi-home',
        text: 'Verify<br/>Home Details',
        to: RouteNames.EXEMPTION_DETAILS,
        disabled: false,
        valid: getMhrExemptionValidation.value.documentId && getMhrExemptionValidation.value.remarks &&
          getMhrExemptionValidation.value.declarationDetails,
        component: ExemptionDetails
      },
      {
        id: 'step-2-btn',
        step: 2,
        icon: 'mdi-text-box-check-outline',
        text: 'Review<br/>and Confirm',
        to: RouteNames.EXEMPTION_REVIEW,
        disabled: false,
        valid: isMhrExemptionValid.value,
        component: ExemptionReview
      }
    ]
  })
  const getMhrExemption = computed((): ExemptionIF => {
    return state.value.mhrExemption
  })
  const getMhrExemptionValidation = computed((): ExemptionValidationIF => {
    return state.value.mhrExemptionValidation
  })
  const isMhrExemptionValid = computed(() => {
    return Object.values(getMhrExemptionValidation.value).every(value => value)
  })
  const getMhrExemptionNote = computed((): ExemptionNoteIF => {
    return state.value.mhrExemption.note
  })

   // MHR Transport Permit
  const getMhrTransportPermit = computed((): MhrTransportPermitIF => {
    return state.value.mhrTransportPermit
  })

  // get new location without address for amend comparison
  const getMhrTransportPermitHomeLocation = computed((): MhrRegistrationHomeLocationWithoutAddressIF => {
    return omit(state.value.mhrTransportPermit?.newLocation, 'address')
  })

  const getMhrOriginalTransportPermit = computed((): MhrTransportPermitIF => {
    return state.value.mhrOriginalTransportPermit
  })

  // get original new location without address for amend comparison
  const getMhrOriginalTransportPermitHomeLocation = computed((): MhrRegistrationHomeLocationWithoutAddressIF => {
    return omit(state.value.mhrOriginalTransportPermit?.newLocation, 'address')
  })

  const getMhrTransportPermitPreviousLocation = computed((): MhrRegistrationHomeLocationIF => {
    return state.value.mhrTransportPermit.previousLocation
  })

  // get original status of the registration when working with amendments
  const getMhrOriginalTransportPermitRegStatus = computed((): string => {
    return state.value.mhrOriginalTransportPermit.registrationStatus
  })

  // get a flag to indicate if change to the Transport Permit are allowed
  const getTransportPermitChangeAllowed = computed((): boolean => {
    return state.value.mhrInformation.changePermit
  })

  /** Actions **/
  function resetNewRegistration () {
    state.value.registration.registrationNumber = null
    state.value.registration.showStepErrors = false
    state.value.registration.lengthTrust.valid = false
    state.value.registration.lengthTrust.showInvalid = false
    state.value.registration.lengthTrust.lifeInfinite = false
    state.value.registration.lengthTrust.trustIndenture = false
    state.value.registration.lengthTrust.lifeYears = 0
    state.value.registration.lengthTrust.lienAmount = ''
    state.value.registration.lengthTrust.surrenderDate = ''
    state.value.registration.collateral.valid = false
    state.value.registration.collateral.showInvalid = false
    state.value.registration.collateral.generalCollateral = []
    state.value.registration.collateral.vehicleCollateral = []
    state.value.registration.parties.valid = false
    state.value.registration.parties.showInvalid = false
    state.value.registration.parties.registeringParty = null
    state.value.registration.parties.securedParties = []
    state.value.registration.parties.debtors = []
    state.value.registration.draft = {
      type: null,
      financingStatement: null,
      amendmentStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    }
    state.value.registration.registrationFlowType = RegistrationFlowType.NEW
    state.value.registration.confirmDebtorName = null
    state.value.registration.courtOrderInformation = {
      orderDate: '',
      effectOfOrder: '',
      courtName: '',
      courtRegistry: '',
      fileNumber: ''
    }
    state.value.registration.amendmentDescription = ''
    state.value.certifyInformation = {
      valid: false,
      certified: false,
      legalName: ''
    }
    state.value.folioOrReferenceNumber = ''
    state.value.staffPayment = {
      option: -1,
      routingSlipNumber: '',
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: '',
      isPriority: false
    }
    state.value.registration.securitiesActNotices = []
    setUnsavedChanges(false)
  }

  function resetMhrInformation () {
    setMhrInformation({
      clientReferenceId: '',
      createDateTime: '',
      mhrNumber: '',
      ownerNames: '',
      path: '',
      registrationDescription: '',
      statusType: '',
      submittingParty: '',
      username: '',
      documentId: '',
      lienRegistrationType: '',
      frozenDocumentType: '',
      permitDateTime: '',
      permitExpiryDateTime: '',
      permitRegistrationNumber: '',
      permitStatus: null,
      permitLandStatusConfirmation: null
    })
    setUnsavedChanges(false)
  }

  function resetRegTableData () {
    state.value.registrationTable.baseRegs = []
    state.value.registrationTable.draftsBaseReg = []
    state.value.registrationTable.draftsChildReg = []
    state.value.registrationTable.newItem = {
      addedReg: '',
      addedRegParent: '',
      addedRegSummary: null,
      prevDraft: ''
    }
    state.value.registrationTable.sortHasMorePages = true
    state.value.registrationTable.sortPage = 1
    state.value.registrationTable.totalRowCount = 0
  }

  function setAccountProductSubscription (productSubscriptions: AccountProductSubscriptionIF) {
    state.value.accountProductSubscriptions = productSubscriptions
  }

  function setUserProductSubscriptions (products: UserProductSubscriptionIF[]) {
    state.value.userProductSubscriptions = products
  }

  function setUserProductSubscriptionsCodes (activeProducts: ProductCode[]) {
    state.value.userProductSubscriptionsCodes = activeProducts
  }

  function setAccountInformation (accountInformation: AccountInformationIF) {
    state.value.accountInformation = accountInformation
  }

  function setAddCollateral (addCollateral: AddCollateralIF) {
    state.value.registration.collateral = addCollateral
    setUnsavedChanges(true)
  }

  function setOriginalAddCollateral (addCollateral: AddCollateralIF) {
    state.value.originalRegistration.collateral = addCollateral
  }

  function setAddSecuredPartiesAndDebtors (addParties: AddPartiesIF) {
    state.value.registration.parties = addParties
    setUnsavedChanges(true)
  }

  function setOriginalAddSecuredPartiesAndDebtors (addParties: AddPartiesIF) {
    state.value.originalRegistration.parties = addParties
  }

  function setAmendmentDescription (description: string) {
    state.value.registration.amendmentDescription = description
    setUnsavedChanges(true)
  }

  function setAuthRoles (authRoles: string[]) {
    state.value.authorization.authRoles = authRoles
  }

  function setRoleSbc (isSbc: boolean) {
    state.value.authorization.isSbc = isSbc
    const roles = state.value.authorization.authRoles

    if (isSbc) {
      !roles.includes('sbc') && roles.push('sbc')
    } else {
      state.value.authorization.authRoles = roles.filter(role => role !== 'sbc')
    }
  }

  function setCertifyInformation (certifyInformation: CertifyIF) {
    state.value.certifyInformation = certifyInformation
  }

  function setStaffPayment (staffPayment: StaffPaymentIF) {
    state.value.staffPayment = staffPayment
  }

  function setIsStaffClientPayment (isStaffClientPayment: boolean) {
    state.value.isStaffClientPayment = isStaffClientPayment
  }

  function setCollateralShowInvalid (show: boolean) {
    state.value.registration.collateral.showInvalid = show
  }

  function setCollateralValid (valid: boolean) {
    state.value.registration.collateral.valid = valid
  }

  function setCourtOrderInformation (courtOrderInformation: CourtOrderIF) {
    state.value.registration.courtOrderInformation = courtOrderInformation
    setUnsavedChanges(true)
  }

  function setDraft (draft: DraftIF) {
    state.value.registration.draft = draft
  }

  function setGeneralCollateral (generalCollateral: GeneralCollateralIF[]) {
    state.value.registration.collateral.generalCollateral = generalCollateral
    setUnsavedChanges(true)
  }

  function setLengthTrust (lengthTrust: LengthTrustIF) {
    state.value.registration.lengthTrust = lengthTrust
    setUnsavedChanges(true)
  }

  function setOriginalLengthTrust (lengthTrust: LengthTrustIF) {
    state.value.originalRegistration.lengthTrust = lengthTrust
  }

  function setSecuritiesActNotices (notices: Array<AddEditSaNoticeIF>) {
    state.value.registration.securitiesActNotices = notices
  }

  function setOriginalSecuritiesActNotices (notices: Array<AddEditSaNoticeIF>) {
    state.value.originalRegistration.securitiesActNotices = notices
  }

  function setSecuritiesActNoticeOrder (noticeIndex: number, orderIndex: number, order: CourtOrderIF) {
    state.value.registration.securitiesActNotices[noticeIndex].securitiesActOrders[orderIndex] = order
  }

  function setRegistrationConfirmDebtorName (debtorName: DebtorNameIF) {
    state.value.registration.confirmDebtorName = debtorName
  }

  function setRegistrationCreationDate (date: string) {
    state.value.registration.creationDate = date
  }

  function setRegistrationExpiryDate (date: string) {
    state.value.registration.expiryDate = date
  }

  function setRegistrationNumber (regNum: string) {
    state.value.registration.registrationNumber = regNum
  }

  function setRegistrationType (registrationType: RegistrationTypeIF) {
    state.value.registration.registrationType = registrationType
  }

  function setRegistrationFlowType (registrationFlowType: RegistrationFlowType) {
    state.value.registration.registrationFlowType = registrationFlowType
  }

  function setRegistrationTypeOtherDesc (description: string) {
    state.value.registration.registrationTypeOtherDesc = description
  }

  function setSearchDebtorName (debtorName: IndividualNameIF) {
    state.value.search.searchDebtorName = debtorName
  }

  function setSearchHistory (searchHistory: SearchResponseIF[]) {
    // need to set .loadingPDF so that the loader circle triggers when set
    //  - if it starts as undefined it wont trigger on change
    for (let i = 0; i < searchHistory?.length || 0; i++) {
      searchHistory[i].loadingPDF = false
      // parse the response from API to check if searchId has Pending suffix (for large reports)
      searchHistory[i].isPending = searchHistory[i].searchId.endsWith('PENDING')
      searchHistory[i].searchId = searchHistory[i].searchId.split('_')[0]
    }

    state.value.search.searchHistory = searchHistory
    state.value.search.searchHistoryLength = searchHistory?.length || 0
  }

  function setSearchResults (searchResults: SearchResponseIF) {
    state.value.search.searchResults = searchResults
  }

  function setManufacturedHomeSearchResults (manufacturedHomeSearchResults: ManufacturedHomeSearchResponseIF) {
    state.value.search.manufacturedHomeSearchResults = manufacturedHomeSearchResults
  }

  function setSelectedManufacturedHomes (selectedManufacturedHomes: ManufacturedHomeSearchResultIF[]) {
    state.value.selectedManufacturedHomes = selectedManufacturedHomes
  }

  function setSearchedType (searchedType: SearchTypeIF) {
    state.value.search.searchedType = searchedType
  }

  function setSearchedValue (searchedValue: string) {
    state.value.search.searchedValue = searchedValue
  }

  function setSearching (searching: boolean) {
    state.value.search.searching = searching
  }

  function setSearchCertified (searchCertified: boolean) {
    state.value.search.searchCertified = searchCertified
  }

  function setUserInfo (userInfo: UserInfoIF) {
    state.value.userInfo = userInfo
  }

  function setUserSettings (settings: UserSettingsIF) {
    state.value.userInfo.settings = settings
  }

  function setVehicleCollateral (vCollateral: VehicleCollateralIF[]) {
    state.value.registration.collateral.vehicleCollateral = vCollateral
    setUnsavedChanges(true)
  }

  function setAddSecuredPartiesAndDebtorsStepValidity (validity: boolean) {
    state.value.registration.parties.valid = validity
  }

  function setAddCollateralStepValidity (validity: boolean) {
    state.value.registration.collateral.valid = validity
  }

  function setLengthTrustStepValidity (validity: boolean) {
    state.value.registration.lengthTrust.valid = validity
  }

  function setFolioOrReferenceNumber (refNumber: string) {
    state.value.folioOrReferenceNumber = refNumber
    setUnsavedChanges(true)
  }

  function setShowStepErrors (show: boolean) {
    state.value.registration.showStepErrors = show
  }

  function setRegTableData (regTableData: RegTableDataI) {
    state.value.registrationTable = regTableData
  }

  function setRegTableBaseRegs (baseRegs: RegistrationSummaryIF[]) {
    state.value.registrationTable.baseRegs = baseRegs
  }

  function setRegTableCollapsed () {
    // ensures that the table triggers an update when returning from a new reg / amend / draft when
    // the base reg is already expanded (otherwise the ref does not get set properly and the scroll doesn't work)
    for (let i = 0; i < state.value.registrationTable.baseRegs?.length; i++) {
      state.value.registrationTable.baseRegs[i].expand = false
    }
  }

  function setRegTableDraftsBaseReg (drafts: DraftResultIF[]) {
    state.value.registrationTable.draftsBaseReg = drafts
  }

  function setRegTableDraftsChildReg (drafts: DraftResultIF[]) {
    state.value.registrationTable.draftsChildReg = drafts
  }

  function setRegTableNewItem (newItem: RegTableNewItemI) {
    state.value.registrationTable.newItem = newItem
  }

  function setRegTableSortHasMorePages (hasMorePages: boolean) {
    state.value.registrationTable.sortHasMorePages = hasMorePages
  }

  function setRegTableSortOptions (options: RegistrationSortIF, isMhr: boolean = false) {
    isMhr
    ? state.value.registrationTable.mhSortOptions = options
    : state.value.registrationTable.sortOptions = options
  }

  function setRegTableSortPage (page: number) {
    state.value.registrationTable.sortPage = page
  }

  function setRegTableTotalRowCount (count: number) {
    state.value.registrationTable.totalRowCount = count
  }

  function setUnsavedChanges (unsavedChanges: boolean) {
    state.value.unsavedChanges = unsavedChanges
  }

  function setCurrentRegistrationsTab (currentRegistrationsTab: number) {
    state.value.currentRegistrationsTab = currentRegistrationsTab
  }

  // MHR Registration
  function setEmptyMhr (emptyMhr: MhrRegistrationIF) {
    state.value.mhrRegistration = emptyMhr
  }

  function setMhrDraftNumber (draftNumber: string) {
    state.value.mhrRegistration.draftNumber = draftNumber
  }

  function setMhrHomeDescription ({ key, value }) {
    state.value.mhrRegistration.description[key] = value
    setUnsavedChanges(true)
  }

  function setMhrHomeBaseInformation ({ key, value }) {
    state.value.mhrRegistration.description.baseInformation[key] = value
    setUnsavedChanges(true)
  }

  function setMhrSubmittingParty ({ key, value }) {
    state.value.mhrRegistration.submittingParty[key] = value
    setUnsavedChanges(true)
  }

  function setMhrRegistrationSubmittingParty (submittingParty: SubmittingPartyIF) {
    state.value.mhrRegistration.submittingParty = submittingParty
    setUnsavedChanges(true)
  }

  function setMhrRegistrationDocumentId (value: string) {
    state.value.mhrRegistration.documentId = value
    setUnsavedChanges(true)
  }

  function setMhrGenerateDocId (value: boolean) {
    state.value.generateDocId = value
  }

  function setMhrAttentionReference (value: string) {
    state.value.mhrRegistration.attentionReference = value
    setUnsavedChanges(true)
  }

  function setMhrLocation ({ key, value }) {
    state.value.mhrRegistration.location[key] = value
    setUnsavedChanges(true)
  }

  function setMhrLocationAllFields (location: MhrRegistrationHomeLocationIF) {
    state.value.mhrRegistration.location = location
  }

  function setIsManualLocation (isManual: boolean) {
    state.value.mhrRegistration.isManualLocationInfo = isManual
  }

  function setCivicAddress (stateKey: string, { key, value }) {
    state.value[stateKey].location.address[key] = value
    setUnsavedChanges(true)
  }

  function setMhrRegistrationHomeOwnerGroups (groups: MhrRegistrationHomeOwnerGroupIF[]) {
    state.value.mhrRegistration.ownerGroups = groups
    setUnsavedChanges(true)
  }

  function setMhrCorrectStatusType (status: MhApiStatusTypes) {
    state.value.mhrRegistration.statusType = status
  }

  function setMhrTableHistory (baseRegs: MhRegistrationSummaryIF[]) {
    state.value.registrationTable.baseMhRegs = baseRegs
  }

  // MHR Re-Registration
  function setMhrReRegistrationPreviousOwnerGroups (ownerGroups: MhrRegistrationHomeOwnerGroupIF[]) {
    state.value.mhrReRegistrationPreviousOwnerGroups = ownerGroups
  }

  function setMhrReRegistrationPreviousTenancyType (tenancyType: string) {
    state.value.mhrReRegistrationPreviousTenancyType = tenancyType
  }

  // MHR Information
  function setMhrNumber (mhrNumber: string) {
    state.value.mhrInformation.mhrNumber = mhrNumber
  }

  function setMhrInformation (mhrInfo: MhRegistrationSummaryIF) {
    state.value.mhrInformation = mhrInfo
  }

  function setMhrInformationDraftId (draftId: string) {
    state.value.mhrInformation.draftNumber = draftId
  }

  function setMhrStatusType (status: MhApiStatusTypes) {
    state.value.mhrInformation.statusType = status
  }

  function setMhrFrozenDocumentType (docType: string) {
    state.value.mhrInformation.frozenDocumentType = docType
  }

  function setMhrExemptDateTime (dateTime: string) {
    state.value.mhrInformation.exemptDateTime = dateTime
  }

  function setLienType (lienType: string) {
    state.value.mhrInformation.lienRegistrationType = lienType
  }

  function setMhrInformationPermitData ({ permitKey, permitData }) {
    state.value.mhrInformation[`permit${permitKey}`] = permitData
  }

  function setTransportPermitChangeAllowed (changePermit: boolean) {
    state.value.mhrInformation.changePermit = changePermit
  }

  function setMhrUnitNotes (unitNotes: Array<UnitNoteIF>) {
    state.value.mhrUnitNotes = unitNotes
  }

  function setMhrBaseline (registration: MhrRegistrationIF) {
    state.value.mhrBaseline = registration
  }

  /** MHR Ownership Transfer Actions */
  function setEmptyMhrTransfer (emptyMhrTransfer: MhrTransferIF) {
    state.value.mhrTransfer = emptyMhrTransfer
  }

  function setMhrTransferHomeOwnerGroups (groups: MhrRegistrationHomeOwnerGroupIF[]) {
    state.value.mhrTransfer.ownerGroups = groups
    setUnsavedChanges(true)
  }

  // MHR Transport Permit
  function setEmptyMhrTransportPermit (emptyTransportPermit: MhrTransportPermitIF) {
    state.value.mhrTransportPermit = emptyTransportPermit
  }

  function setMhrTransportPermitLocationChangeType (locationChangeType: LocationChangeTypes) {
    state.value.mhrTransportPermit.locationChangeType = locationChangeType
  }

  function setMhrTransportPermit ({ key, value }) {
    state.value.mhrTransportPermit[key] = value
    setUnsavedChanges(true)
  }

  function setMhrTransportPermitNewLocation ({ key, value }) {
    state.value.mhrTransportPermit.newLocation[key] = value
    setUnsavedChanges(true)
  }

  function setMhrTransportPermitNewPad (pad: string) {
    state.value.mhrTransportPermit.newLocation.pad = pad
  }

  function setMhrTransportPermitNewCivicAddress ({ key, value }) {
    state.value.mhrTransportPermit.newLocation.address[key] = value
    setUnsavedChanges(true)
  }

  function setMhrTransportPermitPreviousLocation (prevLocation: MhrRegistrationHomeLocationIF) {
    state.value.mhrTransportPermit.previousLocation = prevLocation
  }

  /** Original Transport Permit filing when working with Amendments */
  function setMhrOriginalTransportPermit ({ key, value }) {
    state.value.mhrOriginalTransportPermit[key] = value
  }

  /** Set a snapshot of the MH Registration home owner groups */
  function setMhrTransferCurrentHomeOwnerGroups (groups: MhrRegistrationHomeOwnerGroupIF[]) {
    state.value.mhrTransfer.currentOwnerGroups = groups
  }

  function setMhrTransferDocumentId (documentId: string) {
    state.value.mhrTransfer.documentId = documentId
  }

  function setMhrTransferType (transferType: TransferTypeSelectIF) {
    state.value.mhrTransfer.transferType = transferType
  }

  function setMhrTransferDeclaredValue (declaredValue: number) {
    state.value.mhrTransfer.declaredValue = declaredValue
  }

  function setMhrTransferConsideration (consideration: string) {
    state.value.mhrTransfer.consideration = consideration
  }

  function setMhrTransferDate (transferDate: string) {
    state.value.mhrTransfer.transferDate = transferDate
  }

  function setMhrTransferOwnLand (isOwnLand: boolean) {
    state.value.mhrTransfer.ownLand = isOwnLand
  }

  function setMhrAccountSubmittingParty (submittingPartyInfo: SubmittingPartyIF) {
    state.value.mhrTransfer.submittingParty = submittingPartyInfo
  }

  function setMhrTransferAttentionReference (attentionReference: string) {
    state.value.mhrTransfer.attentionReference = attentionReference
  }

  function setMhrTransferAffidavitCompleted (isAffidavitCompleted: boolean) {
    state.value.mhrTransfer.isAffidavitTransferCompleted = isAffidavitCompleted
  }

  function setMhrRegistrationOwnLand (ownLand: boolean) {
    state.value.mhrRegistration.ownLand = ownLand
    setUnsavedChanges(true)
  }

  // MHR Unit Notes
  function setMhrUnitNoteType (documentType: UnitNoteDocTypes) {
    state.value.mhrUnitNote.note.documentType = documentType
  }

  function setEmptyUnitNoteRegistration (unitNote: UnitNoteRegistrationIF) {
    state.value.mhrUnitNote = unitNote
  }

  function setMhrUnitNoteRegistration (storeAction: UnitNoteStoreActionIF) {
    state.value.mhrUnitNote[storeAction.key] = storeAction.value
  }

  function setMhrUnitNote (unitNote: UnitNoteIF | CancelUnitNoteIF) {
    state.value.mhrUnitNote.note = unitNote
  }

  function setMhrUnitNoteProp (storeAction: UnitNoteStoreActionIF) {
    state.value.mhrUnitNote.note[storeAction.key] = storeAction.value
  }

  // User Access Flow
  function setMhrSubProduct (subProduct: MhrSubTypes) {
    state.value.mhrUserAccess.mrhSubProduct = subProduct
  }

  function setMhrQsInformation (qsInformation: PartyIF) {
    state.value.mhrUserAccess.qsInformation = qsInformation
  }

  function setMhrQsSubmittingParty (qsSubmittingParty: AccountInfoIF) {
    state.value.mhrUserAccess.qsSubmittingParty = qsSubmittingParty
  }

  function setMhrQsIsRequirementsConfirmed (isRequirementsConfirmed: boolean) {
    state.value.mhrUserAccess.isRequirementsConfirmed = isRequirementsConfirmed
  }

  function setMhrQsAuthorization (authorization: UserAccessAuthorizationIF) {
    state.value.mhrUserAccess.authorization = authorization
  }

  function setMhrQsValidation (qsValidation: { key: string, value: boolean }) {
    state.value.mhrUserAccessValidation[qsValidation.key] = qsValidation.value
  }

  // Exemptions
  function setMhrExemption (value: ExemptionIF) {
    state.value.mhrExemption = value
  }

  function setMhrExemptionValue ({ key, value }) {
    state.value.mhrExemption[key] = value
  }

  function setMhrExemptionNote ({ key, value }) {
    state.value.mhrExemption.note[key] = value
  }

  function setMhrExemptionValidation ({ key, value }) {
    state.value.mhrExemptionValidation[key] = value
  }

  return {
    // User-related getters
    getAccountModel,
    getCurrentUser,
    getUserEmail,
    getUserFirstName,
    getUserLastName,
    getUserRoles,
    getUserUsername,
    getUserServiceFee,
    getUserSettings,
    getUserMiscSettingsByKey,

    // Account-related getters
    getAccountId,
    getAccountLabel,
    isPremiumAccount,
    getAccountProductSubscriptions,
    getUserProductSubscriptions,
    getUserProductSubscriptionsCodes,

    // Role-related getters
    isRoleStaffSbc,
    isRoleStaff,
    isRoleStaffBcol,
    isRoleStaffReg,
    isRoleManufacturer,
    isRoleQualifiedSupplier,
    isRoleQualifiedSupplierHomeDealer,
    isRoleQualifiedSupplierLawyersNotaries,
    hasPprRole,
    hasMhrRole,

    // PPR/MHR Enabled
    hasPprEnabled,
    hasMhrEnabled,
    hasMhrReIssuePermitEnabled,

    // Document Record Service
    hasDrsEnabled,

    // Add Collateral getters
    getAddCollateral,
    getOriginalAddCollateral,

    // Amendment getters
    getAmendmentDescription,

    // Secured Parties and Debtors getters
    getAddSecuredPartiesAndDebtors,
    getOriginalAddSecuredPartiesAndDebtors,

    // Debtor Name getters
    getConfirmDebtorName,
    getSearchDebtorName,

    // Registration getters
    getCertifyInformation,
    getCourtOrderInformation,
    getCurrentRegistrationsTab,
    getDraft,
    getGeneralCollateral,
    getLengthTrust,
    getOriginalLengthTrust,
    getSecuritiesActNotices,
    getOriginalSecuritiesActNotices,
    getRegistrationCreationDate,
    getRegistrationExpiryDate,
    getRegistrationSurrenderDate,
    getRegistrationNumber,
    getRegistrationType,
    isMhrRegistration,
    isMhrStaffRegistration,
    isMhrManufacturerRegistration,
    isMhrRegistrationReviewValid,
    getRegistrationFlowType,
    getRegistrationOther,
    getRegistration,

    // Re-Registration Getters
    isMhrReRegistration,
    getMhrReRegistrationPreviousOwnerGroups,
    getMhrReRegistrationPreviousTenancyType,

    // Search getters
    getSearchResults,
    getManufacturedHomeSearchResults,
    getSelectedManufacturedHomes,
    getSearchedType,
    getSearchedValue,
    getSearchHistory,
    getSearchHistoryLength,

    // Vehicle Collateral getter
    getVehicleCollateral,

    // Miscellaneous getters
    getStateModel,
    hasUnsavedChanges,
    isNonBillable,
    isSearching,
    isSearchCertified,
    getFolioOrReferenceNumber,
    getStaffPayment,
    getIsStaffClientPayment,
    getMhrGenerateDocId,
    showStepErrors,

    // Steps and Navigation getters
    getPprSteps,
    getMhrSteps,
    getMhrStaffSteps,
    getUserAccessSteps,
    getMhrManufacturerSteps,
    getFooterButtonConfig,
    isBusySaving,
    isRegistrationValid,

    // Registration Table getters
    getRegTableData,
    getRegTableBaseRegs,
    getMhRegTableBaseRegs,
    getRegTableDraftsBaseReg,
    getRegTableDraftsChildReg,
    getRegTableNewItem,
    getRegTableSortOptions,
    getRegTableMhSortOptions,
    getRegTableSortPage,
    getRegTableTotalRowCount,
    hasMorePages,

    // MHR-related getters
    getMhrHomeSections,
    getMhrDraftNumber,
    getMhrUnitNotes,
    getMhrRegistration,
    getMhrRegistrationManufacturerName,
    getMhrRegistrationYearOfManufacture,
    getMhrRegistrationIsYearApproximate,
    getMhrRegistrationHomeMake,
    getMhrRegistrationHomeModel,
    getMhrRegistrationOtherInfo,
    getMhrRegistrationHomeDescription,
    getMhrRegistrationSubmittingParty,
    getMhrRegistrationHomeOwners,
    getMhrRegistrationDocumentId,
    getMhrAttentionReference,
    getMhrRegistrationLocation,
    getIsManualLocation,
    getMhrRegistrationHomeOwnerGroups,
    getMhrRegistrationValidationModel,
    getMhrInformation,
    getMhrRegistrationOwnLand,

    // Mhr Corrections
    getMhrBaseline,
    getMhrStatusType,

    // Lien-related getter
    hasLien,
    getLienRegistrationType,

    // Mhr Info Validation State
    getMhrInfoValidation,

    // Home Owners
    getMhrTransferHomeOwners,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferCurrentHomeOwnerGroups,

    // Ownership Transfers
    getMhrTransferDocumentId,
    getMhrTransferType,
    getMhrTransferDeclaredValue,
    getMhrTransferConsideration,
    getMhrTransferDate,
    getMhrTransferOwnLand,
    getMhrAccountSubmittingParty,
    getMhrTransferAttentionReference,
    getMhrTransferAffidavitCompleted,

    // MHR Unit Notes
    getMhrUnitNoteRegistration,
    getMhrUnitNote,
    getMhrUnitNoteType, // doc type of the Unit Note to register
    getMhrUnitNoteValidation,

    // MHR User Access
    getMhrSubProduct,
    getMhrQsInformation,
    getMhrQsHomeLocation,
    getMhrQsSubmittingParty,
    getMhrUserAccessValidation,
    getMhrQsIsRequirementsConfirmed,
    getMhrQsAuthorization,

    // Exemptions
    getMhrExemptionSteps,
    getMhrExemption,
    getMhrExemptionNote,
    getMhrExemptionValidation,
    isMhrExemptionValid,

    // MHR Transport Permit
    getMhrTransportPermit,
    getMhrTransportPermitHomeLocation,
    getMhrOriginalTransportPermit,
    getMhrOriginalTransportPermitHomeLocation,
    getMhrTransportPermitPreviousLocation,
    getMhrOriginalTransportPermitRegStatus,
    getTransportPermitChangeAllowed,

    // ACTIONS

    // Registration
    resetNewRegistration,
    resetRegTableData,
    setAccountProductSubscription,
    setUserProductSubscriptions,
    setUserProductSubscriptionsCodes,
    setAccountInformation,
    setAddCollateral,
    setOriginalAddCollateral,
    setAddSecuredPartiesAndDebtors,
    setOriginalAddSecuredPartiesAndDebtors,
    setAmendmentDescription,
    setAuthRoles,
    setRoleSbc,
    setCertifyInformation,
    setStaffPayment,
    setIsStaffClientPayment,
    setCollateralShowInvalid,
    setCollateralValid,
    setCourtOrderInformation,
    setDraft,
    setGeneralCollateral,
    setLengthTrust,
    setOriginalLengthTrust,
    setSecuritiesActNotices,
    setOriginalSecuritiesActNotices,
    setSecuritiesActNoticeOrder,
    setRegistrationConfirmDebtorName,
    setRegistrationCreationDate,
    setRegistrationExpiryDate,
    setRegistrationNumber,
    setRegistrationType,
    setRegistrationFlowType,
    setRegistrationTypeOtherDesc,
    setSearchDebtorName,
    setSearchHistory,
    setSearchResults,
    setManufacturedHomeSearchResults,
    setSelectedManufacturedHomes,
    setSearchedType,
    setSearchedValue,
    setSearching,
    setSearchCertified,
    setUserInfo,
    setUserSettings,
    setVehicleCollateral,
    setAddSecuredPartiesAndDebtorsStepValidity,
    setAddCollateralStepValidity,
    setLengthTrustStepValidity,
    setFolioOrReferenceNumber,
    setShowStepErrors,
    setRegTableData,
    setRegTableBaseRegs,
    setRegTableCollapsed,
    setRegTableDraftsBaseReg,
    setRegTableDraftsChildReg,
    setRegTableNewItem,
    setRegTableSortHasMorePages,
    setRegTableSortOptions,
    setRegTableSortPage,
    setRegTableTotalRowCount,
    setUnsavedChanges,
    setCurrentRegistrationsTab,

    // MHR Global
    setMhrGenerateDocId,

    // MHR Registration
    setEmptyMhr,
    setMhrDraftNumber,
    setMhrHomeDescription,
    setMhrHomeBaseInformation,
    setMhrSubmittingParty,
    setMhrRegistrationSubmittingParty,
    setMhrRegistrationDocumentId,
    setMhrAttentionReference,
    setMhrLocation,
    setMhrLocationAllFields,
    setIsManualLocation,
    setCivicAddress,
    setMhrRegistrationHomeOwnerGroups,
    setMhrCorrectStatusType,
    setMhrTableHistory,
    setMhrRegistrationOwnLand,

    // MHR Re-Registration
    setMhrReRegistrationPreviousOwnerGroups,
    setMhrReRegistrationPreviousTenancyType,

    // MHR Information
    resetMhrInformation,
    setMhrNumber,
    setMhrInformation,
    setMhrInformationDraftId,
    setMhrStatusType,
    setMhrFrozenDocumentType,
    setMhrExemptDateTime,
    setLienType,
    setMhrInformationPermitData,
    setMhrUnitNotes,
    setMhrBaseline,
    setEmptyMhrTransfer,
    setMhrTransferHomeOwnerGroups,
    setMhrTransferCurrentHomeOwnerGroups,
    setMhrTransferDocumentId,
    setMhrTransferType,
    setMhrTransferDeclaredValue,
    setMhrTransferConsideration,
    setMhrTransferDate,
    setMhrTransferOwnLand,
    setMhrAccountSubmittingParty,
    setMhrTransferAttentionReference,
    setMhrTransferAffidavitCompleted,

    // MHR Transport Permit
    setEmptyMhrTransportPermit,
    setMhrTransportPermitLocationChangeType,
    setMhrTransportPermit,
    setMhrTransportPermitNewLocation,
    setMhrTransportPermitNewPad,
    setMhrTransportPermitNewCivicAddress,
    setMhrTransportPermitPreviousLocation,
    setMhrOriginalTransportPermit,
    setTransportPermitChangeAllowed,

    // MHR Unit Notes
    setMhrUnitNoteType,
    setEmptyUnitNoteRegistration,
    setMhrUnitNoteRegistration,
    setMhrUnitNoteProp,
    setMhrUnitNote,

    // MHR User Access
    setMhrSubProduct,
    setMhrQsInformation,
    setMhrQsSubmittingParty,
    setMhrQsIsRequirementsConfirmed,
    setMhrQsAuthorization,
    setMhrQsValidation,

    // Exemption
    setMhrExemption,
    setMhrExemptionValue,
    setMhrExemptionNote,
    setMhrExemptionValidation
  }
})
