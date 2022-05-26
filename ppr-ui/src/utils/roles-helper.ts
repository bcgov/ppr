export function getDescriptiveUserRole (authRoles: Array<string>): string {
  const accessRole = []

  if (authRoles.includes('staff') || authRoles.includes('sbc') ||
    authRoles.includes('helpdesk') || authRoles.includes('ppr_staff') ||
    authRoles.includes('mhr_staff')) accessRole.push('STAFF')
  else accessRole.push('CLIENT')

  if (authRoles.includes('ppr') || authRoles.includes('ppr_staff')) accessRole.push('PPR')
  if (authRoles.includes('mhr') || authRoles.includes('mhr_staff')) accessRole.push('MHR')
  return accessRole.join('_')
}
