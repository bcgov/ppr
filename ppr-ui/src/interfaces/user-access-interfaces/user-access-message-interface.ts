import type { ProductStatus } from '@/enums'

export interface UserAccessMessageIF {
  status: ProductStatus
  icon: string
  color: string
  msg: string
}
