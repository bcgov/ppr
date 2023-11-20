import { ErrorContact } from '@/components/common'
import { createComponent } from './utils'

describe('Error Contact component', () => {
  it('Displays expected content', async () => {
    const wrapper = await createComponent(ErrorContact)

    // verify content
    expect(wrapper.findComponent(ErrorContact).exists()).toBe(true)
    expect(wrapper.find('.contact-container').exists()).toBe(true)
    const contactItems = wrapper.findAll('.contact-item')
    expect(contactItems.length).toBe(3)
    expect(contactItems.at(0).find('.contact-key').text()).toContain('Canada')
    expect(contactItems.at(0).find('.contact-value').text()).toBe('1-877-526-1526')
    expect(contactItems.at(1).find('.contact-key').text()).toContain('Victoria')
    expect(contactItems.at(1).find('.contact-value').text()).toBe('250-387-7848')
    expect(contactItems.at(2).find('.contact-key').text()).toContain('Email')
    expect(contactItems.at(2).find('.contact-value').text()).toBe('BCRegistries@gov.bc.ca')
  })
})
