import { MHRSearchTypes, SearchTypes } from '@/resources'
import { APIMHRSearchTypes, APIMHRMapSearchTypes } from '@/enums'

export const useSearch = () => {
  const isMHRSearchType = (type: string): boolean => {
    const mhi = MHRSearchTypes.findIndex(mh => mh.searchTypeAPI === type)
    return mhi >= 0
  }
  const isPPRSearchType = (type: string): boolean => {
    const sti = SearchTypes.findIndex(st => st.searchTypeAPI === type)
    return sti >= 0
  }
  const mapMhrSearchType = (type: string, reverseMap: boolean = false): APIMHRSearchTypes|APIMHRMapSearchTypes => {
    if (reverseMap) {
      const index = Object.values(APIMHRSearchTypes).indexOf(type as APIMHRSearchTypes)
      return APIMHRMapSearchTypes[Object.keys(APIMHRMapSearchTypes)[index]]
    } else {
      const index = Object.values(APIMHRMapSearchTypes).indexOf(type as APIMHRMapSearchTypes)
      return APIMHRSearchTypes[Object.keys(APIMHRSearchTypes)[index]]
    }
  }

  return {
    isMHRSearchType,
    isPPRSearchType,
    mapMhrSearchType
  }
}
