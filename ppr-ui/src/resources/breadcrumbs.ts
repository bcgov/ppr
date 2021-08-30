import { BreadcrumbIF } from '@/interfaces'

// breadcrumb data in tombstone
export const tombstoneBreadcrumbDashboard: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: true,
    href: '',
    text: 'My Personal Property Registry'
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
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Total Discharge'
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
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'New Registration'
  }
]
export const tombstoneBreadcrumbSearch: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Search Results'
  }
]
