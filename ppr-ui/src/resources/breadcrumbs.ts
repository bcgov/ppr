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
    text: 'My PPR Dashboard'
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
    href: sessionStorage.getItem('BASE_URL') + '/dashboard',
    text: 'My PPR Dashboard'
  },
  {
    disabled: true,
    href: '',
    text: 'Search Results'
  }
]
