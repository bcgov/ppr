// generic error interface
import type { ErrorCodes, ErrorCategories } from '@/enums'
export interface ErrorIF {
  detail?: string,
  category?: ErrorCategories,
  message?: string,
  statusCode: number,
  type?: ErrorCodes
}

export interface ErrorDetailIF {
  error: ErrorIF;
}
