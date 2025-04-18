// generic error interface
import type { ErrorCodes, ErrorCategories } from '@/enums'
export interface ErrorI {
  category: ErrorCategories,
  message: string,
  statusCode: number,
  type: ErrorCodes
}
