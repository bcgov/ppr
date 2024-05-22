import { nextTick } from 'vue'
import { Tombstone, TombstoneDefault, TombstoneDynamic } from '@/components/tombstone'
import { useStore } from '@/store/store'
import { AccountInformationIF, FinancingStatementIF, UserInfoIF } from '@/interfaces'
import { mockTransportPermitNewLocation, mockTransportPermitPreviousLocation, mockedFinancingStatementComplete, mockedSelectSecurityAgreement } from './test-data'
import { AuthRoles, MhApiStatusTypes, ProductCode, RouteNames } from '@/enums'
import { createComponent, getTestId } from './utils'
import { defaultFlagSet, pacificDate } from '@/utils'
import { useTransportPermits } from '@/composables'

const store = useStore()

// selectors
const tombstoneHeader: string = '.tombstone-header'
const tombstoneSubHeader: string = '.tombstone-sub-header'
const tombstoneInfo: string = '.tombstone-info'

describe('Tombstone component', () => {
  let wrapper: any
  const accountInfo: AccountInformationIF = {
    accountType: '',
    id: 1,
    label: 'testPPR',
    type: ''
  }
  const userInfo: UserInfoIF = {
    contacts: [
      {
        created: '',
        createdBy: '',
        email: '',
        modified: '',
        phone: '',
        phoneExtension: ''
      }
    ],
    feeSettings: {
      isNonBillable: false,
      serviceFee: 1.50
    },
    firstname: 'test',
    lastname: 'tester',
    username: '123d3crr3',
    settings: {
      defaultDropDowns: true,
      defaultTableFilters: true,
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  }
  const registration: FinancingStatementIF = {
    ...mockedFinancingStatementComplete
  }
  const registrationType = mockedSelectSecurityAgreement()

  beforeEach(async () => {
    // setup data used by header
    await store.setAccountInformation(accountInfo)
    await store.setUserInfo(userInfo)
    await store.setRegistrationType(registrationType)
    await store.setRegistrationNumber(registration.baseRegistrationNumber)
    await store.setRegistrationCreationDate(registration.createDateTime)
    await store.setRegistrationExpiryDate(registration.expiryDate)
    await store.setAuthRoles([AuthRoles.PUBLIC, 'ppr'])
    await store.setUserProductSubscriptionsCodes([ProductCode.PPR])
    await nextTick()
  })

  it('renders Tombstone component properly for Total Discharge', async () => {
    wrapper = await createComponent(Tombstone, null, RouteNames.REVIEW_DISCHARGE)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDynamic).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Base Registration Number ' + registration.baseRegistrationNumber)
    const subHeader = await wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(registrationType.registrationTypeUI)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(2)
    expect(extraInfo.at(0).text()).toContain('Base Registration Date and Time: ')
    expect(extraInfo.at(0).text()).toContain(pacificDate(new Date(registration.createDateTime))?.trim())
    expect(extraInfo.at(1).text()).toContain('Current Expiry Date and Time: ')
    expect(extraInfo.at(1).text()).toContain(pacificDate(new Date(registration.expiryDate))?.trim())
  })

  it('renders Tombstone component properly for Dashboard', async () => {
    wrapper = await createComponent(Tombstone, null, RouteNames.DASHBOARD)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)

    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = await wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component properly for Search', async () => {
    wrapper = await createComponent(Tombstone, null, RouteNames.SEARCH)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component properly for New Registration: length-trust', async () => {
    wrapper = await createComponent(Tombstone, null, RouteNames.LENGTH_TRUST)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component properly for New Registration: parties/debtors', async () => {
    wrapper = await createComponent(Tombstone, null, RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component properly for New Registration: collateral', async () => {
    wrapper = await createComponent(Tombstone, null, RouteNames.ADD_COLLATERAL)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component properly for New Registration: review/confirm', async () => {
    wrapper = await createComponent(Tombstone, null, RouteNames.REVIEW_CONFIRM)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component with Restored badge in Cancel Transport Permit flow', async () => {
    defaultFlagSet['mhr-cancel-transport-permit-enabled'] = true

    wrapper = await createComponent(Tombstone, { actionInProgress: true }, RouteNames.MHR_INFORMATION)
    wrapper.vm.dataLoaded = true

    // setup current location (outside of BC)
    const location = { ...mockTransportPermitNewLocation }
    await store.setMhrLocationAllFields(location)

    // setup current location (in BC)
    const previousLocation = { ...mockTransportPermitPreviousLocation }
    store.setMhrTransportPermitPreviousLocation(previousLocation)
    store.setTransportPermitChangeAllowed(true)
    useTransportPermits().setCancelLocationChange(true)
    store.setMhrStatusType(MhApiStatusTypes.EXEMPT)
    await nextTick()

    const tombstoneDynamic = wrapper.findComponent(TombstoneDynamic)

    expect(tombstoneDynamic.find(getTestId('restored-badge')).exists()).toBeTruthy()
    expect(tombstoneDynamic.text()).toContain('Active')
  })

})
