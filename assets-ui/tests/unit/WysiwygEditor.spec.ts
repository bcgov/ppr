import { nextTick } from 'vue'
import { WysiwygEditor } from '@/components/common'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'
import { vi } from 'vitest'

describe('WysiwygEditor', () => {
  let wrapper

  beforeEach(async () => {
    vi.unmock('@/components/common/WysiwygEditor.vue')
    await flushPromises()
    wrapper = await createComponent(WysiwygEditor, { editorContent: '<p>Test content</p>' })
    await nextTick()
  })

  it('renders the component correctly', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('sets the editor content correctly', () => {
    expect(wrapper.vm.wysiwygEditorContent).toBe('<p>Test content</p>')
  })

  it('emits the editor content when it updates', async () => {
    wrapper = await createComponent(WysiwygEditor, { editorContent: '<p>New content</p>' })

    await nextTick()

    expect(getLastEvent(wrapper, 'emitEditorContent')).toEqual('<p>New content</p>')
  })

  it('displays table input dialog on insertTable action', async () => {
    // Simulate clicking insertTable action
    await wrapper.vm.getToolAction({
      action: 'insertTable'
    })

    expect(wrapper.vm.displayTableInput).toBe(true)
  })

  it('handles dialog action correctly', async () => {
    // Simulate clicking insertTable action
    await wrapper.vm.getToolAction({
      action: 'insertTable'
    })

    wrapper.vm.insertTableRows = 2
    wrapper.vm.insertTableCols = 3

    // Simulate proceeding with the dialog action
    await wrapper.vm.handleDialogAction(true)

    expect(wrapper.vm.displayTableInput).toBe(false)
    // Add your assertions for the inserted table here
  })
})
