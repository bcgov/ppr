import { computed, ComputedRef, nextTick } from 'vue'
import {
  cleanEmpty,
  convertDate,
  createManufacturer,
  createQualifiedSupplier,
  fromDisplayPhone,
  getAccountInfoFromAuth,
  getAccountMembers,
  getFeatureFlag,
  getKeyByValue,
  getMhrManufacturerInfo,
  getQsServiceAgreements,
  getQualifiedSupplier,
  hasTruthyValue,
  isObjectEqual,
  requestProductAccess,
  updateManufacturer,
  updateProductAccess,
  updateQualifiedSupplier,
  updateUserSettings
} from '@/utils'
import {
  AccountProductMemberships,
  ApiHomeTenancyTypes,
  HomeLocationTypes,
  HomeOwnerPartyTypes,
  MhrSubTypes,
  ProductCode,
  ProductStatus,
  RouteNames,
  SettingOptions
} from '@/enums'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useAuth, useNavigation } from '@/composables'
import {
  AddressIF,
  MhrManufacturerInfoIF,
  MhrQsPayloadIF,
  UserAccessMessageIF,
  UserProductSubscriptionIF
} from '@/interfaces'
import { omit } from 'lodash'

export const useUserAccess = () => {
  const { initializeUserProducts } = useAuth()
  const { goToDash, goToRoute, containsCurrentRoute } = useNavigation()
  const {
    setUserSettings,
    setUnsavedChanges,
    setMhrQsInformation,
    setCivicAddress,
    setMhrSubProduct,
    setMhrQsSubmittingParty,
    setMhrQsAuthorization,
    setMhrQsIsRequirementsConfirmed,
    setMhrQsValidation,
    setIsAccountAdministrator
  } = useStore()
  const {
    getAccountId,
    hasMhrEnabled,
    isRoleStaffReg,
    getCurrentUser,
    getUserSettings,
    getUserLastName,
    getUserFirstName,
    getMhrSubProduct,
    getMhrQsInformation,
    getMhrQsHomeLocation,
    getMhrQsAuthorization,
    getMhrQsSubmittingParty,
    getMhrQsIsRequirementsConfirmed,
    getMhrUserAccessValidation,
    getUserProductSubscriptions,
    getMhrTransferCurrentHomeOwnerGroups,
    getMhrRegistrationLocation
  } = storeToRefs(useStore())

  /** Filters and returns only the specified Mhr Sub Products **/
  const mhrSubProducts: ComputedRef<UserProductSubscriptionIF[]> = computed((): UserProductSubscriptionIF[] => {
    const mhrSubProductCodes = [ProductCode.LAWYERS_NOTARIES, ProductCode.MANUFACTURER, ProductCode.DEALERS]
    return getUserProductSubscriptions.value?.filter(product =>
      Object.values(mhrSubProductCodes).includes(product?.code)
    )
  })

  /** Filters and returns the sub product with a relevant status: prioritize ACTIVE and PENDING **/
  const currentSubProduct: ComputedRef<UserProductSubscriptionIF> = computed((): UserProductSubscriptionIF => {
    return mhrSubProducts.value.find(product => {
      return (
        product.subscriptionStatus === ProductStatus.ACTIVE ||
        product.subscriptionStatus === ProductStatus.PENDING
      )
    }) || mhrSubProducts.value.find(product =>
      product.subscriptionStatus === ProductStatus.REJECTED
    )
  })

  /** Returns true when not staff, on the appropriate routes and the feature flag is enabled **/
  const isQsAccessEnabled: ComputedRef<boolean> = computed((): boolean => {
    return !isRoleStaffReg.value && hasMhrEnabled.value &&
      getFeatureFlag('mhr-user-access-enabled')
  })

  /** Returns true while the account has an active Mhr Sub Product **/
  const hasActiveQsAccess: ComputedRef<boolean> = computed((): boolean => {
    return mhrSubProducts.value?.some(product =>
      product.subscriptionStatus === ProductStatus.ACTIVE
    )
  })

  /** Returns true while staff review the application for the Qualified Supplier access **/
  const hasPendingQsAccess: ComputedRef<boolean> = computed((): boolean => {
    return mhrSubProducts.value?.some(product =>
      product.subscriptionStatus === ProductStatus.PENDING
    )
  })

  /** Returns true while staff have rejected the Qualified Supplier access **/
  const hasRejectedQsAccess: ComputedRef<boolean> = computed((): boolean => {
    return mhrSubProducts.value?.some(product =>
      product.subscriptionStatus === ProductStatus.REJECTED
    )
  })

  /** Returns true while the User is within the User Access Routes **/
  const isUserAccessRoute: ComputedRef<boolean> = computed((): boolean => {
    return containsCurrentRoute(
      [RouteNames.QS_ACCESS_TYPE, RouteNames.QS_ACCESS_INFORMATION, RouteNames.QS_ACCESS_REVIEW_CONFIRM]
    )
  })

  const hasQsApplicationData = computed(() => {
    return hasTruthyValue(getMhrQsInformation.value) || getMhrUserAccessValidation.value.qsSaConfirmValid ||
      getMhrQsIsRequirementsConfirmed.value || getMhrQsAuthorization.value.isAuthorizationConfirmed
  })

  /** Content for the QS Application Caution and Alert component **/
  const qsMsgContent: ComputedRef<UserAccessMessageIF> = computed((): UserAccessMessageIF => {
    const productName = MhrSubTypes[getKeyByValue(ProductCode, currentSubProduct.value?.code)]
    const helpEmail = currentSubProduct.value?.code === ProductCode.LAWYERS_NOTARIES
      ? 'bcolhelp@gov.bc.ca'
      : 'bcregistries@gov.bc.ca'

    const content: UserAccessMessageIF[] = [
      {
        status: ProductStatus.ACTIVE,
        icon: 'mdi-check-circle',
        color: 'success',
        msg: `Your application for Qualified Supplier – ${productName} access to the Manufactured Home
          Registry has been approved.`
      },
      {
        status: ProductStatus.PENDING,
        icon: 'mdi-clock-outline',
        color: 'darkGray',
        msg: `Your application for Qualified Supplier – ${productName} access is under review. You will
          receive email notification once your request has been reviewed.`
      },
      {
        status: ProductStatus.REJECTED,
        icon: 'mdi-alert',
        color: 'error',
        msg: `Your application for Qualified Supplier – ${productName} access has been rejected.
          Refer to your notification email or contact <a href="mailto:${helpEmail}">${helpEmail}</a> for details.
          You can submit a new Qualified Supplier access request once you have all of the required information.`
      }
    ]

    // Return if the account has previously closed the status message
    if (getUserSettings.value[SettingOptions.MISCELLANEOUS_PREFERENCES]?.some(
      setting => setting.accountId === getAccountId.value && !!setting[SettingOptions.QS_STATUS_MSG_HIDE]
    )
    ) { return null }

    return content.find(content => content.status === currentSubProduct.value?.subscriptionStatus)
  })

  /** Returns true while the Authorization Component is valid **/
  const isAuthorizationValid: ComputedRef<boolean> = computed(() => {
    return (
      getMhrQsAuthorization.value.isAuthorizationConfirmed &&
      getMhrQsAuthorization.value.authorizationName.trim() !== '' &&
      getMhrQsAuthorization.value.authorizationName.length <= 150
    )
  })

  /** Returns true while the QS Application is valid **/
  const isValid: ComputedRef<any> = computed((): boolean => {
    return (
      getMhrUserAccessValidation.value.qsInformationValid &&
      getMhrUserAccessValidation.value.qsSaConfirmValid &&
      getMhrQsIsRequirementsConfirmed.value &&
      isAuthorizationValid.value
    )
  })

  /** Returns True if the current user is an Account Admin **/
  const fetchIsAccountAdmin = async (): Promise<void> => {
    const { members } = await getAccountMembers()
    const isAdmin = members?.some(member => member.membershipTypeCode === AccountProductMemberships.ADMIN &&
      member.user && member.user.id === getCurrentUser.value.id
    )
    setIsAccountAdministrator(isAdmin)
  }

  /** Navigate to User Access Home route **/
  const goToUserAccess = async (): Promise<void> => {
    if (!hasPendingQsAccess.value && !isUserAccessRoute.value) {
      await initUserAccess()
      await goToRoute(RouteNames.QS_ACCESS_TYPE)
    }
  }

  /** Initialize user access properties **/
  const initUserAccess = async (defaultType: MhrSubTypes = null): Promise<void> => {
    setMhrSubProduct(defaultType)
    await setQsInformationModel(defaultType, true)
    await resetCivicAddress()

    // Set qs submitting party to state
    const accountInfo = await getAccountInfoFromAuth(getCurrentUser.value)
    setMhrQsSubmittingParty(accountInfo)

    setMhrQsIsRequirementsConfirmed(false)
    setAuthorizationModel()

    // Reset Validations
    setQsDefaultValidation()

    // Set unsaved changes to prompt cancel dialogs on exit
    setUnsavedChanges(true)
  }

  /** Set default state for User Access flow based on Product type **/
  const setQsInformationModel = async (val: MhrSubTypes = null, clearModel: boolean = false) => {
    const defaultQsInfo = {
      businessName: '',
      dbaName: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: null,
        postalCode: '',
        country: null,
        deliveryInstructions: ''
      },
      phoneNumber: '',
      phoneExtension: ''
    }

    // Clear the model, when prompted
    if (clearModel) await setMhrQsInformation(defaultQsInfo)

    // Add or remove DBA property based on Product Type
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { dbaName, ...baseQsInfo } = getMhrQsInformation.value
    const formattedQsInfoModel = [MhrSubTypes.MANUFACTURER, MhrSubTypes.DEALERS].includes(val)
      ? { ...getMhrQsInformation.value, dbaName: getMhrQsInformation.value.dbaName || '' }
      : baseQsInfo

    setMhrQsInformation(formattedQsInfoModel)
    setAuthorizationModel()
  }

  /** Set baseline authorization data **/
  const setAuthorizationModel = () => {
    setMhrQsAuthorization({
      isAuthorizationConfirmed: false,
      authorizationName: getUserFirstName.value + ' ' + getUserLastName.value,
      date: convertDate(new Date(), false, false)
    })
  }

  /** Reset the civic address model to default values **/
  const resetCivicAddress = async () => {
    setCivicAddress('mhrUserAccess', { key: 'street', value: '' })
    setCivicAddress('mhrUserAccess', { key: 'city', value: '' })
    setCivicAddress('mhrUserAccess', { key: 'country', value: null })
    setCivicAddress('mhrUserAccess', { key: 'region', value: null })
  }

  const setQsDefaultValidation = () => {
    // Reset Validations (location flag is defaulted to true)
    for (const flag in getMhrUserAccessValidation.value) {
      setMhrQsValidation({ key: flag, value: flag === 'qsLocationValid' })
    }
  }

  /** Update Qualified Supplier status message - locally and user settings **/
  const hideStatusMsg = async (hideMsg: boolean): Promise<void> => {
    await updateUserMiscSettings(SettingOptions.QS_STATUS_MSG_HIDE, hideMsg)
  }

  /** Update Misc Preference in User Profile by specifying key and value to update **/
  const updateUserMiscSettings = async (settingKey: SettingOptions, settingValue: string | boolean) => {
    let miscSettings = getUserSettings.value[SettingOptions.MISCELLANEOUS_PREFERENCES] || []

    // Update existing account setting if it exists, otherwise create new misc setting for account.
    if (miscSettings?.find(setting => setting.accountId === getAccountId.value)) {
      miscSettings = miscSettings.map(pref => pref.accountId === getAccountId.value
        ? { ...pref, [settingKey]: settingValue }
        : pref
      )
    } else miscSettings.push({ accountId: getAccountId.value, [SettingOptions.QS_STATUS_MSG_HIDE]: settingValue })

    await updateUserSettings(SettingOptions.MISCELLANEOUS_PREFERENCES, miscSettings)
    await setUserSettings({ ...getUserSettings.value, [SettingOptions.MISCELLANEOUS_PREFERENCES]: miscSettings })
  }

  /** Download QS Service Agreement via user browser **/
  const downloadServiceAgreement = async (): Promise<void> => {
    const serviceAgreementBlob = await getQsServiceAgreements()

    // Create a URL for the blob
    const url = URL.createObjectURL(serviceAgreementBlob)

    // Create a link element and set its attributes
    const link = document.createElement('a')
    link.href = url
    link.download = 'service-agreement.pdf' // Specify the desired filename for the downloaded PDF
    link.style.display = 'none'

    // Append the link to the DOM and trigger a click event
    document.body.appendChild(link)
    link.click()

    // Clean up: remove the link and revoke the blob URL
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * Disable manufacturer/dealer transfer based on name match conditions and restricted to Sole Owners
   * @returns {Promise<boolean>} Promise that returns true when Manufacturer matches name records and is a sole owner
   */
  const disableDealerManufacturerTransfer = async (isDealer: boolean = false): Promise<boolean> => {
    // Ensure there is only one owner group and it's a sole ownership
    const ownerGroups = getMhrTransferCurrentHomeOwnerGroups.value
    if (ownerGroups.length !== 1) return true

    const isSoleOwner = ownerGroups[0].type === ApiHomeTenancyTypes.SOLE
    const currentOwnerName = ownerGroups[0]?.owners[0]?.organizationName || ''

    // If not a sole owner, return true (disabling the transfer)
    if (!isSoleOwner) return true

    // Fetch dealer or manufacturer data based on the provided flag
    let orgName: string | undefined
    let dbaName: string | undefined

    if (isDealer) {
      const dealerData: MhrQsPayloadIF = await getQualifiedSupplier()
      orgName = dealerData?.businessName
      dbaName = dealerData?.dbaName
    } else {
      const manufacturerData: MhrManufacturerInfoIF = await getMhrManufacturerInfo()
      orgName = manufacturerData?.ownerGroups[0]?.owners[0]?.organizationName
      dbaName = manufacturerData?.dbaName
    }

    // Check if current owner's name matches the dealer/manufacturer records (either org or dba name)
    const isNameMatch = currentOwnerName === orgName || currentOwnerName === dbaName

    // Disable transfer if the name doesn't match
    return !isNameMatch
  }

  /**
   * Disable dealer/manufacturer location change based on address match conditions between QS Lot and Home Civic Address
   * @returns {Promise<boolean>} Promise that returns true when dealer/manufacturer address matches lot address
   */
  const disableDealerManufacturerLocationChange = async (isDealer = false): Promise<boolean> => {
    let dealerManufacturerAddress: AddressIF

    if(isDealer) {
      return getMhrRegistrationLocation.value.locationType !== HomeLocationTypes.LOT
    } else {
      const manufacturerData: MhrManufacturerInfoIF = await getMhrManufacturerInfo()
      dealerManufacturerAddress = manufacturerData?.location?.address
    }

    return !isObjectEqual(
      omit(getMhrRegistrationLocation.value?.address, 'postalCode'),
      omit(dealerManufacturerAddress, 'postalCode')
    )
  }

  /**
   * Submit qualified supplier application
   * Includes a request to CREATE a Qualified Supplier in MHR
   * Includes a request to CREATE a TASK for Staff in Auth Web
   */
  const submitQsApplication = async (): Promise<void> => {
    try {
      const qsData: MhrQsPayloadIF|MhrManufacturerInfoIF = getMhrSubProduct.value === MhrSubTypes.MANUFACTURER
        ? await submitManufacturer()
        : await submitQsLawyerNotaryOrDealer()

      const authProductCode = ProductCode[getKeyByValue(MhrSubTypes, getMhrSubProduct.value)]
      let authData = await requestProductAccess(authProductCode)

      // Attempt to patch in the event of a product conflict error
      if (authData?.error && authData.error?.statusCode === 409) {
        authData = await updateProductAccess(authProductCode)
      }

      if (!!qsData && !!authData) {
        // Re-initialize user products to pull status changes on requested sub products
        await initializeUserProducts()
        await nextTick()

        // Reset msg preferences for account on new submission
        await hideStatusMsg(false)

        setUnsavedChanges(false)
        await goToDash()
      }
    } catch (error) {
      console.error('An error occurred:', error)
    }
  }

  /**
   * Submits a request to create or update a Qualified Supplier record.
   * @returns {Promise<MhrQsPayloadIF>} - A promise that resolves to the created or updated payload.
   */
  const submitQsLawyerNotaryOrDealer = async (): Promise<MhrQsPayloadIF> => {
    // Build payload for submission
    const payload: MhrQsPayloadIF = {
      ...cleanEmpty(getMhrQsInformation.value) as MhrQsPayloadIF,
      ...(getMhrSubProduct.value === MhrSubTypes.DEALERS && {
        locationAddress: { ...getMhrQsHomeLocation.value }
      }),
      authorizationName: getMhrQsAuthorization.value.authorizationName,
      termsAccepted: true,
      phoneNumber: fromDisplayPhone(getMhrQsInformation.value.phoneNumber)
    }

    // Check for current QS Record
    const hasQsRecord = await getQualifiedSupplier()

    // Create or Update based on previous record
    return hasQsRecord
      ? await updateQualifiedSupplier(payload)
      : await createQualifiedSupplier(payload)
  }

  /**
   * Submits the manufacturer information.
   * @returns {Promise<MhrManufacturerInfoIF>} Promise that resolves to the manufacturer information.
   * @throws {Error} If there is an error during the submission process.
   */
  const submitManufacturer = async (): Promise<MhrManufacturerInfoIF> => {
    // Build payload for submission
    const payload: MhrManufacturerInfoIF = await buildManufacturerPayload()

    // Check for current Manufacturer Record
    const hasManufacturerRecord = await getMhrManufacturerInfo()

    // Create or Update based on previous record
    return hasManufacturerRecord
      ? await updateManufacturer(payload)
      : await createManufacturer(payload)
  }

  /**
   * Builds the payload object for creating a manufacturer.
   * @returns {Promise<void>} A promise that resolves with no value when the payload is built.
   */
  const buildManufacturerPayload = async (): Promise<MhrManufacturerInfoIF> => {
    // Append dba name to bus name when dba is present
    const consolidatedBusName = getMhrQsInformation.value.dbaName
      ? `${getMhrQsInformation.value.businessName}/${getMhrQsInformation.value.dbaName}`
      : getMhrQsInformation.value.businessName

    return {
      authorizationName: getMhrQsAuthorization.value.authorizationName,
      dbaName: getMhrQsInformation.value.dbaName,
      termsAccepted: true,
      submittingParty: {
        businessName: getMhrQsSubmittingParty.value.name,
        address: getMhrQsSubmittingParty.value.mailingAddress,
        phoneNumber: fromDisplayPhone(getMhrQsSubmittingParty.value.phoneNumber),
        phoneExtension: getMhrQsSubmittingParty.value.phoneExtension
      },
      ownerGroups: [
        {
          groupId: 1,
          type: ApiHomeTenancyTypes.SOLE,
          owners: [
            {
              organizationName: getMhrQsInformation.value.businessName,
              partyType: HomeOwnerPartyTypes.OWNER_BUS,
              address: getMhrQsInformation.value.address,
              phoneNumber: fromDisplayPhone(getMhrQsInformation.value.phoneNumber),
              phoneExtension:getMhrQsInformation.value.phoneExtension
            }
          ]
        }
      ],
      location: {
        locationType: HomeLocationTypes.LOT,
        dealerName: consolidatedBusName,
        address: getMhrQsHomeLocation.value
      },
      description: {
        manufacturer: consolidatedBusName
      }
    } as MhrManufacturerInfoIF
  }

  return {
    isValid,
    initUserAccess,
    goToUserAccess,
    qsMsgContent,
    hideStatusMsg,
    setQsInformationModel,
    setQsDefaultValidation,
    updateUserMiscSettings,
    fetchIsAccountAdmin,
    isQsAccessEnabled,
    hasPendingQsAccess,
    hasRejectedQsAccess,
    hasActiveQsAccess,
    hasQsApplicationData,
    isUserAccessRoute,
    isAuthorizationValid,
    downloadServiceAgreement,
    disableDealerManufacturerTransfer,
    disableDealerManufacturerLocationChange,
    submitQsApplication
  }
}
