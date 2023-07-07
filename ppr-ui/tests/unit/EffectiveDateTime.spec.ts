import Vue from 'vue'
import Vuetify from 'vuetify'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import { getTestId } from './utils'
import { EffectiveDateTime } from '@/components/unitNotes'
import { SharedDatePicker } from '@/components/common'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Any> object with the given parameters.
 */
function createComponent (propsData: any): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  return mount((EffectiveDateTime as any), {
    localVue,
    propsData,
    vuetify
  })
}

const props = {
  content: {
    title: 'Effective Date and Time',
    description: 'Select the effective date and time for',
    sideLabel: 'Effective Date and Time'
  },
  validate: false
}

describe('EffectiveDateTime', () => {
  it('should render the component', () => {
    const wrapper: Wrapper<any> = createComponent(props)

    const EffectiveDateTimeComponent = wrapper.findComponent(EffectiveDateTime)

    expect(EffectiveDateTimeComponent.exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.findComponent(SharedDatePicker).exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.find(getTestId('time-picker-fields')).exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.find(getTestId('footnote-label')).exists()).toBeFalsy()
  })
})
