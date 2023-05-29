// Libraries
import { getRegisteringPartyFromAuth } from '@/utils'
import { PartyIF } from '@/interfaces'

// Components

// Other

describe('Auth API Helper Tests', () => {
  // Use mock service directly - account id is mock test id.
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  it('Get registering party from auth', async () => {
    const registeringParty:PartyIF = await getRegisteringPartyFromAuth()
    expect(registeringParty.businessName).toBeDefined()
    expect(registeringParty.address).toBeDefined()
    expect(registeringParty.address.street).toBeDefined()
    expect(registeringParty.address.city).toBeDefined()
    expect(registeringParty.address.region).toBeDefined()
    expect(registeringParty.address.postalCode).toBeDefined()
    expect(registeringParty.address.country).toBe('CA')
  })
})
