import type { SubProductConfigIF } from '@/interfaces'
import { SubProductSelector } from '@/components/common'
import { nextTick } from 'vue'
import { createComponent } from './utils'

describe('SubProductSelector', () => {
  it('renders the component', async () => {
    const wrapper = await createComponent(SubProductSelector, { subProductConfig: [] })
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

    const wrapper = await createComponent(SubProductSelector, { subProductConfig })

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

    const wrapper = await createComponent(SubProductSelector, { subProductConfig })

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

    const wrapper = await createComponent(SubProductSelector, { subProductConfig })

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

    const wrapper = await createComponent(SubProductSelector, {
      subProductConfig: subProductConfig,
      defaultProduct: 'subProduct1'
    })

    await nextTick()

    // Change the selectedProduct prop
    const radioButtons = wrapper.findAll('.sub-product-radio-btn')
    radioButtons.at(1).find('input').setValue(true)

    // Wait for the next tick to let Vue update the DOM
    await nextTick()

    // Check that the emitted event was triggered with the correct payload
    expect(wrapper.emitted('updateSubProduct')).toBeTruthy()
    expect(wrapper.emitted('updateSubProduct')[0]).toEqual(['subProduct2'])
  })
})
