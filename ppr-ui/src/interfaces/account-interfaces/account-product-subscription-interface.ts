import { AccountProductCodes, AccountProductMemberships, AccountProductRoles } from '@/enums'

export interface AccountProductSubscriptionIF {
  [AccountProductCodes.RPPR]?: {
    membership: AccountProductMemberships
    roles: Array<AccountProductRoles>
  }
}