import { DialogOptionsIF } from '@/interfaces'

// search
export const paymentConfirmaionDialog: DialogOptionsIF = {
  acceptText: 'Accept',
  cancelText: 'Cancel',
  title: 'Payment Confirmation',
  text: 'Each search incurs a fee, even if the search returns no results. ' +
    'Your account will be debited $8.50 for this transaction.'
}

export const selectionConfirmaionDialog: DialogOptionsIF = {
  acceptText: 'Generate Report Now',
  cancelText: 'Change Selected Registrations',
  title: 'Confirm selections and generate report',
  text: 'registrations will be included in your PDF search results report ' +
    'along with an overview of the search results. Click the "Change ' +
    'Selected Registrations" button if you would like to edit your ' +
    'selection before returning to the dashboard.'
}

// registration
export const amendConfirmationDialog: DialogOptionsIF = {
  acceptText: 'Continue',
  cancelText: 'Cancel',
  title: 'Confirm registration to be amended',
  label: 'an Amendment',
  text: ''
}

export const dischargeConfirmationDialog: DialogOptionsIF = {
  acceptText: 'Continue',
  cancelText: 'Cancel',
  title: 'Confirm registration to be discharged',
  label: 'a Total Discharge',
  text: ''
}

export const renewConfirmationDialog: DialogOptionsIF = {
  acceptText: 'Continue',
  cancelText: 'Cancel',
  title: 'Confirm registration to be renewed',
  label: 'a Renewal',
  text: ''
}

// table deletion
export const tableDeleteDialog: DialogOptionsIF = {
  acceptText: 'Delete',
  cancelText: 'Cancel',
  title: 'Delete Draft',
  text: 'Are you sure you want to permanently delete this draft registration ' +
    'and remove it from your registrations table?'
}

export const tableRemoveDialog: DialogOptionsIF = {
  acceptText: 'Remove',
  cancelText: 'Cancel',
  title: 'Remove From Table',
  text: 'Are you sure you want to remove this registration from your registrations ' +
    'table? If you remove this registration from your table, you can add it back later ' +
    'by retrieving the registration using the base registration number.'
}

export const mhrTableRemoveDialog: DialogOptionsIF = {
  acceptText: 'Remove',
  cancelText: 'Cancel',
  title: 'Remove From Table',
  text: 'Are you sure you want to remove this registration from your registrations ' +
    'table? If you remove this registration from your table, you can add it back later ' +
    'by retrieving the registration using the MHR Number.'
}

export const mhrDeceasedOwnerChanges: DialogOptionsIF = {
  acceptText: 'Undo Changes and Delete Owner',
  cancelText: 'Cancel',
  title: 'Deceased owner\'s information cannot be changed',
  text: `The phone number and mailing address of a deceased owner cannot be changed prior to deletion.
    Deleting this owner will undo any changes you have made to their phone number or mailing address. `
}

export const confirmQsProductChangeDialog: DialogOptionsIF = {
  acceptText: 'Change Access Type',
  cancelText: 'Cancel',
  title: 'Change Access Type',
  text: `Changing the Access Type will delete any application information you have entered and return you to the
    original state. `
}

export const manufacturerRegSuccessDialogOptions: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Registration Successful',
  text: `This home is now included in the Manufactured Home Registry.<br><br>
    The verification statement and registration decals displaying the Manufactured Home Registration Number
    will be mailed to the Submitting Party.<br><br>
    <b>Note: The registration decals must be affixed to the home, according to the instructions on the
    decal envelope.</b>`
}

export const staleDraftDialogOptions = (draftIdentifier: string): DialogOptionsIF => {
  return {
    acceptText: 'Delete Draft',
    cancelText: '',
    title: 'Draft No Longer Valid',
    text: `Your draft for ${draftIdentifier} is no longer valid as changes have been made since your draft was
    created. Delete your draft and open the latest version of the manufactured home information to make changes.`
  }
}
