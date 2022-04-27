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
export const tombstoneBreadcrumbRenewal: Array<BreadcrumbIF> = [
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
    text: 'Renewal'
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
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Amendment'
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
export const tombstoneBreadcrumbSearchConfirm: Array<BreadcrumbIF> = [
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
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'mhr/search',
    text: 'Search Results'
  },
  {
    disabled: true,
    href: '',
    text: 'Search Results Review'
  }
]
