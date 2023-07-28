import { Router, useRoute, useRouter } from 'vue2-helpers/vue-router'
import { computed, ComputedRef } from 'vue-demi'
import { getFeatureFlag } from '@/utils'
import { RouteNames } from '@/enums'
import { Route } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'

export const useUserAccess = () => {
  const route: Route = useRoute()
  const router: Router = useRouter()
  const {
    isRoleStaffReg
  } = storeToRefs(useStore())

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
    return [RouteNames.QS_ACCESS_TYPE, RouteNames.QS_ACCESS_INFORMATION, RouteNames.QS_ACCESS_REVIEW_CONFIRM]
      .includes(route.name as RouteNames)
  })

  /** Navigate to User Access Home route **/
  const goToUserAccess = (): void => {
    !isPendingQsAccess.value && !isUserAccessRoute.value && router.push({ name: RouteNames.QS_ACCESS_TYPE })
  }

  return {
    goToUserAccess,
    isQsAccessEnabled,
    isPendingQsAccess,
    isUserAccessRoute
  }
}
