import { ProductCode, ProductStatus } from "@/enums"
import { UserProductSubscriptionIF } from "@/interfaces"

type mockedProductSubscriptions = {
  ['ALL']?: UserProductSubscriptionIF[],
  ['MHR']?: UserProductSubscriptionIF,
  ['PPR']?: UserProductSubscriptionIF,
  ['BUSINESS']?: UserProductSubscriptionIF,
}

export const mockedProductSubscriptions: mockedProductSubscriptions = {
  'ALL': [
    {
      premiumOnly: false,
      type: null,
      url: '',
      code: ProductCode.MHR,
      hidden: false,
      needReview: false,
      description: '',
      subscriptionStatus: ProductStatus.ACTIVE
    },
    {
      premiumOnly: false,
      type: null,
      url: '',
      code: ProductCode.PPR,
      hidden: false,
      needReview: false,
      description: '',
      subscriptionStatus: ProductStatus.ACTIVE
    },
    {
      premiumOnly: false,
      type: null,
      url: '',
      code: ProductCode.VS,
      hidden: false,
      needReview: false,
      description: '',
      subscriptionStatus: ProductStatus.ACTIVE
    },
  ],
  'MHR': {
    premiumOnly: false,
    type: null,
    url: '',
    code: ProductCode.MHR,
    hidden: false,
    needReview: false,
    description: '',
    subscriptionStatus: ProductStatus.ACTIVE
  },
  'PPR': {
    premiumOnly: false,
    type: null,
    url: '',
    code: ProductCode.PPR,
    hidden: false,
    needReview: false,
    description: '',
    subscriptionStatus: ProductStatus.ACTIVE
  },
  'BUSINESS': {
    premiumOnly: false,
    type: null,
    url: '',
    code: ProductCode.BUSINESS,
    hidden: false,
    needReview: false,
    description: '',
    subscriptionStatus: ProductStatus.ACTIVE
  },
}
