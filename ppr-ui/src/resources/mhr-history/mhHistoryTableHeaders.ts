import { BaseHeaderIF } from '@/interfaces'

export const homeDescriptionHeaders: Array<BaseHeaderIF> = [
  {
    name: '',
    value: '',
    class: 'column-width-md'
  },
  {
    name: 'Manufacturer\'s Name',
    value: 'manufacturer',
    class: 'col-22-5'
  },
  {
    name: 'Make/Model',
    value: ['baseInformation.make', 'baseInformation.model'],
    class: 'column-xs'
  },
  {
    name: 'Serial Number',
    value: 'sections[0].serialNumber',
    class: 'column-xs'
  },
  {
    name: 'Registration Date',
    value: 'createDateTime',
    class: 'column-xs'
  }
]

export const homeLocationHeaders: Array<BaseHeaderIF> = [
  {
    name: '',
    value: 'action',
    class: 'column-width-md'
  },
  {
    name: 'Town/City',
    value: 'townCity',
    class: 'col-22-5'
  },
  {
    name: 'Street',
    value: 'street',
    class: 'column-xs'
  },
  {
    name: 'From',
    value: 'from',
    class: 'column-xs'
  },
  {
    name: 'To',
    value: 'to',
    class: 'column-xs'
  }
]

export const homeOwnerHeaders: Array<BaseHeaderIF> = [
  {
    name: '',
    value: 'action',
    class: 'column-width-md'
  },
  {
    name: 'Owner Name',
    value: 'name',
    class: 'col-22-5'
  },
  {
    name: 'Tenancy Type',
    value: 'tenancyType',
    class: 'column-xs'
  },
  {
    name: 'Owner From',
    value: 'from',
    class: 'column-xs'
  },
  {
    name: 'Owner Until',
    value: 'to',
    class: 'column-xs'
  },
  {
    name: 'Owner Status',
    value: 'status',
    class: 'column-xs'
  }
]
