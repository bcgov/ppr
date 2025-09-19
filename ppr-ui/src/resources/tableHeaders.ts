import { APISearchTypes, FilterTypes } from '@/enums'
import type { BaseHeaderIF, TableHeadersIF } from '@/interfaces'

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
    },
    {
      text: 'Base Registration Number',
      value: 'baseRegistrationNumber'
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

export const searchHistoryTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-md',
    sortable: true,
    text: 'Search Value',
    value: 'searchQuery.criteria.value',
    filter: {
      text: 'Search Value',
      type: FilterTypes.TEXT_FIELD
    }
  },
  {
    class: 'column-md',
    sortable: true,
    text: 'Search Type or Category',
    value: 'searchQuery.type',
    filter: {
      text: 'Search Category',
      type: FilterTypes.SELECT
    }
  },
  {
    class: 'column-lg',
    sortable: true,
    text: 'Date/Time (Pacific time)',
    value: 'searchDateTime',
    filter: {
      text: 'Date',
      type: FilterTypes.DATE_PICKER
    }
  },
  {
    class: 'column-mds',
    sortable: true,
    text: 'Folio',
    value: 'searchQuery.clientReferenceId',
    filter: {
      text: 'Folio',
      type: FilterTypes.TEXT_FIELD
    }
  },
  {
    class: 'column-md text-center',
    sortable: false,
    text: 'Download Report',
    value: 'pdf'
  },
  {
    class: 'column-lg text-center matches',
    sortable: false,
    text: 'Matches',
    value: 'matches',
    subHeaders: ['Found', 'Exact', 'Selected']
  } 
]

export const searchHistoryTableHeadersStaff: Array<BaseHeaderIF> = [
  {
    class: 'column-md',
    sortable: true,
    text: 'Search Value',
    value: 'searchQuery.criteria.value',
    filter: {
      text: 'Search Value',
      type: FilterTypes.TEXT_FIELD
    }
  },
  {
    class: 'column-md',
    sortable: true,
    text: 'Search Type or Category',
    value: 'searchQuery.type',
    filter: {
      text: 'Search Category',
      type: FilterTypes.SELECT
    }
  },
  {
    class: 'column-mds',
    sortable: true,
    text: 'Folio Number',
    value: 'searchQuery.clientReferenceId',
    filter: {
      text: 'Folio Number',
      type: FilterTypes.TEXT_FIELD
    }
  },
  {
    class: 'column-lg',
    sortable: true,
    text: 'Date/Time (Pacific time)',
    value: 'searchDateTime',
    filter: {
      text: 'Date',
      type: FilterTypes.DATE_PICKER
    }
  },
  {
    class: 'column-mds',
    sortable: true,
    text: 'Username',
    value: 'username',
    filter: {
      text: 'Username',
      type: FilterTypes.TEXT_FIELD
    }
  },
  {
    class: 'column-md text-center',
    sortable: false,
    text: 'Download Report',
    value: 'pdf'
  },
  {
    class: 'column-lg text-center matches',
    sortable: false,
    text: 'Matches',
    value: 'matches',
    subHeaders: ['Found', 'Exact', 'Selected']
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
    class: 'column-sm',
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
    class: 'actions-col pa-0 actions-width',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const debtorTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'col-30 py-4',
    sortable: false,
    text: 'Name',
    value: 'party.name'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: 'Address',
    value: 'party.address'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: 'Birthdate',
    value: 'party.birthdate'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: '',
    value: ''
  }
]

export const partyTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'col-30 py-4',
    sortable: false,
    text: 'Name',
    value: 'name'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: 'Address',
    value: 'address'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: 'Email Address',
    value: 'emailAddress'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: 'Secured Party Code',
    value: 'code'
  }
]

export const registeringTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'col-30 py-4',
    sortable: false,
    text: 'Name',
    value: 'name'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: 'Address',
    value: 'address'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: 'Email Address',
    value: 'emailAddress'
  },
  {
    class: 'col-22-5 py-4',
    sortable: false,
    text: 'Registering Party Code',
    value: 'code'
  }
]

