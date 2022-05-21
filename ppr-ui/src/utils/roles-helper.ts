export function getDescriptiveUserRole (authRoles: Array<string>): string {
  const accessRole = []

  if (authRoles.includes('ppr_staff')) return 'STAFF_PPR'
  if (authRoles.includes('mhr_staff')) return 'STAFF_MHR'
  if (authRoles.includes('staff') && authRoles.includes('helpdesk')) return 'STAFF_PPR'

  if (authRoles.includes('staff') || authRoles.includes('sbc') ||
    authRoles.includes('helpdesk')) accessRole.push('STAFF')
  else accessRole.push('CLIENT')

  if (authRoles.includes('ppr')) accessRole.push('PPR')
  if (authRoles.includes('mhr')) accessRole.push('MHR')
  return accessRole.join('_')
}
