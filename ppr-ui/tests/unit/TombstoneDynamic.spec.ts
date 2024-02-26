import { createComponent } from './utils'
import {
  mockedFinancingStatementComplete,
  mockedMhrInformation,
  mockedMhrInformationExempt,
  mockedSelectSecurityAgreement
} from './test-data'
import { useStore } from '@/store/store'
import { FinancingStatementIF } from '@/interfaces'
import { TombstoneDynamic } from '@/components/tombstone'
import { RouteNames } from '@/enums'
import { pacificDate } from '@/utils'
import { nextTick } from 'vue'

const store = useStore()

// selectors
const tombstoneHeader: string = '.tombstone-header'
const tombstoneSubHeader: string = '.tombstone-sub-header'
const tombstoneInfo: string = '.tombstone-info'

describe('Tombstone component', () => {
  let wrapper

  const registration: FinancingStatementIF = {
    ...mockedFinancingStatementComplete
  }
  const registrationType = mockedSelectSecurityAgreement()

  beforeAll(async () => {
    // setup data
    await store.setRegistrationType(registrationType)
    await store.setRegistrationNumber(registration.baseRegistrationNumber)
    await store.setRegistrationCreationDate(registration.createDateTime)
    await store.setRegistrationExpiryDate(registration.expiryDate)
  })

  beforeEach(async () => {
    wrapper = await createComponent(TombstoneDynamic, null, RouteNames.REVIEW_DISCHARGE)
    await nextTick()
  })

  afterAll(async () => {
    await store.setRegistrationType(null)
    await store.setRegistrationNumber(null)
    await store.setRegistrationCreationDate(null)
    await store.setRegistrationExpiryDate(null)
  })

  it('renders Tombstone component properly for Total Discharge', async () => {
    await store.setMhrInformation(mockedMhrInformation)
    const tombstoneDynamic = wrapper.findComponent(TombstoneDynamic)
    expect(tombstoneDynamic.exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Base Registration Number ' + registration.baseRegistrationNumber)
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(registrationType.registrationTypeUI)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(2)
    expect(extraInfo.at(0).text()).toContain('Base Registration Date and Time: ')
    expect(extraInfo.at(0).text()).toContain(pacificDate(new Date(registration.createDateTime))?.trim())
    expect(extraInfo.at(1).text()).toContain('Current Expiry Date and Time: ')
    expect(extraInfo.at(1).text()).toContain(pacificDate(new Date(registration.expiryDate))?.trim())
  })

  it('renders Tombstone component properly for Renewal', async () => {
    wrapper = await createComponent(TombstoneDynamic, null, RouteNames.RENEW_REGISTRATION)
    await nextTick()

    expect(wrapper.findComponent(TombstoneDynamic).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Base Registration Number ' + registration.baseRegistrationNumber)
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(registrationType.registrationTypeUI)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(2)
    expect(extraInfo.at(0).text()).toContain('Base Registration Date and Time: ')
    expect(extraInfo.at(0).text()).toContain(pacificDate(new Date(registration.createDateTime))?.trim())
    expect(extraInfo.at(1).text()).toContain('Current Expiry Date and Time: ')
    expect(extraInfo.at(1).text()).toContain(pacificDate(new Date(registration.expiryDate))?.trim())
  })

  it('renders Tombstone component properly for Amendment', async () => {
    wrapper = await createComponent(TombstoneDynamic, null, RouteNames.AMEND_REGISTRATION)
    await nextTick()

    expect(wrapper.findComponent(TombstoneDynamic).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Base Registration Number ' + registration.baseRegistrationNumber)
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(registrationType.registrationTypeUI)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(2)
    expect(extraInfo.at(0).text()).toContain('Base Registration Date and Time: ')
    expect(extraInfo.at(0).text()).toContain(pacificDate(new Date(registration.createDateTime))?.trim())
    expect(extraInfo.at(1).text()).toContain('Current Expiry Date and Time: ')
    expect(extraInfo.at(1).text()).toContain(pacificDate(new Date(registration.expiryDate))?.trim())
  })
})

describe('TombstoneDynamic component - MHR', () => {
  let wrapper: any
  const mhrRegistrationInfo = mockedMhrInformation

  beforeEach(async () => {
    // setup data
    await store.setMhrInformation(mockedMhrInformation)
    wrapper = await createComponent(TombstoneDynamic, { isMhrInformation: true }, RouteNames.MHR_INFORMATION)
  })

  it('renders Tombstone component properly for Mhr', async () => {
    const tombstoneDynamic = wrapper.findComponent(TombstoneDynamic)
    tombstoneDynamic.vm.$props.isMhrInformation = true
    await nextTick()
    expect(wrapper.findComponent(TombstoneDynamic).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Manufactured Home Registration Number ' +
                                          mhrRegistrationInfo.mhrNumber)
    const extraInfo = await wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(1)
    expect(extraInfo.at(0).text()).toContain('Registration Status:')
    expect(extraInfo.at(0).text()).toContain('Active')
  })

  it('renders Tombstone component properly for Mhr Cancelled', async () => {
    await store.setMhrInformation({ ...mockedMhrInformation, statusType: 'CANCELLED' })
    const tombstoneDynamic = wrapper.findComponent(TombstoneDynamic)
    tombstoneDynamic.vm.$props.isMhrInformation = true
    await nextTick()
    expect(wrapper.findComponent(TombstoneDynamic).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Manufactured Home Registration Number ' +
                                          mhrRegistrationInfo.mhrNumber)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(1)
    expect(extraInfo.at(0).text()).toContain('Registration Status:')
    expect(extraInfo.at(0).text()).toContain('Cancelled')
  })

  it('should render Tombstone component for Exempt MHR (Residential Exemption unit note)', async () => {
    await store.setMhrInformation(mockedMhrInformationExempt)
    const tombstoneDynamic = await wrapper.findComponent(TombstoneDynamic)
    await nextTick()

    expect(tombstoneDynamic.find(tombstoneHeader).text())
      .toContain('Manufactured Home Registration Number ' + mockedMhrInformationExempt.mhrNumber)
    expect(tombstoneDynamic.find(tombstoneInfo).text()).toContain(mockedMhrInformationExempt.statusType)
  })
})
