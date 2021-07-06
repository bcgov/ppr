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
      sortable: false,
      text: '',
      value: 'data-table-select',
      width: '11rem'
    },
    {
      text: 'Debtor Name',
      value: 'debtor.personName'
    },
    {
      text: 'Birthdate',
      value: 'debtor.birthDate'
    }
  ],
  [APISearchTypes.BUSINESS_DEBTOR]: [
    {
      sortable: false,
      text: '',
      value: 'data-table-select',
      width: '11rem'
    },
    {
      text: 'Debtor Name',
      value: 'debtor.businessName'
    }
  ],
  [APISearchTypes.MHR_NUMBER]: [
    {
      sortable: false,
      text: '',
      value: 'data-table-select',
      width: '11rem'
    },
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
      sortable: false,
      text: '',
      value: 'data-table-select',
      width: '11rem'
    },
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
    value: 'exactResultsSize'
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Results Selected',
    value: 'selectedResultsSize'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Download Report',
    value: 'pdf'
  }
]

export const vehicleTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-md',
    sortable: false,
    text: 'Vehicle Type',
    value: 'vehicle.type'
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Year',
    value: 'vehicle.year'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Make',
    value: 'vehicle.make'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Model',
    value: 'vehicle.model'
  },
  {
    class: 'column-lg',
    text: 'Serial/VIN/D.O.T. Number',
    value: 'vehicle.serial'
  },
  {
    class: 'column-mds pa-0',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const debtorTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-mds py-4',
    sortable: false,
    text: 'Name',
    value: 'party.name'
  },
  {
    class: 'column-mdl py-4',
    sortable: false,
    text: 'Address',
    value: 'party.address'
  },
  {
    class: 'column-mds py-4',
    sortable: false,
    text: 'Birthdate',
    value: 'party.birthdate'
  },

  {
    class: 'column-sm pa-0',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const partyTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-mds py-4',
    sortable: false,
    text: 'Name',
    value: 'name'
  },
  {
    class: 'column-md py-4',
    sortable: false,
    text: 'Address',
    value: 'address'
  },
  {
    class: 'column-md py-4',
    sortable: false,
    text: 'Email Address',
    value: 'emailAddress'
  },
  {
    class: 'column-mds py-4',
    sortable: false,
    text: 'Secured Party Code',
    value: 'code'
  },
  {
    class: 'column-sm pa-0',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const registeringTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-mds py-4',
    sortable: false,
    text: 'Name',
    value: 'name'
  },
  {
    class: 'column-md py-4',
    sortable: false,
    text: 'Address',
    value: 'address'
  },
  {
    class: 'column-md py-4',
    sortable: false,
    text: 'Email Address',
    value: 'emailAddress'
  },
  {
    class: 'column-mds py-4',
    sortable: false,
    text: 'Registering Party Code',
    value: 'code'
  }
]
