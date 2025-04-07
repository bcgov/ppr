import { QsAccessBtn } from '@/components/common'
import { useStore } from '@/store/store'
import { axe } from 'vitest-axe'
import { createComponent } from './utils'
import { ProductCode, ProductStatus, ProductType } from '@/enums'
import type { UserProductSubscriptionIF } from '@/interfaces'

const store = useStore()

const mockedProductSubscription: UserProductSubscriptionIF[] = [{
  premiumOnly: true,
  type: ProductType.INTERNAL,
  code: ProductCode.MANUFACTURER,
  url: '',
  hidden: false,
  needReview: false,
  description: '',
  subscriptionStatus: ProductStatus.ACTIVE
}]

describe('QsAccessBtn', () => {
  let wrapper

  afterEach(async () => {
    await store.setUserProductSubscriptions([])
  })

  it('should have no accessibility violations', async () => {
    await store.setUserProductSubscriptions(mockedProductSubscription)
    wrapper = await createComponent(QsAccessBtn)

    // Run the axe accessibility check on the component's HTML
    const results = await axe(wrapper.html())
    expect(results).toBeDefined();
    expect(results.violations).toBeDefined();
    expect(results.violations).toHaveLength(0);
  })

  it('renders Approved Qualified Supplier link when isRoleQualifiedSupplier is true', async () => {
    await store.setUserProductSubscriptions(mockedProductSubscription)
    wrapper = await createComponent(QsAccessBtn)
    expect(wrapper.find('.approved-qs-link').exists()).toBe(true)
    expect(wrapper.find('.request-qs-tooltip').exists()).toBe(false)
  })

  it('renders Request MHR Qualified Supplier Access link when isRoleQualifiedSupplier is false', async () => {
    wrapper = await createComponent(QsAccessBtn)
    // Product Subscriptions are not setup, therefore approved-qs-lik should not be shown
    expect(wrapper.find('.approved-qs-link').exists()).toBe(false)
    expect(wrapper.find('.request-qs-link').exists()).toBe(true)
  })
})
