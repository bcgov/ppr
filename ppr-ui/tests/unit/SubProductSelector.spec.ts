import { Wrapper, mount } from '@vue/test-utils'
import { SubProductConfigIF } from '@/interfaces'
import { SubProductSelector } from '@/components/common'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { nextTick } from 'vue-demi'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

describe('SubProductSelector', () => {
  it('renders the component', () => {
    const wrapper: Wrapper<any> = mount((SubProductSelector as any), {
      vuetify,
      propsData: {
        subProductConfig: []
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders the correct amount of sub-products', async () => {
    const subProductConfig: Array<SubProductConfigIF> = [
      {
        type: 'subProduct1',
        label: 'Sub Product 1',
        productBullets: ['Bullet 1', 'Bullet 2'],
        note: 'This is a note'
      },
      {
        type: 'subProduct2',
        label: 'Sub Product 2',
        productBullets: ['Bullet 1', 'Bullet 2'],
        note: ''
      }
    ]

    const wrapper: Wrapper<any> = mount((SubProductSelector as any), {
      vuetify,
      propsData: {
        subProductConfig
      }
    })

    const radioGroup = wrapper.find('.sub-product-radio-group')
    expect(radioGroup.exists()).toBe(true)

    const subProductRows = wrapper.findAll('.sub-product-radio-wrapper')
    expect(subProductRows.length).toBe(2)
  })

  it('renders sub-product bullets correctly', async () => {
    const subProductConfig: Array<SubProductConfigIF> = [
      {
        type: 'subProduct1',
        label: 'Sub Product 1',
        productBullets: ['Bullet 1', 'Bullet 2'],
        note: ''
      }
    ]

    const wrapper: Wrapper<any> = mount((SubProductSelector as any), {
      vuetify,
      propsData: {
        subProductConfig
      }
    })

    const bullets = wrapper.findAll('.bullet')
    expect(bullets.length).toBe(2)
    expect(bullets.at(0).text()).toBe('Bullet 1')
    expect(bullets.at(1).text()).toBe('Bullet 2')
  })

  it('renders sub-product note correctly', async () => {
    const subProductConfig: Array<SubProductConfigIF> = [
      {
        type: 'subProduct1',
        label: 'Sub Product 1',
        productBullets: [],
        note: '<strong>Note:</strong> This is a note'
      }
    ]

    const wrapper: Wrapper<any> = mount((SubProductSelector as any), {
      vuetify,
      propsData: {
        subProductConfig
      }
    })

    const note = wrapper.find('.sub-product-note')
    expect(note.exists()).toBe(true)
    expect(note.text()).toContain('Note:')
    expect(note.html()).toContain('<strong>Note:</strong> This is a note')
  })

  it('emits the selected-product-change event when selectedProduct changes', async () => {
    const subProductConfig: Array<SubProductConfigIF> = [
      {
        type: 'subProduct1',
        label: 'Sub Product 1',
        productBullets: ['Bullet 1', 'Bullet 2'],
        note: 'This is a note'
      },
      {
        type: 'subProduct2',
        label: 'Sub Product 2',
        productBullets: ['Bullet 1', 'Bullet 2'],
        note: ''
      }
    ]

    const wrapper: Wrapper<any> = mount((SubProductSelector as any), {
      vuetify,
      propsData: {
        subProductConfig,
        defaultProduct: 'subProduct1'
      }
    })
    await nextTick()

    // Change the selectedProduct prop
    const radioBtns = wrapper.findAll('.sub-product-radio-btn')
    radioBtns.at(1).trigger('click')

    // Wait for the next tick to let Vue update the DOM
    await nextTick()

    // Check that the emitted event was triggered with the correct payload
    expect(wrapper.emitted('updateSubProduct')).toBeTruthy()
    expect(wrapper.emitted('updateSubProduct')[0]).toEqual(['subProduct2'])
  })
})
