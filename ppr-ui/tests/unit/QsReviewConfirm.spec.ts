import { QsReviewConfirm } from '@/views'
import { createComponent, setupMockUser } from './utils'
import { convertDate, defaultFlagSet } from '@/utils'
import { useStore } from '@/store/store'
import { MhrSubTypes } from '@/enums'
import flushPromises from 'flush-promises'
import { Authorization, ConfirmRequirements, ListRequirements } from '@/components/userAccess/ReviewConfirm'
import { mockedAccountInfo } from './test-data'

const store = useStore()

describe('QsReviewConfirm', () => {
  let wrapper
  const subProduct = MhrSubTypes.LAWYERS_NOTARIES

  const authorization = {
    isAuthorizationConfirmed: false,
    date: convertDate(new Date(), false, false),
    authorizationName: 'Test User'
  }
  beforeAll(async () => {
    defaultFlagSet['mhr-user-access-enabled'] = true
    await store.setMhrSubProduct(subProduct)
    await store.setMhrQsSubmittingParty(mockedAccountInfo)
    await store.setMhrQsIsRequirementsConfirmed(false)
    await store.setMhrQsAuthorization(authorization)
    await setupMockUser()
    await flushPromises()
  })

  afterAll(async () => {
    defaultFlagSet['mhr-user-access-enabled'] = false
    await flushPromises()
  })

  beforeEach(async () => {
    wrapper = await await createComponent(QsReviewConfirm)
    await flushPromises()
  })

  it('renders the component', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.findComponent(ConfirmRequirements).exists()).toBe(true)
    expect(wrapper.findComponent(Authorization).exists()).toBe(true)
  })

  it('renders the AccountInfo component with the correct props', () => {
    const accountInfoComponent = wrapper.findComponent({ name: 'AccountInfo' })
    expect(accountInfoComponent.exists()).toBe(true)

    // Verify that the props are passed correctly
    expect(accountInfoComponent.props('title')).toBe('Submitting Party for this Application')
    expect(accountInfoComponent.props('tooltipContent'))
      .toContain('The default Submitting Party is based on your BC Registries user account information.')
    expect(accountInfoComponent.props('accountInfo')).toStrictEqual(mockedAccountInfo)
  })

  it('Confirm requirements works as expected', async () => {
    const confirmRequirementsSection = wrapper.find('#qs-confirm-requirements')
    expect(confirmRequirementsSection.exists()).toBe(true)

    // heading
    const heading = confirmRequirementsSection.find('h2')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toBe(`Confirm`)

    // List items
    const requirements = wrapper.findComponent(ListRequirements)
    expect(requirements.exists()).toBe(true)
    expect(requirements.find('ol').exists()).toBe(true)
    expect(requirements.findAll('li').length).toBe(2)

    // Checkbox
    const confirmationCheckboxContainer = confirmRequirementsSection.find('.confirmation-checkbox')
    expect(confirmationCheckboxContainer.exists()).toBe(true)

    expect(store.getMhrQsIsRequirementsConfirmed).toBe(false)

    const checkboxText = confirmationCheckboxContainer.find('span')
    expect(checkboxText.exists()).toBe(true)
    expect(checkboxText.text()).toBe('I confirm and agree to all of the above requirements.')

    await confirmationCheckboxContainer.find('input').setValue(true)

    expect(store.getMhrQsIsRequirementsConfirmed).toBe(true)
  })

  it('confirm authorization works as expected', async () => {
    const authorizationSection = wrapper.find('#qs-authorization')
    expect(authorizationSection.exists()).toBe(true)

    const heading = authorizationSection.find('h2')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toBe('Authorization')

    expect(store.getMhrQsAuthorization.authorizationName).toBe('Test User')

    // setup
    const authorizationCheckbox = authorizationSection.find('#authorization-checkbox')
    const checkboxText = authorizationSection.find('.authorization-text')
    const authorizationTextField = authorizationSection.find('#authorization-text-field')
    const authorizationDate = authorizationSection.find('#authorization-date')
    expect(authorizationCheckbox.exists()).toBe(true)
    expect(authorizationTextField.exists()).toBe(true)
    expect(authorizationDate.exists()).toBe(true)
    expect(checkboxText.exists()).toBe(true)

    // Checks that text is updated and reflected in text next to checkbox
    expect(checkboxText.text().includes(store.getMhrQsAuthorization.authorizationName)).toBe(true)

    await authorizationTextField.setValue('Hello its me')

    expect(store.getMhrQsAuthorization.authorizationName).toBe('Hello its me')
    expect(checkboxText.text().includes(store.getMhrQsAuthorization.authorizationName)).toBe(true)

    await authorizationCheckbox.setValue(true)

    expect(store.getMhrQsAuthorization.isAuthorizationConfirmed).toBe(true)
  })
})
