import { HomeCertificationOptions } from '@/enums'
import { MhRegistrationSummaryIF } from '@/interfaces'
import { MhrReRegistrationType } from '@/resources'
import { useStore } from '@/store/store'
import { fetchMhRegistration, getMhrDraft } from '@/utils'
import { useNewMhrRegistration } from './useNewMhrRegistration'
import { cloneDeep } from 'lodash'
import { useMhrInformation } from '../mhrInformation'

export const useMhrReRegistration = () => {
  const { setMhrBaseline, setRegistrationType, setMhrDraftNumber } = useStore()

  const { setMhrNumber, setMhrStatusType } = useStore()
  const { parseMhrPermitData } = useMhrInformation()

  const initMhrReRegistration = async (mhrSummary: MhRegistrationSummaryIF): Promise<void> =>
    initReRegistrationOrDraft(mhrSummary)

  const initDraftMhrReRegistration = async (mhrSummary: MhRegistrationSummaryIF): Promise<void> =>
    initReRegistrationOrDraft(mhrSummary, true)

  /**
   * Private function to init the MHR Re-Registration or Draft Re-Registration.
   *
   * @param {MhRegistrationSummaryIF} mhrSummary - The MHR summary information.
   * @param {boolean} isDraft - A flag indicating whether the registration is a draft or not. Defaults to false.
   *
   */
  const initReRegistrationOrDraft = async (
    mhrSummary: MhRegistrationSummaryIF,
    isDraft: boolean = false
  ): Promise<void> => {
    setMhrNumber(mhrSummary.mhrNumber)
    setRegistrationType(MhrReRegistrationType)
    setMhrStatusType(mhrSummary.statusType)

    const { data } = await fetchMhRegistration(mhrSummary.mhrNumber)

    // Handle 'certificationOption' or 'noCertification' value mapping (because it's not returned in response)
    const certificationOption =
      (data?.description?.csaNumber && HomeCertificationOptions.CSA) ||
      (data?.description?.engineerName && HomeCertificationOptions.ENGINEER_INSPECTION) ||
      null

    if (!isDraft) {
      // remove props that should not be pre-populated into Re-Registration
      data.documentId = ''
      data.ownerGroups = []
      // parse Transport Permit data to correctly show Location of Home step
      parseMhrPermitData(data)
    } else {
      const draftNumber = mhrSummary.draftNumber
      const { registration } = await getMhrDraft(draftNumber)
      setMhrDraftNumber(draftNumber)
      setMhrStatusType(data?.status)
      await useNewMhrRegistration().initDraftOrCurrentMhr(registration)
    }

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

    if (!isDraft) {
      await useNewMhrRegistration().initDraftOrCurrentMhr(data, false)
    }
  }

  return {
    initMhrReRegistration,
    initDraftMhrReRegistration
  }
}
