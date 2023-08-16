import { mount } from '@vue/test-utils'
import { QsAccessBtn } from '@/components/common'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'
const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

describe('QsAccessBtn', () => {
  it('renders Approved Qualified Supplier link when isRoleQualifiedSupplier is true', () => {
    const wrapper = mount(QsAccessBtn, {
      data () {
        return {
          hasActiveQsAccess: true
        }
      },
      store,
      vuetify
    })

    expect(wrapper.find('.approved-qs-link').exists()).toBe(true)
    expect(wrapper.find('.request-qs-tooltip').exists()).toBe(false)
  })

  it('renders Request MHR Qualified Supplier Access link when isRoleQualifiedSupplier is false', () => {
    const wrapper = mount(QsAccessBtn, {
      data () {
        return {
          hasActiveQsAccess: false
        }
      },
      store,
      vuetify
    })

    expect(wrapper.find('.approved-qs-link').exists()).toBe(false)
    expect(wrapper.find('.request-qs-tooltip').exists()).toBe(true)
  })
})
