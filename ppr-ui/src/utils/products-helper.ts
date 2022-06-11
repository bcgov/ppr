import { ProductCode, AuthRoles } from '@/enums'
import { getFeatureFlag } from '@/utils'

/**
 * Util function to get user's role and subscribed products as one string.
 * Will be used to get respective content/titles for the users based on those values.
 *
 * @param authRoles - List of user's roles
 * @param subscribedProducts - Optional list of products that client is subscribed to
 * If no subscribed products passed, then it is a staff role
 * @returns String to describe user's roles and products. e.g. STAFF_PPR
 */
export function getRoleProductCode (
  authRoles: Array<AuthRoles>,
  subscribedProductCodes: Array<ProductCode> = []): string {
  const accessRole = []

  if (authRoles.includes(AuthRoles.STAFF) || authRoles.includes(AuthRoles.SBC) ||
    authRoles.includes(AuthRoles.HELPDESK) || authRoles.includes(AuthRoles.PPR_STAFF) ||
    subscribedProductCodes === []) {
    // Staff User
    accessRole.push('STAFF')
    // If MHR UI is disabled then user has access only to PPR
    if (!getFeatureFlag('mhr-ui-enabled')) {
      accessRole.push('PPR')
    }
  } else if (authRoles.includes(AuthRoles.PUBLIC)) {
    // Client User
    accessRole.push('CLIENT')

    if (subscribedProductCodes.includes(ProductCode.MHR) && getFeatureFlag('mhr-ui-enabled')) {
      accessRole.push('MHR')
    }

    if (subscribedProductCodes.includes(ProductCode.PPR)) {
      accessRole.push('PPR')
    }
  }
  return accessRole.join('_')
}
