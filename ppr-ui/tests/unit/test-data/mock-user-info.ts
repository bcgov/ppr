import { UserInfoIF } from '@/interfaces'
import { mockedDefaultUserSettingsResponse } from './mock-user-profile-responses'

export const mockedUserInfo: UserInfoIF = {
  contacts: [
    {
      created: '',
      createdBy: '',
      email: '234',
      modified: '',
      phone: '555-444-3322',
      phoneExtension: '123'
    }
  ],
  feeSettings: {
    isNonBillable: false,
    serviceFee: 1.5
  },
  firstname: 'John',
  lastname: 'Smith',
  username: 'user123',
  settings: mockedDefaultUserSettingsResponse
}
