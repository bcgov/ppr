import { useRoute, useRouter } from 'vue-router'
import { RouteNames } from '@/enums'
import { scrollToTop } from '@/utils'

export const useNavigation = () => {
  const route = useRoute()
  const router = useRouter()

  // Payment Urls
  const authWebPayUrl = `${useRuntimeConfig()?.public.VUE_APP_AUTH_WEB_URL}/makePayment`
  const homeRedirectUrl = sessionStorage.getItem('BASE_URL').replace(/\/dashboard$/, '')
  /**
   * Simple Navigation helper
   * @routeName The specified route name to navigate too.
   * @query The navigation route options.
   */
  const goToRoute = async (routeName: RouteNames, query: {[key: string]: string|number} = null): Promise<void> => {
    await navigateTo({ name: routeName, query })
    scrollToTop()
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
    return routeNames.includes(route?.name as RouteNames)
  }

  /**
   * Redirects to payment page for the specified invoice
   * @param invoiceId - The ID of the invoice to process payment for
   * @param returnId - Optional return ID to append to the URL
   */
  const goToPay = (invoiceId: string, returnId: string = ''): void => {
    if (invoiceId) {
      try {
        if (returnId) {
          const returnUrl = new URL(`/ppr/search/${returnId}`, homeRedirectUrl)
          window.location.href = `${authWebPayUrl}/${invoiceId}/${returnUrl}`
        } else window.location.href = `${authWebPayUrl}/${invoiceId}/${homeRedirectUrl}`

        return
      } catch (error) {
        console.error('Error redirecting to payment:', error)
      }
    } else {
      console.error('Payment ID not found')
    }
  }

  /**
   * Navigates to the specified URL, including Account ID param if available.
   * This function may or may not return. The caller should account for this!
   */
  const navigateToUrl = (url: string): boolean => {
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
    goToPay,
    navigateToUrl,
    isRouteName,
    containsCurrentRoute
  }
}
