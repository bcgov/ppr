
import { getRoleProductCode } from '@/utils'
import { mockedProductSubscriptions as products } from './test-data'

describe('Roles helper utility methods', () => {
  it('should properly construct descriptive role names from authRoles', () => {

    expect(getRoleProductCode(['ppr_staff'], [products.PPR])).toBe('STAFF_PPR')

    expect(getRoleProductCode(['ppr', 'helpdesk'], [products.PPR])).toBe('STAFF_PPR')
    expect(getRoleProductCode(['ppr', 'mhr', 'helpdesk'], [products.PPR, products.MHR])).toBe('STAFF_MHR_PPR')

    expect(getRoleProductCode(['staff', 'ppr'], [products.PPR])).toBe('STAFF_PPR')
    expect(getRoleProductCode(['staff', 'mhr'], [products.MHR])).toBe('STAFF_MHR')
    expect(getRoleProductCode(['sbc', 'ppr', 'mhr'], [...products.ALL])).toBe('STAFF_MHR_PPR')

    expect(getRoleProductCode(['ppr'], [products.PPR])).toBe('CLIENT_PPR')
    expect(getRoleProductCode(['mhr'], [products.MHR])).toBe('CLIENT_MHR')
    expect(getRoleProductCode(['ppr', 'mhr'], [products.PPR, products.MHR])).toBe('CLIENT_MHR_PPR')

    expect(getRoleProductCode(['ppr_staff'], [products.PPR, products.BUSINESS])).toBe('STAFF_PPR')
    expect(getRoleProductCode(['mhr_staff'], [products.BUSINESS, products.MHR])).toBe('STAFF_MHR')
    expect(getRoleProductCode(['ppr_staff', 'mhr_staff'], [products.BUSINESS, products.MHR, products.PPR])).toBe('STAFF_MHR_PPR')
    expect(getRoleProductCode(['staff', 'ppr', 'ppr_staff', 'mhr', 'mhr_staff'], [...products.ALL])).toBe('STAFF_MHR_PPR')

    expect(getRoleProductCode(['ppr_staff', 'mhr'], [...products.ALL])).toBe('STAFF_MHR_PPR')
    expect(getRoleProductCode(['mhr_staff', 'ppr'], [...products.ALL])).toBe('STAFF_MHR_PPR')
    expect(getRoleProductCode(['staff', 'ppr', 'mhr'], [...products.ALL])).toBe('STAFF_MHR_PPR')
  })
})
