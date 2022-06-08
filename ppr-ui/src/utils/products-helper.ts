import { ProductCode, ProductStatus } from '@/enums'
import { UserProductSubscriptionIF } from '@/interfaces'

/**
 * Util function to get user's role and subscribed products as one string.
 * Will be used to get respective content/titles for the users based on those values.
 *
 * @param authRoles - List of user's roles
 * @param subscribedProducts - List of products that user's subscribed to
 * @returns String to describe user's roles and products. e.g. STAFF_PPR
 */
export function getRoleProductCode (
  authRoles: Array<string>,
  subscribedProducts: Array<UserProductSubscriptionIF>): string {
  let role: string

  if (authRoles.includes('staff') || authRoles.includes('sbc') ||
    authRoles.includes('helpdesk') || authRoles.includes('ppr_staff') ||
    authRoles.includes('mhr_staff')) role = 'STAFF'
  else role = 'CLIENT'

  // Get active product codes (MHR/PPR) and sort them for consistency
  const productCodes = subscribedProducts
    .filter(product => product.subscriptionStatus === ProductStatus.ACTIVE)
    .filter(product => product.code === ProductCode.MHR || product.code === ProductCode.PPR)
    .map(product => product.code)
    .sort()

  return [role, ...productCodes].join('_')
}
