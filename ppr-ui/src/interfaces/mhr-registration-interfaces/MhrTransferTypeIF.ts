// Search type interface
import { HintIF } from '@/interfaces'
import { ApiTransferTypes, UiTransferTypes } from '@/enums/transferTypes'

export interface TransferTypeSelectIF {
  divider: boolean
  selectDisabled: boolean
  transferType: ApiTransferTypes
  textLabel: UiTransferTypes
  group: number
  class?: string
  icon?: string
  color?: string
  tooltip?: {
    title: string
    bullets: Array<string>
  }
}
