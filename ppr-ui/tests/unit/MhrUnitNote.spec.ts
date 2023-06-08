import Vue from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import VueRouter from 'vue-router'
import { createLocalVue, shallowMount, Wrapper } from '@vue/test-utils'
import mockRouter from './MockRouter'

import { MhrUnitNote } from '@/views'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { UnitNoteAdd, UnitNoteReview } from '@/components/unitNotes'
import { getTestId } from './utils'
import { unitNotes } from '@/resources/mhr-transfers/unit-notes'

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
  return shallowMount((MhrUnitNote as any), {
    localVue,
    router,
    vuetify
  })
}

describe('Should render MHR Unit Note', () => {
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
    expect(unitNoteAdd.find('h1').text()).toContain(unitNotes[UNIT_NOTE_DOC_TYPE].header)
    expect(wrapper.findComponent(UnitNoteAdd).exists()).toBeTruthy()
    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()
  })
})