// used for secured parties/debtors in edit mode
export const editTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'actions-width pa-0',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const registrationTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Registration Number',
    value: 'registrationNumber',
    display: true
  },
  {
    class: 'column-lg',
    sortable: true,
    text: 'Registration Type',
    value: 'registrationType',
    display: true
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Verification Statement',
    value: 'vs',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Date (Pacific Time)',
    value: 'createDateTime',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Current Status',
    value: 'statusType',
    display: true
  },
  {
    class: 'column-lg',
    sortable: true,
    text: 'Registered By',
    value: 'registeringName',
    display: false
  },
  {
    class: 'column-lg',
    sortable: false,
    text: 'Registering Party',
    value: 'registeringParty',
    display: false
  },
  {
    class: 'column-lg',
    sortable: false,
    text: 'Secured Parties',
    value: 'securedParties',
    display: false
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Folio/Reference Number',
    value: 'clientReferenceId',
    display: false
  },

  {
    class: 'column-md',
    sortable: false,
    text: 'Days to Expiry (Pacific Time)',
    value: 'expireDays',
    display: true
  },
  {
    class: 'registration-action',
    sortable: false,
    text: 'Actions',
    value: 'actions',
    display: true
  }
]

export const mhRegistrationTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Registration Number',
    value: 'mhrNumber',
    display: true
  },
  {
    class: 'column-md',
    sortable: true,
    text: 'Current Status',
    value: 'statusType',
    display: true
  },
  {
    class: 'column-lg',
    sortable: true,
    text: 'Registration Type',
    value: 'registrationDescription',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Date (Pacific Time)',
    value: 'createDateTime',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Owners',
    value: 'ownerNames',
    display: true
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Verifications',
    value: 'vs',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Document ID',
    value: 'documentId',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Civic Address',
    value: 'civicAddress',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Manufacturer',
    value: 'manufacturerName',
    display: true
  },
  {
    class: 'column-md',
    sortable: true,
    text: 'Username',
    value: 'registeringName',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Submitting Party',
    value: 'registeringParty',
    display: true
  },
  {
    class: 'column-mdl',
    sortable: true,
    text: 'Folio/Reference Number',
    value: 'clientReferenceId',
    display: true
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Days to Expiry (Pacific Time)',
    value: 'expireDays',
    display: true
  },
  {
    class: 'registration-action',
    sortable: false,
    text: 'Actions',
    value: 'actions',
    display: true
  }
]

