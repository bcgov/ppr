import { BreadcrumbIF } from '@/interfaces'
import { RouteNames } from '@/enums'

// breadcrumb data in tombstone
export const tombstoneBreadcrumbDashboard: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: true,
    text: 'My Personal Property Registry',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbDischarge: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    text: 'Total Discharge',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbRenewal: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    text: 'Renewal',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbAmendment: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    text: 'Amendment',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbRegistration: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    text: 'New Registration',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbPprSearch: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    text: 'Search Results',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbMhrSearch: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    text: 'Selection List',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbSearchConfirm: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: false,
    to: { name: RouteNames.MHRSEARCH },
    text: 'Selection List'
  },
  {
    disabled: true,
    href: '',
    text: 'Selection Review',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbMhrInformation: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: true,
    text: 'MHR Number',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbMhrCorrection: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: false,
    text: 'MHR Number',
    to: { name: RouteNames.MHR_INFORMATION }
  },
  {
    disabled: true,
    text: 'Registry Correction - Staff Error or Omission',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbMhrReRegistration: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: false,
    text: 'MHR Number',
    to: { name: RouteNames.MHR_INFORMATION }
  },
  {
    disabled: true,
    text: 'Re-Register Manufactured Home',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbMhrUnitNote: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: false,
    to: { name: RouteNames.MHR_INFORMATION },
    text: 'MHR Number'
  },
  {
    disabled: true,
    text: '', // dynamic based on the Unit Note type,
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbQsApplication: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: true,
    text: 'Qualified Supplier Application',
    to: { name: '' }
  }
]

export const tombstoneBreadcrumbExemption: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: false,
    to: { name: RouteNames.MHR_INFORMATION },
    text: 'MHR Number'
  },
  {
    disabled: true,
    text: 'Residential Exemption',
    to: { name: '' }
  }
]
