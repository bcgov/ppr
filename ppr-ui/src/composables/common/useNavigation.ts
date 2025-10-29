import { useRoute, useRouter } from 'vue-router'
import { RouteNames } from '@/enums'
import { scrollToTop } from '@/utils'
import { useRuntimeConfig } from '#app'

export const useNavigation = () => {
  const route = useRoute()
  const router = useRouter()

  // Payment Urls
  const authWebPayUrl = `${useRuntimeConfig()?.public.VUE_APP_AUTH_WEB_URL}/makePayment`
  const homeRedirectUrl = sessionStorage.getItem('BASE_URL')
  /**
   * Simple Navigation helper
   * @routeName The specified route name to navigate too.
   * @query The navigation route options.
   */
  const goToRoute = async (routeName: RouteNames, query: {[key: string]: string|number} = null): Promise<void> => {
    await navigateTo({ name: routeName, query })
    scrollToTop()
  }

  /**
   * Navigates to the home Dashboard route.
   * @param anchorId Optional search ID to include as a route param.
   */
  const goToDash = async (anchorId?: string): Promise<void> => {
    const routeOptions: any = { name: RouteNames.DASHBOARD }
    if (anchorId) {
      routeOptions.params = { anchorId }
    }
    await router.push(routeOptions)
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
   * @param returnId - Optional return ID to append to the URL for redirection
   * @param anchorId - Optional anchor ID to append to the URL to anchor on the home page
   */
  const goToPay = (invoiceId: string, returnId: string = '', anchorId: string = ''): void => {
    if (invoiceId) {
      try {
        if (returnId) {
          const returnUrl = new URL(`/ppr/search/${returnId}`, homeRedirectUrl)
          window.location.href = `${authWebPayUrl}/${invoiceId}/${returnUrl}`
        } else if (anchorId) {
          const returnUrl = sessionStorage.getItem('BASE_URL') + `/dashboard/${anchorId}`
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
