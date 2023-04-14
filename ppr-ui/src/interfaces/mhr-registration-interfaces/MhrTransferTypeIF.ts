// Search type interface
import { ApiTransferTypes, UITransferTypes } from '@/enums/transferTypes'

export interface TransferTypeSelectIF {
  divider: boolean
  selectDisabled: boolean
  transferType: ApiTransferTypes
  textLabel: UITransferTypes
  group: number
  class?: string
  icon?: string
  color?: string
  tooltip?: {
    title: string
    bullets: Array<string>,
    note?: string
  }
}
