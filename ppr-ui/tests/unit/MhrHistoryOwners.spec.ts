import { describe, it, expect, beforeEach } from 'vitest'
import { createComponent } from './utils'
import { MhrHistoryOwners } from '@/components/mhrHistory'
import { OwnerIF } from '@/interfaces'
import { nextTick } from 'vue'
import BaseAddress from '@/composables/address/BaseAddress.vue'

// Mock content data
const contentMock: OwnerIF = {
  type: 'Joint Tenants',
  groupId: 1,
  groupCount: 2,
  ownerId: 1,
  groupOwnerCount: 3,
  groupTenancyType: 'Joint',
  interest: 'Undivided',
  interestNumerator: 1,
  interestDenominator: 2,
  address: {
    street: '123 Main St',
    city: 'Vancouver',
    region: 'BC',
    country: 'CA',
    postalCode: 'V1A 1A1'
  },
  phoneNumber: '123-456-7890',
  phoneExtension: 123,
  emailAddress: 'test@example.com',
  createDateTime: '2022-01-01T14:30:45+00:00',
  registrationDescription: 'Test Registration',
  documentRegistrationNumber: '123456',
  documentId: '7890',
  endDateTime: '2023-01-01T14:30:45+00:00'
}

describe('MhrHistoryOwners.vue', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(MhrHistoryOwners, {
      content: contentMock
    })
    await nextTick()
  })

  it('renders the component', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('#mhr-history-owners').exists()).toBe(true)
  })

  it('displays tenancy type, group, owner, group tenancy type, and interest correctly', () => {
    expect(wrapper.text()).toContain('Tenancy Type:')
    expect(wrapper.text()).toContain(contentMock.type)
    expect(wrapper.text()).toContain('Group:')
    expect(wrapper.text()).toContain(`${contentMock.groupId} of ${contentMock.groupCount}`)
    expect(wrapper.text()).toContain('Owner:')
    expect(wrapper.text()).toContain(`${contentMock.ownerId} of ${contentMock.groupOwnerCount}`)
    expect(wrapper.text()).toContain('Group Tenancy Type:')
    expect(wrapper.text()).toContain(contentMock.groupTenancyType)
    expect(wrapper.text()).toContain('Interest:')
    expect(wrapper.text()).toContain(`${contentMock.interest} ${contentMock.interestNumerator}/${contentMock.interestDenominator}`)
  })

  it('displays mailing address correctly', () => {
    expect(wrapper.text()).toContain('Mailing Address')
    const baseAddress = wrapper.findComponent(BaseAddress)
    expect(baseAddress.text()).toContain(contentMock.address.street)
    expect(baseAddress.text()).toContain(contentMock.address.city)
    expect(baseAddress.text()).toContain(contentMock.address.region)
    expect(baseAddress.text()).toContain('Canada') // Formatted value
    expect(baseAddress.text()).toContain(contentMock.address.postalCode)
  })

  it('displays phone number and email address correctly', () => {
    expect(wrapper.text()).toContain('Phone Number')
    expect(wrapper.text()).toContain(contentMock.phoneNumber)
    expect(wrapper.text()).toContain(`Ext ${contentMock.phoneExtension}`)
    expect(wrapper.text()).toContain('Email Address')
    expect(wrapper.text()).toContain(contentMock.emailAddress)
  })

  it('displays owned from details correctly', () => {
    expect(wrapper.text()).toContain('Owned From')
    expect(wrapper.text()).toContain('January 1, 2022') // Adjust the date format to shortPacificDate
    expect(wrapper.text()).toContain('Document Type')
    expect(wrapper.text()).toContain(contentMock.registrationDescription)
    expect(wrapper.text()).toContain('Registration Number')
    expect(wrapper.text()).toContain(contentMock.documentRegistrationNumber)
    expect(wrapper.text()).toContain('Document ID')
    expect(wrapper.text()).toContain(contentMock.documentId)
  })

  it('displays owned until details correctly if endDateTime is present', () => {
    expect(wrapper.text()).toContain('Owned Until')
    expect(wrapper.text()).toContain('January 1, 2023') // Adjust the date format according to shortPacificDate
    expect(wrapper.text()).toContain('Document Type')
    expect(wrapper.text()).toContain(contentMock.registrationDescription)
    expect(wrapper.text()).toContain('Registration Number')
    expect(wrapper.text()).toContain(contentMock.documentRegistrationNumber)
    expect(wrapper.text()).toContain('Document ID')
    expect(wrapper.text()).toContain(contentMock.documentId)
  })

  it('displays "Current" for owned until if endDateTime is not present', async () => {
    wrapper = await createComponent(MhrHistoryOwners, {
      content: { ...contentMock, endDateTime: null }
    })
    await nextTick()
    await nextTick()
    expect(wrapper.text()).toContain('Owned Until')
    expect(wrapper.text()).toContain('Current')
  })

  it('displays email address as "(Not Entered)" if not present', async () => {
    wrapper = await createComponent(MhrHistoryOwners, {
      content: { ...contentMock, emailAddress: null }
    })
    expect(wrapper.text()).toContain('Email Address')
    expect(wrapper.text()).toContain('(Not Entered)')
  })
})
