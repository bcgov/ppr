import { computed, ComputedRef, nextTick } from 'vue-demi'
import {
  cleanEmpty,
  convertDate,
  createQualifiedSupplier,
  fromDisplayPhone,
  getAccountInfoFromAuth,
  getFeatureFlag,
  getKeyByValue,
  getQsServiceAgreements,
  getQualifiedSupplier,
  hasTruthyValue,
  requestProductAccess,
  updateQualifiedSupplier,
  updateUserSettings
} from '@/utils'
import { MhrSubTypes, ProductCode, ProductStatus, RouteNames, SettingOptions } from '@/enums'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useAuth, useNavigation } from '@/composables'
import { MhrQsPayloadIF, UserAccessMessageIF, UserProductSubscriptionIF } from '@/interfaces'

export const useUserAccess = () => {
  const { initializeUserProducts } = useAuth()
  const { goToDash, goToRoute, containsCurrentRoute } = useNavigation()
  const {
    setUserSettings,
    setUnsavedChanges,
    setMhrQsInformation,
    setMhrSubProduct,
    setMhrQsSubmittingParty,
    setMhrQsAuthorization,
    setMhrQsIsRequirementsConfirmed,
    setMhrQsValidation
  } = useStore()
  const {
    getAccountId,
    hasMhrEnabled,
    isRoleStaffReg,
    getUserSettings,
    getUserLastName,
    getUserFirstName,
    getMhrSubProduct,
    getMhrQsInformation,
    getMhrQsAuthorization,
    getMhrQsIsRequirementsConfirmed,
    getMhrUserAccessValidation,
    getUserProductSubscriptions
  } = storeToRefs(useStore())

  /** Filters and returns only the specified Mhr Sub Products **/
  const mhrSubProducts: ComputedRef<UserProductSubscriptionIF[]> = computed((): UserProductSubscriptionIF[] => {
    const mhrSubProductCodes = [ProductCode.LAWYERS_NOTARIES, ProductCode.MANUFACTURER, ProductCode.DEALERS]
    return getUserProductSubscriptions.value?.filter(product =>
      Object.values(mhrSubProductCodes).includes(product?.code)
    )
  })

  /** Filters and returns the sub product with a relevant status **/
  const currentSubProduct: ComputedRef<UserProductSubscriptionIF> = computed((): UserProductSubscriptionIF => {
    return mhrSubProducts.value.find(product =>
      product.subscriptionStatus !== ProductStatus.NOT_SUBSCRIBED
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
        color: '',
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

  /** Navigate to User Access Home route **/
  const goToUserAccess = async (): Promise<void> => {
    if (!hasPendingQsAccess.value && !isUserAccessRoute.value) {
      await initUserAccess()
      await goToRoute(RouteNames.QS_ACCESS_TYPE)
    }
  }

  /** Initialize user access properties to default state **/
  const initUserAccess = async (defaultType: MhrSubTypes = null): Promise<void> => {
    setMhrSubProduct(defaultType)
    setMhrQsInformation({
      businessName: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: '',
        postalCode: '',
        country: '',
        deliveryInstructions: ''
      },
      phoneNumber: '',
      phoneExtension: ''
    })

    // Set qs submitting party to state
    const accountInfo = await getAccountInfoFromAuth()
    setMhrQsSubmittingParty(accountInfo)

    setMhrQsIsRequirementsConfirmed(false)
    setMhrQsAuthorization({
      isAuthorizationConfirmed: false,
      authorizationName: getUserFirstName.value + ' ' + getUserLastName.value,
      date: convertDate(new Date(), false, false)
    })

    // Reset Validations
    for (const flag in getMhrUserAccessValidation.value) {
      setMhrQsValidation({ key: flag, value: false })
    }

    // Set unsaved changes to prompt cancel dialogs on exit
    setUnsavedChanges(true)
  }

  /** Update Qualified Supplier status message - locally and user settings **/
  const hideStatusMsg = async (hideMsg: boolean): Promise<void> => {
    let msgSettings = getUserSettings.value[SettingOptions.MISCELLANEOUS_PREFERENCES] || []

    // Update existing account setting if it exists, otherwise create new misc setting for account.
    if (msgSettings?.find(setting => setting.accountId === getAccountId.value)) {
      msgSettings = msgSettings.map(pref => pref.accountId === getAccountId.value
        ? { ...pref, [SettingOptions.QS_STATUS_MSG_HIDE]: hideMsg }
        : pref
      )
    } else msgSettings.push({ accountId: getAccountId.value, [SettingOptions.QS_STATUS_MSG_HIDE]: hideMsg })

    await updateUserSettings(SettingOptions.MISCELLANEOUS_PREFERENCES, msgSettings)
    await setUserSettings({ ...getUserSettings.value, [SettingOptions.MISCELLANEOUS_PREFERENCES]: msgSettings })
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
   * Submit qualified supplier application
   * Includes a request to CREATE a Qualified Supplier in MHR
   * Includes a request to CREATE a TASK for Staff in Auth Web
   */
  const submitQsApplication = async (): Promise<void> => {
    const payload: MhrQsPayloadIF = {
      ...cleanEmpty(getMhrQsInformation.value) as MhrQsPayloadIF,
      authorizationName: getMhrQsAuthorization.value.authorizationName,
      phoneNumber: fromDisplayPhone(getMhrQsInformation.value.phoneNumber)
    }

    try {
      // Check for current QS Record
      const hasQsRecord = await getQualifiedSupplier()

      // Create or Update based on previous record
      const qsData: MhrQsPayloadIF = hasQsRecord
        ? await updateQualifiedSupplier(payload)
        : await createQualifiedSupplier(payload)

      const authProductCode = ProductCode[getKeyByValue(MhrSubTypes, getMhrSubProduct.value)]
      const authData = await requestProductAccess(authProductCode)

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

  return {
    isValid,
    initUserAccess,
    goToUserAccess,
    qsMsgContent,
    hideStatusMsg,
    isQsAccessEnabled,
    hasPendingQsAccess,
    hasRejectedQsAccess,
    hasActiveQsAccess,
    hasQsApplicationData,
    isUserAccessRoute,
    isAuthorizationValid,
    downloadServiceAgreement,
    submitQsApplication
  }
}
