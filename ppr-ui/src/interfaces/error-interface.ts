// generic error interface
import { ErrorCodes, ErrorCategories } from '@/enums'
export interface ErrorIF {
  detail?: string,
  category?: ErrorCategories,
  message?: string,
  statusCode: number,
  type?: ErrorCodes
}
