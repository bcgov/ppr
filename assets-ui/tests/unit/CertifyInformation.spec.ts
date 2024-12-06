import { useStore } from '@/store/store'
import { nextTick } from 'vue'
import { CertifyInformation } from '@/components/common'
import { CertifyIF } from '@/interfaces'
import { mockedAmendmentCertified, mockedAmendmentCertifiedInvalid, mockedRegisteringParty1 } from './test-data'
import { createComponent } from './utils'

const store = useStore()
const certifyInitial: CertifyIF = {
  valid: false,
  certified: false,
  legalName: '',
  registeringParty: mockedRegisteringParty1
}

describe('Certify Information on the confirmation page', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setCertifyInformation(mockedAmendmentCertified)
    wrapper = await createComponent(CertifyInformation, { setShowErrors: false })
    await nextTick()
  })

  it('renders the view with checkbox', () => {
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.find('#checkbox-certified').exists()).toBe(true)
  })

  it('renders the certify information valid data from the store', async () => {
    const certifyInfo: CertifyIF = wrapper.vm.certifyInformation
    expect(certifyInfo.legalName).toEqual(mockedAmendmentCertified.legalName)
    expect(certifyInfo.certified).toBeTruthy()
    expect(certifyInfo.registeringParty).toBeDefined()
    expect(certifyInfo.registeringParty.businessName).toBeDefined()
    expect(certifyInfo.registeringParty.address).toBeDefined()
    expect(certifyInfo.valid).toBeTruthy()
    expect(wrapper.vm.legalName).toEqual(mockedAmendmentCertified.legalName)
    expect(wrapper.vm.valid).toBeTruthy()
    expect(wrapper.vm.showErrors).toBeFalsy()
    expect(wrapper.vm.showErrorComponent).toBeFalsy()
    expect(wrapper.vm.registeringParty[0]).toBeDefined()
    expect(wrapper.vm.registeringParty[0].businessName).toBeDefined()
    expect(wrapper.vm.registeringParty[0].address).toBeDefined()
    expect(wrapper.vm.infoText.length).toBeGreaterThan(10)
  })

  it('renders the certify information invalid state data from the store', async () => {
    await store.setCertifyInformation(certifyInitial)
    wrapper = await createComponent(CertifyInformation, { setShowErrors: true })

    const certifyInfo: CertifyIF = wrapper.vm.certifyInformation
    expect(certifyInfo.legalName).toBeDefined()
    expect(certifyInfo.certified).toBeFalsy()
    expect(certifyInfo.valid).toBeFalsy()
    expect(wrapper.vm.legalName).toBeDefined()
    expect(wrapper.vm.certified).toBe(false)
    expect(wrapper.vm.valid).toBeFalsy()
    expect(wrapper.vm.showErrors).toBeTruthy()
    expect(wrapper.vm.showErrorComponent).toBeTruthy()
    expect(wrapper.vm.registeringParty).toBeDefined()
  })

  it('renders the certify information transition from initial to valid state', async () => {
    await store.setCertifyInformation(mockedAmendmentCertifiedInvalid)
    wrapper = await createComponent(CertifyInformation, { setShowErrors: true })
    await nextTick()

    // verify invalid states
    expect(wrapper.vm.valid).toBeFalsy()
    expect(wrapper.emitted().certifyValid).toBeFalsy()
    expect(wrapper.vm.showErrorComponent).toBeTruthy()

    const checkbox = await wrapper.find('#checkbox-certified')
    checkbox.setValue(true)
    await nextTick()

    // verify valid states
    expect(wrapper.vm.valid).toBeTruthy()
    expect(wrapper.emitted().certifyValid).toBeTruthy()
    expect(wrapper.vm.showErrorComponent).toBeFalsy()
  })
})

describe('Certify Information for staff', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setRoleSbc(true)
    await store.setCertifyInformation(mockedAmendmentCertified)
    wrapper = await createComponent(CertifyInformation, { setShowErrors: false })
  })

  it('renders the certify information for staff', async () => {
    const certifyInfo: CertifyIF = wrapper.vm.certifyInformation
    expect(certifyInfo.legalName).toEqual(mockedAmendmentCertified.legalName)
    expect(certifyInfo.certified).toBeTruthy()
    expect(certifyInfo.registeringParty).toBeDefined()
    expect(certifyInfo.registeringParty.businessName).toBe('SBC Staff')
    expect(certifyInfo.registeringParty.address).toBeFalsy()
    expect(wrapper.vm.legalName).toEqual(mockedAmendmentCertified.legalName)
  })
})
