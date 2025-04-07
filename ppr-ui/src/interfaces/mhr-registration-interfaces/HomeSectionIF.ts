// New mhr registration Home Section interface.
import type { ActionTypes } from '@/enums'

export interface HomeSectionIF {
  id?: string, // optional property for editing specific sections
  serialNumber: string,
  lengthFeet: number,
  lengthInches: number,
  widthFeet: number,
  widthInches: number,
  action?: ActionTypes // for mhr corrections
}
