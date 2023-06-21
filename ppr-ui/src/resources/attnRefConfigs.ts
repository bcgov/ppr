import { AttnRefConfigIF } from '@/interfaces'

export const folioOrRefConfig: AttnRefConfigIF = {
  title: 'Folio or Reference Number',
  description: 'Add an optional number for this transaction for your own tracking purposes. This information is not' +
    ' used by the Manufactured Home Registry.',
  inputTitle: 'Folio Number',
  inputLabel: 'Folio or Reference Number (Optional)'
}

export const attentionConfig: AttnRefConfigIF = {
  title: 'Attention',
  description: 'If the intended recipient of the registry documents is different from the Submitting Party' +
    ' name, add an optional name. If entered, it will appear on the cover letter.',
  inputTitle: 'Attention',
  inputLabel: 'Attention (Optional)'
}

export const attentionConfigManufactuer: AttnRefConfigIF = {
  ...attentionConfig,
  description: 'If the intended recipient of the registration verification statement and decal is' +
   ' different from the Submitting Party name, add an optional name.' +
   ' If entered, it will appear on the cover letter from BC Registries.'
}
