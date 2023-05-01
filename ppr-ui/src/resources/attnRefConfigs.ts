import { AttnRefConfigIF } from '@/interfaces'

export const clientConfig: AttnRefConfigIF = {
  title: 'Folio or Reference Number',
  description: 'Add an optional number for this transaction for your own tracking purposes. This information is not' +
    ' used by the Manufactured Home Registry.',
  inputTitle: 'Folio Number',
  inputLabel: 'Folio or Reference Number (Optional)'
}

export const staffConfig: AttnRefConfigIF = {
  title: 'Attention',
  description: 'If the intended recipient of the registry documents is different from the Submitting Party' +
    ' name, add an optional name. If entered, it will appear on the cover letter.',
  inputLabel: 'Attention (Optional)'
}
