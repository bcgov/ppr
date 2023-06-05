import { BaseHeaderIF } from '@/interfaces'

export const authorizedTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-md extra-indent py-4',
    sortable: false,
    text: 'Name',
    value: 'name'
  },
  {
    class: 'column-md pl-1 py-4',
    sortable: false,
    text: 'Account Name',
    value: 'legalName'
  },
  {
    class: 'column-md py-4',
    sortable: false,
    text: 'Address',
    value: 'address'
  },
  {
    class: 'column-mds py-4',
    sortable: false,
    text: 'Email Address',
    value: 'emailAddress'
  }
]
