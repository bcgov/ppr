import { AttnRefConfigIF } from '@/interfaces'

export const clientConfig: AttnRefConfigIF = {
  title: 'Attention or Reference Number',
  description: 'Add an optional Attention or Reference Number information for this transaction. If entered,' +
    ' it will appear on the Verification of Service document.',
  inputLabel: 'Attention or Reference Number (Optional)'
}

export const staffConfig: AttnRefConfigIF = {
  title: 'Attention',
  description: 'If the intended recipient of the registry documents is different from the Submitting Party' +
    ' name, add an optional name. If entered, it will appear on the cover letter.',
  inputLabel: 'Attention (Optional)'
}
