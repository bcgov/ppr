// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { Wrapper } from '@vue/test-utils'
import {
  mockedPartyCodeSearchResponse,
  mockedSecuredParties1
} from './test-data'

// Components
import { SecuredPartyDialog } from '@/components/dialogs'
import { createComponent } from './utils'

Vue.use(Vuetify)

const props = {
  defaultDialog: true,
  defaultParty: mockedSecuredParties1[0],
  defaultResults: mockedPartyCodeSearchResponse
}

describe('Secured Party Dialog SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SecuredPartyDialog, props)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(SecuredPartyDialog).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find('#dialog-cancel-button').exists()).toBe(true)
    expect(wrapper.find('#create-new-party').text()).toContain('new Secured Party')
  })

  it('renders secured party search responses', async () => {
    expect(wrapper.findAll('.searchResponse').length).toBe(2)
    // get the first result name
    expect(wrapper.find('.searchResponse .businessName').text()).toBe(mockedPartyCodeSearchResponse[0].businessName)
  })

  it('displays the correct current secured party info', () => {
    expect(wrapper.find('.currentParty .businessName').text()).toBe(mockedSecuredParties1[0].businessName)
  })
})

describe('Registering Party Dialog SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SecuredPartyDialog, props)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(SecuredPartyDialog).exists()).toBe(true)
    wrapper.setProps({ isRegisteringParty: true })
    await nextTick()
    expect(wrapper.find('#create-new-party').text()).toContain('new Registering Party')
  })
})
