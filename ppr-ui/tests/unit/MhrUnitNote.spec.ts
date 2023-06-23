import Vue from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import VueRouter from 'vue-router'
import { createLocalVue, shallowMount, Wrapper } from '@vue/test-utils'
import mockRouter from './MockRouter'

import { MhrUnitNote } from '@/views'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { getTestId } from './utils'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { ContactInformation, DocumentId, Remarks } from '@/components/common'
import { UnitNoteAdd, UnitNoteReview } from '@/components/unitNotes'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({
    name: RouteNames.MHR_INFORMATION_NOTE
  })

  document.body.setAttribute('data-app', 'true')
  return shallowMount(MhrUnitNote as any, {
    localVue,
    router,
    vuetify
  })
}

describe('MHR Unit Note Filing', () => {
  let wrapper: Wrapper<any>

  const UNIT_NOTE_DOC_TYPE = UnitNoteDocTypes.NOTICE_OF_CAUTION

  beforeEach(async () => {
    await store.setMhrUnitNoteType(UNIT_NOTE_DOC_TYPE)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders MhrUnitNote component and related sub-components', async () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_INFORMATION_NOTE)
    expect(wrapper.exists()).toBeTruthy()

    const unitNoteAdd = wrapper.find(getTestId('unit-note-add'))
    expect(unitNoteAdd.find('h1').text()).toContain(UnitNotesInfo[UNIT_NOTE_DOC_TYPE].header)
    expect(wrapper.findComponent(UnitNoteAdd).exists()).toBeTruthy()
    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()
  })

  it('renders MhrUnitNote base component for filing the Unit Note', async () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_INFORMATION_NOTE)
    expect(wrapper.exists()).toBeTruthy()

    const AddUnitNoteContainer = wrapper.findComponent(UnitNoteAdd)
    expect(AddUnitNoteContainer.exists()).toBeTruthy()

    expect(AddUnitNoteContainer.findComponent(DocumentId)).toBeTruthy()
    expect(AddUnitNoteContainer.findComponent(Remarks)).toBeTruthy()
    expect(AddUnitNoteContainer.findComponent(ContactInformation)).toBeTruthy()

    expect(AddUnitNoteContainer.findAll('.border-error-left').length).toBe(0)
    expect(AddUnitNoteContainer.findAll('.error-text').length).toBe(0)
  })
})
