import type { RouteNames } from '@/enums'
import type { Component } from 'vue'

export interface StepIF {
  id: string
  step: number
  icon: string
  text: string
  to: RouteNames
  component: Component | string
  valid: boolean
  disabled?: boolean
}
