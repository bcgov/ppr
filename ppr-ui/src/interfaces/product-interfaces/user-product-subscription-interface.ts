import { ProductCode, ProductStatus, ProductType } from '@/enums'

export interface UserProductSubscriptionIF {
      "premiumOnly": boolean,
      "type": ProductType,
      "code": ProductCode,
      "url": string,
      "hidden": boolean,
      "needReview": boolean,
      "description": string,
      "subscriptionStatus": ProductStatus
}