// generic error interface
import { ErrorCodes } from '@/enums'
export interface ErrorIF {
  detail?: string,
  message?: string,
  statusCode: number,
  type?: ErrorCodes
}
