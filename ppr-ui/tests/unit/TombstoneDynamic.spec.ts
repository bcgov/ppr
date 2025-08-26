import { createComponent, getTestId, setupMockStaffUser, setupMockUser } from './utils'
import {
  mockedFinancingStatementComplete,
  mockedMhrInformation,
  mockedMhrInformationExempt,
  mockedSelectSecurityAgreement
} from './test-data'
import { useStore } from '@/store/store'
import type { FinancingStatementIF } from '@/interfaces'
import { MhApiStatusTypes, RouteNames } from '@/enums'
import { defaultFlagSet, pacificDate } from '@/utils'
import { nextTick } from 'vue'
import { expect } from 'vitest'
import { Tombstone, TombstoneDefault, TombstoneDynamic } from '@/components/tombstones'
import flushPromises from 'flush-promises'

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

  it('does not render correction btns for Mhr when staff and the FF is disabled', async () => {
    setupMockStaffUser()
    await nextTick()

    const correctionBtn = await wrapper.find('#registry-correction-btn')
    expect(correctionBtn.exists()).toBe(false)
  })

  it('does not render correction btns for Mhr when not staff and the FF is enabled', async () => {
    setupMockUser()
    await nextTick()

    const correctionBtn = await wrapper.find('#registry-correction-btn')
    expect(correctionBtn.exists()).toBe(false)
  })

  it('renders correction btns properly for Mhr when staff and the FF is enabled', async () => {
    setupMockStaffUser()
    await nextTick()

    const correctionBtn = await wrapper.find('#registry-correction-btn')
    expect(correctionBtn.exists()).toBe(true)
  })

  it('does not render correction and public amend buttons for Cancelled Mhr', async () => {
    await store.setMhrStatusType(MhApiStatusTypes.CANCELLED)
    await nextTick()

    expect(wrapper.find('#registry-correction-btn').exists()).toBe(false)
    expect(wrapper.find('#public-amend-btn').exists()).toBe(false)
    expect(wrapper.find(getTestId('mhr-reg-status')).text()).toContain('Cancelled')
  })
})
