import { Route } from 'vue-router'
import { Router, useRoute, useRouter } from 'vue2-helpers/vue-router'
import { RouteNames } from '@/enums'

export const useNavigation = () => {
  const route: Route = useRoute()
  const router: Router = useRouter()

  /**
   * Simple Navigation helper
   * @routeName The specified route name to navigate too.
   */
  const goToRoute = async (routeName: RouteNames): Promise<void> => {
    await router.push({ name: routeName })
  }

  /** Navigate to home Dashboard **/
  const goToDash = async (): Promise<void> => {
    await router.push({ name: RouteNames.DASHBOARD })
  }

  /** Helper to check is the current route matches */
  const isRouteName = (routeName: RouteNames): boolean => {
    return route.name === routeName
  }

  /** Helper to check if the specified routes contain the current route */
  const containsCurrentRoute = (routeNames: Array<RouteNames>): boolean => {
    return routeNames.includes(route.name as RouteNames)
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
    route,
    router,
    goToRoute,
    goToDash,
    navigateTo,
    isRouteName,
    containsCurrentRoute
  }
}
