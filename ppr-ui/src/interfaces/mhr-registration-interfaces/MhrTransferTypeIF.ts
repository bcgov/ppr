// Search type interface
import type { ApiTransferTypes, UITransferTypes } from '@/enums/transferTypes'

export interface TransferTypeSelectIF {
  divider: boolean
  disabled: boolean
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
