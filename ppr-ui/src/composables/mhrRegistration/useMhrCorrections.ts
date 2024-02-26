
export const useMhrCorrections = () => {
  {
    isRoleStaffReg
  } = storeToRefs(useStore())



/** Returns true when not staff, on the appropriate routes and the feature flag is enabled **/
  const isMhrChangesEnabled: ComputedRef<boolean> = computed((): boolean => {
    return !isRoleStaffReg.value && getFeatureFlag('mhr-user-access-enabled')
  })
}
