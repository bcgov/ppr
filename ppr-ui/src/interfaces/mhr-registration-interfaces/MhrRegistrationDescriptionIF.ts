import { HomeSectionIF } from '@/interfaces'
import { HomeCertificationOptions } from '@/enums'

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
  engineerReportDate: string,
  certificationOption?: HomeCertificationOptions, // Optional because it's a local property. Not used for submission
  rebuiltRemarks: string,
  otherRemarks: string
}
