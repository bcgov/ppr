import type { HomeSectionIF } from '@/interfaces'
import type { HomeCertificationOptions } from '@/enums'

export interface MhrRegistrationDescriptionIF {
  manufacturer: string,
  baseInformation: {
    year: number,
    circa: boolean,
    make: string,
    model: string
  },
  sectionCount: number,
  sections: Array<HomeSectionIF>,
  csaNumber: string,
  csaStandard: string,
  engineerName: string,
  engineerDate: string,
  certificationOption?: HomeCertificationOptions, // Optional because it's a local property. Not used for submission
  hasNoCertification?: boolean, // For staff registration use only. Not submitted with registration
  rebuiltRemarks: string,
  otherRemarks: string
}
