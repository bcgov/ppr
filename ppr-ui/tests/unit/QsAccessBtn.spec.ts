import { mount } from '@vue/test-utils'
import { QsAccessBtn } from '@/components/common'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'
const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Mock the useUserAccess composable to provide necessary values for testing
jest.mock('@/composables', () => ({
  useUserAccess: jest.fn(() => ({
    isPendingQsAccess: false,
    isUserAccessRoute: false,
    goToUserAccess: jest.fn()
  })),
  useMhrValidations: jest.fn(() => ({
    getStepValidation: jest.fn()
  }))
}))

describe('QsAccessBtn', () => {
  it('renders Approved Qualified Supplier link when isRoleQualifiedSupplier is true', () => {
    const wrapper = mount(QsAccessBtn, {
      data () {
        return {
          isRoleQualifiedSupplier: true
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
          isRoleQualifiedSupplier: false
        }
      },
      store,
      vuetify
    })

    expect(wrapper.find('.approved-qs-link').exists()).toBe(false)
    expect(wrapper.find('.request-qs-tooltip').exists()).toBe(true)
  })
})
