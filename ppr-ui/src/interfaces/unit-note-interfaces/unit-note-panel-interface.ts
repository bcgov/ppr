import { UnitNoteIF } from './unit-note-interface'

export interface GroupedNotesIF {
  primaryUnitNote: UnitNoteIF,
  additionalUnitNotes?: Array<UnitNoteIF>
}
