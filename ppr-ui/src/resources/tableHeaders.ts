import { APISearchTypes } from '@/enums'
import { BaseHeaderIF, TableHeadersIF } from '@/interfaces'

export const searchTableHeaders: TableHeadersIF = {
  [APISearchTypes.SERIAL_NUMBER]: [
    {
      sortable: false,
      text: '',
      value: 'data-table-select',
      width: '11rem'
    },
    {
      text: 'Serial Number',
      value: 'vehicleCollateral.serialNumber'
    },
    {
      text: 'Type',
      value: 'vehicleCollateral.type'
    },
    {
      text: 'Year',
      value: 'vehicleCollateral.year'
    },
    {
      text: 'Make/Model',
      value: 'vehicleCollateral.make'
    }
  ],
  [APISearchTypes.INDIVIDUAL_DEBTOR]: [
    {
      text: 'Debtor Name',
      value: 'debtor.personalName'
    },
    {
      text: 'Birthdate',
      value: ''
    }
  ],
  [APISearchTypes.BUSINESS_DEBTOR]: [
    {
      text: 'Debtor Name',
      value: 'debtor.businessName'
    }
  ],
  [APISearchTypes.MHR_NUMBER]: [
    {
      text: 'Manufactured Home Registration Number',
      value: 'vehicleCollateral.manufacturedHomeRegistrationNumber'
    },
    {
      text: 'Serial Number',
      value: 'vehicleCollateral.serialNumber'
    },
    {
      text: 'Year',
      value: 'vehicleCollateral.year'
    },
    {
      text: 'Make/Model',
      value: 'vehicleCollateral.make'
    }
  ],
  [APISearchTypes.AIRCRAFT]: [
    {
      text: 'Serial Number',
      value: 'vehicleCollateral.serialNumber'
    },
    {
      text: 'Year',
      value: 'vehicleCollateral.year'
    },
    {
      text: 'Make/Model',
      value: 'vehicleCollateral.make'
    }
  ],
  [APISearchTypes.REGISTRATION_NUMBER]: [
    {
      text: 'Registration Number',
      value: 'registrationNumber'
    }
  ]
}

export const searchHistroyTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-md',
    sortable: false,
    text: 'Search Value',
    value: 'searchQuery.criteria.value'
  },
  {
    class: 'column-mdl',
    sortable: false,
    text: 'Type',
    value: 'UISearchType'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Folio',
    value: 'searchQuery.clientReferenceId'
  },
  {
    class: 'column-lg',
    text: 'Date/Time (Pacific time)',
    value: 'searchDateTime'
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Results Found',
    value: 'totalResultsSize'
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Exact Matches',
    value: ''
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Results Selected',
    value: ''
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Download Report',
    value: ''
  }
]
