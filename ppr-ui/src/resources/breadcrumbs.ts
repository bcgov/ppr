import { BreadcrumbIF } from '@/interfaces'
import { RouteNames } from '@/enums'

// breadcrumb data in tombstone
export const tombstoneBreadcrumbDashboard: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: true,
    href: '',
    text: 'My Personal Property Registry',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbDischarge: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Total Discharge',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbRenewal: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Renewal',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbAmendment: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Amendment',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbRegistration: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'New Registration',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbSearch: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Selection List',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbSearchConfirm: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'mhr/search',
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
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: true,
    href: '',
    text: 'MHR Number',
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbMhrUnitNote: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + RouteNames.MHR_INFORMATION,
    to: { name: RouteNames.MHR_INFORMATION },
    text: 'MHR Number'
  },
  {
    href: '',
    disabled: true,
    text: '', // dynamic based on the Unit Note type,
    to: { name: '' }
  }
]
export const tombstoneBreadcrumbQsApplication: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: true,
    href: '',
    text: 'Qualified Supplier Application',
    to: { name: '' }
  }
]

export const tombstoneBreadcrumbExemption: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard',
    to: { name: '' }
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: true,
    href: '',
    text: 'Residential Exemption',
    to: { name: '' }
  }
]
