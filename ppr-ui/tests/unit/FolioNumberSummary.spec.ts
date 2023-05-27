// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue } from '@vue/test-utils'

// Components
import { FolioNumberSummary } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

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
    await store.setFolioOrReferenceNumber('ABC123')
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the view with text box', () => {
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    expect(wrapper.find('#txt-folio').exists()).toBe(true)
  })

  it('renders the folio data from the store', async () => {
    expect(wrapper.vm.folioNumber).toEqual('ABC123')
    expect(wrapper.find('#txt-folio').element.value).toBe('ABC123')
  })

  it('is valid and emits the valid event', async () => {
    wrapper.find('#txt-folio').setValue('MY TEST')
    await nextTick()
    expect(wrapper.emitted().folioValid).toBeTruthy()
    expect(wrapper.vm.isValid).toBeTruthy()
  })

  it('sets the validity to false for > 50 characters', async () => {
    wrapper.find('#txt-folio').setValue(
      'MY TEST THAT IS VERY LONG IN FACT TOO LONG SKDJFA ASKDJFL ASDKFJL ASDKJFL ALKSJDFLKJ ALSDKFJ AKSDJF'
    )
    await nextTick()
    expect(wrapper.vm.isValid).toBeFalsy()
    expect(wrapper.emitted().folioValid).toBeTruthy()
  })
})
