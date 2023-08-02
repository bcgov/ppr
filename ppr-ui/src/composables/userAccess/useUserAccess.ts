import { computed, ComputedRef, Ref } from 'vue-demi'
import { getFeatureFlag } from '@/utils'
import { RouteNames } from '@/enums'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useNavigation } from '@/composables'

export const useUserAccess = () => {
  const { goToRoute, containsCurrentRoute } = useNavigation()
  const { setMhrQsInformation, setMhrSubProduct, setMhrQsValidation } = useStore()
  const { getMhrUserAccessValidation, isRoleStaffReg } = storeToRefs(useStore())

  /** Returns true when on the appropriate routes and the feature flag is enabled **/
  const isQsAccessEnabled: ComputedRef<boolean> = computed((): boolean => {
    return !isRoleStaffReg.value &&
      getFeatureFlag('mhr-user-access-enabled')
  })

  /** Returns true while staff review the application for the appropriate user access **/
  const isPendingQsAccess: ComputedRef<boolean> = computed((): boolean => {
    return false // Status to be retrieved from auth. *Pending Auth Api Work
  })

  /** Returns true while the User is within the User Access Routes **/
  const isUserAccessRoute: ComputedRef<boolean> = computed((): boolean => {
    return containsCurrentRoute(
      [RouteNames.QS_ACCESS_TYPE, RouteNames.QS_ACCESS_INFORMATION, RouteNames.QS_ACCESS_REVIEW_CONFIRM]
    )
  })

  /** Navigate to User Access Home route **/
  const goToUserAccess = async (): Promise<void> => {
    if (!isPendingQsAccess.value && !isUserAccessRoute.value) {
      initUserAccess()
      await goToRoute(RouteNames.QS_ACCESS_TYPE)
    }
  }

  /** Initialize user access properties to default state **/
  const initUserAccess = (): void => {
    setMhrSubProduct(null)
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

    // Reset Validations
    for (const flag in getMhrUserAccessValidation.value) {
      setMhrQsValidation({ key: flag, value: false })
    }
  }

  return {
    goToUserAccess,
    isQsAccessEnabled,
    isPendingQsAccess,
    isUserAccessRoute,
    initUserAccess
  }
}
