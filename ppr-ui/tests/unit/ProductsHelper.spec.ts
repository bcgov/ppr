import { defaultFlagSet, getRoleProductCode } from '@/utils'
import { AuthRoles, ProductCode as Products } from '@/enums'

describe('Roles helper utility methods', () => {
  it('should properly construct descriptive role names from authRoles', () => {
    const CLIENT = [AuthRoles.PUBLIC]
    const STAFF = [AuthRoles.PPR_STAFF]
    const STAFF_MHR_PPR = [AuthRoles.PPR_STAFF, AuthRoles.MHR]

    // Staff with MHR enabled
    expect(getRoleProductCode(STAFF)).toBe('STAFF')
    expect(getRoleProductCode(STAFF_MHR_PPR)).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.PPR, AuthRoles.HELPDESK])).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.PPR, AuthRoles.MHR, AuthRoles.HELPDESK])).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.STAFF, AuthRoles.MHR])).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.STAFF, AuthRoles.PPR, AuthRoles.MHR])).toBe('STAFF')
    expect(getRoleProductCode([AuthRoles.STAFF, AuthRoles.PPR, AuthRoles.PPR_STAFF, AuthRoles.MHR])).toBe('STAFF')

    // Public Client with MHR enabled
    expect(getRoleProductCode(CLIENT, [Products.MHR])).toBe('CLIENT_MHR')
    expect(getRoleProductCode(CLIENT, [Products.PPR, Products.MHR])).toBe('CLIENT_MHR_PPR')
    expect(getRoleProductCode([AuthRoles.PUBLIC, AuthRoles.MHR], [Products.MHR])).toBe('CLIENT_MHR')
  })
})
