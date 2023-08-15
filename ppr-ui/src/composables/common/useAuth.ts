import { computed, ComputedRef } from 'vue-demi'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { AccountProductSubscriptionIF } from '@/interfaces'
import { AccountProductCodes, AccountProductMemberships, AccountProductRoles, ProductStatus } from '@/enums'
import { fetchAccountProducts, getProductSubscription } from '@/utils'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

export const useAuth = () => {
  const {
    setAccountProductSubscription,
    setUserProductSubscriptions,
    setUserProductSubscriptionsCodes
  } = useStore()
  const {
    getAccountId,
    isRoleStaff,
    isRoleStaffReg,
    isRoleStaffBcol
  } = storeToRefs(useStore())

  /** Helper to check if the current user is authenticated */
  const isAuthenticated: ComputedRef<boolean> = computed((): boolean => {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  })

  /** Get and set user products from Auth **/
  const initializeUserProducts = async (): Promise<void> => {
    const subscribedProducts = await fetchAccountProducts((getAccountId.value))
    if (subscribedProducts) {
      setUserProductSubscriptions(subscribedProducts)

      const activeProductCodes = subscribedProducts
        .filter(product => product.subscriptionStatus === ProductStatus.ACTIVE)
        .map(product => product.code)
      setUserProductSubscriptionsCodes(activeProductCodes)
    } else {
      throw new Error('Unable to get Products for the User')
    }
  }

  /** Gets product subscription authorizations and stores it. */
  const loadAccountProductSubscriptions = async (): Promise<void> => {
    let rpprSubscription = {} as AccountProductSubscriptionIF
    if (isRoleStaff.value) {
      rpprSubscription = {
        [AccountProductCodes.RPPR]: {
          membership: AccountProductMemberships.MEMBER,
          roles: [AccountProductRoles.PAY, AccountProductRoles.SEARCH]
        }
      }
      if (isRoleStaffBcol.value || isRoleStaffReg.value) {
        rpprSubscription.RPPR.roles.push(AccountProductRoles.EDIT)
      }
    } else rpprSubscription = await getProductSubscription(AccountProductCodes.RPPR)
    setAccountProductSubscription(rpprSubscription)
  }

  return {
    isAuthenticated,
    initializeUserProducts,
    loadAccountProductSubscriptions
  }
}
