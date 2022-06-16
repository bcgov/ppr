
import { defaultFlagSet, getRoleProductCode } from '@/utils'
import { AuthRoles, ProductCode as Products} from '@/enums'

describe('Roles helper utility methods', () => {
  it('should properly construct descriptive role names from authRoles', () => {

    const CLIENT = [AuthRoles.PUBLIC]
    const STAFF = [AuthRoles.PPR_STAFF]
    const STAFF_MHR_PPR = [AuthRoles.PPR_STAFF, AuthRoles.MHR]

    // Staff with MHR enabled
    defaultFlagSet['mhr-ui-enabled'] = true
    expect(getRoleProductCode(STAFF)).toBe('STAFF')
    expect(getRoleProductCode(STAFF_MHR_PPR)).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.PPR, AuthRoles.HELPDESK])).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.PPR, AuthRoles.MHR, AuthRoles.HELPDESK])).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.STAFF, AuthRoles.MHR])).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.STAFF, AuthRoles.PPR, AuthRoles.MHR])).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.STAFF, AuthRoles.PPR, AuthRoles.PPR_STAFF, AuthRoles.MHR])).toBe('STAFF')

    // Staff with MHR disabled
    defaultFlagSet['mhr-ui-enabled'] = false
    expect(getRoleProductCode(STAFF)).toBe('STAFF_PPR')
    expect(getRoleProductCode(STAFF_MHR_PPR)).toBe('STAFF_PPR')
    expect(getRoleProductCode([AuthRoles.SBC, AuthRoles.PPR, AuthRoles.MHR])).toBe('STAFF_PPR')

    // Public Client with MHR enabled
    defaultFlagSet['mhr-ui-enabled'] = true
    expect(getRoleProductCode(CLIENT, [Products.MHR])).toBe('CLIENT_MHR')
    expect(getRoleProductCode(CLIENT, [Products.PPR, Products.MHR])).toBe('CLIENT_MHR_PPR')
    expect(getRoleProductCode([AuthRoles.PUBLIC, AuthRoles.MHR], [Products.MHR])).toBe('CLIENT_MHR')

    // Public Client with MHR disabled
    defaultFlagSet['mhr-ui-enabled'] = false
    expect(getRoleProductCode(CLIENT, [Products.PPR])).toBe('CLIENT_PPR')
    expect(getRoleProductCode(CLIENT, [Products.PPR, Products.MHR])).toBe('CLIENT_PPR') // mhr disabled
  })
})
