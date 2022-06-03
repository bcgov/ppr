import { RouteNames } from '@/enums'

export interface StepIF {
  id: string
  step: number
  icon: string
  text: string
  to: RouteNames
  component: string
  disabled?: boolean
}
