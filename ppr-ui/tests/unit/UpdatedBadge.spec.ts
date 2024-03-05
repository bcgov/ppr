import { UpdatedBadge } from '@/components/common'
import { createComponent } from './utils'

const mockBaseline = [
  {
    item1: 1,
    item2: 'A',
    item4: false,
    item3: { item1: 2, item2: 'TEST' },
    item5: { item1: 2, item2: 'TEST' },
    item6: [
      { item1: 2, item2: 'TEST' }
    ]
  }
]

const mockCurrentStateMatch = [
  {
    item1: 1,
    item2: 'A',
    item4: false,
    item5: { item1: 2, item2: 'TEST' },
    item3: { item1: 2, item2: 'test' },
    item6: [
      { item1: 2, item2: 'test' }
    ]
  }
]

const mockCurrentStateDeepMismatch = [
  {
    item1: 1,
    item2: 'A',
    item4: false,
    item3: { item1: 2, item2: 'TEST' },
    item5: { item1: 2, item2: 'test' },
    item6: [
      { item1: 12, item2: 'TEST' }
    ]
  }
]

const mockCurrentStateDeepMismatchAdditionalProperty= [
  {
    item1: 1,
    item2: 'A',
    item4: false,
    item3: { item1: 2, item2: 'TEST' },
    item5: { item1: 2, item2: 'test' },
    item6: [
      { item1: 2, item2: 'TEST', item7: 'another one' }
    ]
  }
]

const mockCurrentStateCaseSensitiveMismatch = [
  {
    item1: 1,
    item2: 'a',
    item4: false,
    item3: { item1: 2, item2: 'TEST' },
    item5: { item1: 2, item2: 'TEST' },
    item6: [
      { item1: 2, item2: 'TEST' }
    ]
  }
]

describe('UpdatedBadge', () => {
  let wrapper, badge

  it('wont render by default', async () => {
    wrapper = await createComponent(UpdatedBadge)
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(false)
  })

  it('renders with the CORRECTED label by default when there is a basic change', async () => {
    wrapper = await createComponent(UpdatedBadge, { baseline: 'test', currentState: 'testTest' })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('CORRECTED')
  })

  it('renders with a dynamic label by default when there is a basic change', async () => {
    wrapper = await createComponent(UpdatedBadge, { action: 'AMEND', baseline: 'test', currentState: 'testTest' })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('AMEND')
  })

  it('is not case sensitive on string comparisons', async () => {
    wrapper = await createComponent(UpdatedBadge, { baseline: 'test', currentState: 'TEST' })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(false)
  })

  it('handles boolean comparisons matches', async () => {
    wrapper = await createComponent(UpdatedBadge, {
      baseline: { v1: true }, currentState: { v1: true }
    })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(false)
  })

  it('handles boolean comparisons mismatches', async () => {
    wrapper = await createComponent(UpdatedBadge, {
      baseline: { v1: true }, currentState: { v1: false }
    })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('CORRECTED')
  })

  it('handles number comparisons matches', async () => {
    wrapper = await createComponent(UpdatedBadge, {
      baseline: { v1: 123 }, currentState: { v1: 123 }
    })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(false)
  })

  it('handles number comparisons mismatches', async () => {
    wrapper = await createComponent(UpdatedBadge, {
      baseline: { v1: 123 }, currentState: { v1: 1234 }
    })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('CORRECTED')
  })

  it('handles deep comparisons (nested objects and arrays) that match', async () => {
    wrapper = await createComponent(UpdatedBadge, { baseline: mockBaseline, currentState: mockCurrentStateMatch })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(false)
  })

  it('handles deep comparisons (nested objects and arrays) that mismatch', async () => {
    wrapper = await createComponent(UpdatedBadge, {
      baseline: mockBaseline, currentState: mockCurrentStateDeepMismatch
    })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('CORRECTED')
  })

  it('handles deep comparisons (nested objects and arrays) with additional properties', async () => {
    wrapper = await createComponent(UpdatedBadge, {
      baseline: mockBaseline, currentState: mockCurrentStateDeepMismatchAdditionalProperty
    })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('CORRECTED')
  })

  it('handles case sensitive comparison', async () => {
    wrapper = await createComponent(UpdatedBadge, {
      action: 'AMENDED', baseline: mockBaseline, currentState: mockCurrentStateCaseSensitiveMismatch, isCaseSensitive: true
    })
    badge = await wrapper.find('#updated-badge-component')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('AMENDED')
  })
})
