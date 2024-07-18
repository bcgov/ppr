import { TransportPermitDetails } from '@/components/mhrTransportPermit'
import { createComponent } from './utils'
import { nextTick } from 'vue'
import { beforeEach } from 'vitest'
import { useStore } from '@/store/store'
import { MhApiStatusTypes } from '@/enums'
import flushPromises from 'flush-promises'

const store = useStore()

describe('Transport Permit Details', () => {
  let wrapper

  beforeEach(async () => {
    store.setMhrInformation({
      permitDateTime: '2024-02-05T08:40:53-08:00',
      permitExpiryDateTime: '2024-03-06T09:00:00-07:53',
      permitRegistrationNumber: '00502383',
      permitStatus: MhApiStatusTypes.ACTIVE
    })
    await flushPromises()

    wrapper = await createComponent(TransportPermitDetails)
    await nextTick()
  })

  it('renders the component', async () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the transport detail property labels', async () => {
    expect(wrapper.find('h4').text()).toContain('Transport Permit Details')

    const headerLabel = wrapper.findAll('.tp-header')
    expect(headerLabel.length).toBe(3)

    expect(headerLabel.at(0).text()).toContain('Transport Permit Number')
    expect(headerLabel.at(1).text()).toContain('Date and Time of Issue')
    expect(headerLabel.at(2).text()).toContain('Date of Expiry')
  })

  it('renders the transport detail property values', async () => {
    const headerLabel = wrapper.findAll('.tp-label')
    expect(headerLabel.length).toBe(3)

    expect(headerLabel.at(0).text()).toContain('00502383')
    expect(headerLabel.at(1).text()).toContain('February 5, 2024 at 8:40 am Pacific time')
    expect(headerLabel.at(2).text()).toContain('March 6, 2024')
  })
})
