import { RouteNames } from '@/enums'
import { Component } from 'vue'

export interface StepIF {
  id: string
  step: number
  icon: string
  text: string
  to: RouteNames
  component: Component
  valid: boolean
  disabled?: boolean
}
