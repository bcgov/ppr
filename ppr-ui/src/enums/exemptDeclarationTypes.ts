/** Enum describing the declaration types of a Non-Residential Exemption **/
export enum NonResOptions {
  DESTROYED = 'Destroyed',
  CONVERTED = 'Converted',
}

// Destroyed Types
export enum NonResDestroyedReasons {
  BURNT = 'Burnt',
  DISMANTLED = 'Dismantled',
  DILAPIDATED = 'Dilapidated',
  OTHER = 'Other'
}

// Converted Types
export enum NonResConvertedReasons {
  OFFICE = 'Office',
  STORAGE_SHED = 'Storage Shed',
  BUNKHOUSE = 'Bunkhouse',
  OTHER = 'Other'
}
