import { HomeCertificationOptions } from '@/enums'
import { MhRegistrationSummaryIF } from '@/interfaces'
import { MhrReRegistrationType } from '@/resources'
import { useStore } from '@/store/store'
import { fetchMhRegistration } from '@/utils'
import { useNewMhrRegistration } from './useNewMhrRegistration'
import { cloneDeep } from 'lodash'
import { useMhrInformation } from '../mhrInformation'

export const useMhrReRegistration = () => {
  const {
    setMhrBaseline,
    setRegistrationType
  } = useStore()

  const { setMhrNumber, setMhrStatusType } = useStore()
  const { parseMhrPermitData } = useMhrInformation()

  const initMhrReRegistration = async (mhrSummary: MhRegistrationSummaryIF): Promise<void> => {
    setMhrNumber(mhrSummary.mhrNumber)
    setRegistrationType(MhrReRegistrationType)
    setMhrStatusType(mhrSummary.statusType)

    const { data } = await fetchMhRegistration(mhrSummary.mhrNumber)

    // Handle 'certificationOption' or 'noCertification' value mapping (because it's not returned in response)
    const certificationOption =
      (data?.description?.csaNumber && HomeCertificationOptions.CSA) ||
      (data?.description?.engineerName && HomeCertificationOptions.ENGINEER_INSPECTION) ||
      null

    // remove props that should not be pre-populated into Re-Registration
    data.documentId = ''
    data.ownerGroups = []

    // parse Transport Permit data to correctly show Location of Home step
    parseMhrPermitData(data)

    // Preserve MHR snapshot
    await setMhrBaseline(
      cloneDeep({
        ...data,
        description: {
          ...data.description,
          certificationOption: certificationOption,
          hasNoCertification: certificationOption === null
        }
      })
    )
    await useNewMhrRegistration().initDraftOrCurrentMhr(data, false)
  }

  return {
    initMhrReRegistration
  }
}
