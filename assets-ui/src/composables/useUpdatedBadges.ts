import { ComputedRef, computed } from 'vue'
import { useMhrCorrections } from './mhrRegistration'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

export const useUpdatedBadges = () => {

  const { isMhrReRegistration } = storeToRefs(useStore())
  const { isMhrCorrection } = useMhrCorrections()

  const showUpdatedBadge: ComputedRef<boolean> = computed((): boolean =>
    isMhrCorrection.value || isMhrReRegistration.value)

  return {
    showUpdatedBadge
  }
}
