import { Route } from 'vue-router'
import { Router, useRoute, useRouter } from 'vue2-helpers/vue-router'
import { RouteNames } from '@/enums'

export const useNavigation = () => {
  const route: Route = useRoute()
  const router: Router = useRouter()

  /** Helper to check is the current route matches */
  const isRouteName = (routeName: RouteNames): boolean => {
    return route.name === routeName
  }

  /** Navigate to home Dashboard **/
  const goToDash = (): void => {
    router.push({
      name: RouteNames.DASHBOARD
    })
  }

  /**
   * Navigates to the specified URL, including Account ID param if available.
   * This function may or may not return. The caller should account for this!
   */
  const navigateTo = (url: string): boolean => {
    try {
      // get account id and set in params
      const accountId = sessionStorage.getItem('ACCOUNT_ID')
      if (accountId) {
        if (url.includes('?')) {
          url += `&accountid=${accountId}`
        } else {
          url += `?accountid=${accountId}`
        }
      }
      // assume URL is always reachable
      window.location.assign(url)

      return true
    } catch (error) {
      console.log('Error navigating =', error) // eslint-disable-line no-console

      return false
    }
  }

  return {
    goToDash,
    isRouteName,
    navigateTo
  }
}
