// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'

import { getVuexStore } from '@/store'
import { mount, createLocalVue } from '@vue/test-utils'

// Components
import { FolioNumberSummary } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Folio number on the summary page', () => {
  let wrapper: any

  beforeEach(async () => {
    // create a Local Vue and install router on it
    const localVue = createLocalVue()

    localVue.use(Vuetify)
    document.body.setAttribute('data-app', 'true')
    wrapper = mount((FolioNumberSummary as any), {
      localVue,
      propsData: {},
      store,
      vuetify
    })
    await store.dispatch('setFolioOrReferenceNumber', 'ABC123')
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the view with text box', () => {
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    expect(wrapper.find('#txt-folio').exists()).toBe(true)
  })

  it('renders the folio data from the store', async () => {
    expect(wrapper.vm.$data.folioNumber).toEqual('ABC123')
    expect(wrapper.find('#txt-folio').element.value).toBe('ABC123')
  })

  it('is valid and emits the valid event', async () => {
    wrapper.find('#txt-folio').setValue('MY TEST')
    expect(wrapper.emitted().folioValid).toBeTruthy()
    expect(wrapper.vm.$data.isValid).toBeTruthy()
  })

  it('sets the validity to false for > 50 characters', async () => {
    wrapper.find('#txt-folio').setValue(
      'MY TEST THAT IS VERY LONG IN FACT TOO LONG SKDJFA ASKDJFL ASDKFJL ASDKJFL ALKSJDFLKJ ALSDKFJ AKSDJF'
    )
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.$data.isValid).toBeFalsy()
    expect(wrapper.emitted().folioValid).toBeTruthy()
  })
})