export const mhSearchNameHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-md',
    sortable: false,
    text: 'Owner Name',
    value: 'ownerName'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Owner Status',
    value: 'ownerStatus'
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Registration Number',
    value: 'mhrNumber'
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Current Registration Status',
    value: 'status'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Manufacturer',
    value: 'manufacturerName'
  },
  {
    class: 'column-xs',
    sortable: false,
    text: 'Year',
    value: 'year'
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Make/Model',
    value: 'makeModel'
  },
  {
    class: 'column-sm',
    text: 'Home Location',
    value: 'homeLocation'
  },
  {
    class: 'column-sm',
    text: 'Serial Number',
    value: 'serialNumber'
  },
  {
    class: 'lien-info',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const mhSearchSerialNumberHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-md',
    sortable: false,
    text: 'Serial Number',
    value: 'serialNumber'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Registration Number',
    value: 'mhrNumber'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Current Registration Status',
    value: 'status'
  },
  {
    class: 'column-md',
    text: 'Owner Name',
    value: 'ownerName'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Owner Status',
    value: 'ownerStatus'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Manufacturer',
    value: 'manufacturerName'
  },
  {
    class: 'column-xs',
    sortable: false,
    text: 'Year',
    value: 'year'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Make/Model',
    value: 'makeModel'
  },
  {
    class: 'column-mds',
    text: 'Home Location',
    value: 'homeLocation'
  },
  {
    class: 'lien-info',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const mhSearchMhrNumberHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-mdl',
    sortable: false,
    text: 'Registration Number',
    value: 'mhrNumber'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Current Registration Status',
    value: 'status'
  },
  {
    class: 'column-mds',
    text: 'Owner Name',
    value: 'ownerName'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Owner Status',
    value: 'ownerStatus'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Manufacturer',
    value: 'manufacturerName'
  },
  {
    class: 'column-xs',
    sortable: false,
    text: 'Year',
    value: 'year'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Make/Model',
    value: 'make'
  },
  {
    class: 'column-mds',
    text: 'Home Location',
    value: 'homeLocation'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Serial Number',
    value: 'serialNumber'
  },
  {
    class: 'lien-info',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const mhSearchNameHeadersReview: Array<BaseHeaderIF> = [
  {
    class: 'column-mdl',
    sortable: false,
    text: 'Owner Name',
    value: 'ownerName'
  },
  {
    class: 'column-sm',
    sortable: false,
    text: 'Registration Number',
    value: 'mhrNumber'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Year/Make/Model',
    value: 'yearMakeModel'
  },
  {
    class: 'column-sm',
    text: 'Home Location',
    value: 'homeLocation'
  },
  {
    class: 'column-sm',
    text: 'Serial Number',
    value: 'serialNumber'
  },
  {
    class: 'lien-info',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const mhSearchSerialNumberHeadersReview: Array<BaseHeaderIF> = [
  {
    class: 'column-md',
    text: 'Serial Number',
    value: 'serialNumber'
  },
  {
    class: 'column-mds',
    sortable: false,
    text: 'Registration Number',
    value: 'mhrNumber'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Owner Name',
    value: 'ownerName'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Year/Make/Model',
    value: 'yearMakeModel'
  },
  {
    class: 'column-mds',
    text: 'Home Location',
    value: 'homeLocation'
  },
  {
    class: 'lien-info',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const mhSearchMhrNumberHeadersReview: Array<BaseHeaderIF> = [
  {
    class: 'column-mdl',
    sortable: false,
    text: 'Registration Number',
    value: 'mhrNumber'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Owner Name',
    value: 'ownerName'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Year/Make/Model',
    value: 'yearMakeModel'
  },
  {
    class: 'column-mds',
    text: 'Home Location',
    value: 'homeLocation'
  },
  {
    class: 'column-mds',
    text: 'Serial Number',
    value: 'serialNumber'
  },
  {
    class: 'lien-info',
    sortable: false,
    text: '',
    value: 'edit'
  }
]

export const homeSectionsTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-lg',
    sortable: false,
    text: 'Section',
    value: 'section'
  },
  {
    class: 'column-mdl',
    sortable: false,
    text: 'Serial Number',
    value: 'serialNumber'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Length',
    value: 'length'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Width',
    value: 'width'
  },
  {
    class: 'actions',
    sortable: false,
    text: '',
    value: 'actions'
  }
]

export const homeSectionsReviewTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-mdl',
    sortable: false,
    text: 'Section',
    value: 'section'
  },
  {
    class: 'column-lg',
    sortable: false,
    text: 'Serial Number',
    value: 'serialNumber'
  },
  {
    class: 'column-lg',
    sortable: false,
    text: 'Length',
    value: 'length'
  },
  {
    class: 'column-lg',
    sortable: false,
    text: 'Width',
    value: 'width'
  }
]

export const homeOwnersTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-xl',
    sortable: false,
    text: 'Name',
    value: 'fullName'
  },
  {
    class: 'column-xl',
    sortable: false,
    text: 'Mailing Address',
    value: 'mailingAddress'
  },
  {
    class: 'column-md',
    sortable: false,
    text: 'Phone Number',
    value: 'phoneNumber',
    width: '10rem'
  },
  {
    class: 'actions column-md',
    sortable: false,
    value: 'actions'
  }
]

export const homeOwnersTableHeadersReview: Array<BaseHeaderIF> = [
  {
    class: 'column-width-xxl',
    sortable: false,
    text: 'Name',
    value: 'fullName'
  },
  {
    class: 'column-width-xxl',
    sortable: false,
    text: 'Mailing Address',
    value: 'mailingAddress'
  },
  {
    class: 'column-width-lg',
    sortable: false,
    text: 'Phone Number',
    value: 'phoneNumber'
  }
]

export const personGivingNoticeTableHeaders: Array<BaseHeaderIF> = [
  {
    class: 'column-lg',
    sortable: false,
    text: 'Name',
    value: 'fullName'
  },
  {
    class: 'column-mdxl',
    sortable: false,
    text: 'Mailing Address',
    value: 'mailingAddress'
  },
  {
    class: 'column-mdxl',
    sortable: false,
    text: 'Email Address',
    value: 'emailAddress'
  },
  {
    class: 'column-mdxl',
    sortable: false,
    text: 'Phone Number',
    value: 'phoneNumber'
  }
]
