<template>
  <div>
    <v-row no-gutters>
      <v-col
        cols="12"
        class="py-3"
      >
        <h3> {{ noteHeader }} </h3>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <span class="info-text fs-14">
          Registered on {{ pacificDate(note.createDateTime, true) }}
          <v-divider
            vertical
            class="vert-divider mx-3"
          />
          Document Registration Number {{ note.documentRegistrationNumber }}
        </span>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, computed, toRefs } from 'vue'
import { APIRegistrationTypes, MhUIStatusTypes, UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums'
import {
  UnitNotesInfo,
  cancelledWithRedemptionNote,
  cancelledWithStaffMhrCorrection,
  cancelledWithClientMhrCorrection,
  cancelledWithPublicAmendment
} from '@/resources'
import type { UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'
import { localTodayDate, pacificDate } from '@/utils'
import { useMhrUnitNote } from '@/composables'

export default defineComponent({
  name: 'UnitNoteHeaderInfo',
  props: {
    note: {
      type: Object as () => UnitNoteIF,
      required: true
    }
  },
  setup (props) {
    const {
      isExpiryDatePassed
    } = useMhrUnitNote()

    const localState = reactive({
      today: computed(() : string => localTodayDate()),
      noteHeader: computed(() : string => {
        let header =
        [UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION, UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]
          .includes(props.note.documentType)
          ? UnitNotesInfo[props.note.documentType]?.panelHeader
          : UnitNotesInfo[props.note.documentType]?.header

        if (isExpiryDatePassed(props.note, localState.today)) {
          header += ` (Expired)`
        } else if (props.note.status === UnitNoteStatusTypes.CANCELLED &&
          props.note.documentType === UnitNoteDocTypes.NOTICE_OF_TAX_SALE) {
            header += ` ${cancelledWithRedemptionNote}`
        } else if (props.note.status === UnitNoteStatusTypes.CANCELLED) {
          switch (props.note.cancelledDocumentType) {
            case APIRegistrationTypes.MHR_CORRECTION_STAFF:
              header += ` ${cancelledWithStaffMhrCorrection}`
              break
            case APIRegistrationTypes.MHR_CORRECTION_CLIENT:
              header += ` ${cancelledWithClientMhrCorrection}`
              break
            case APIRegistrationTypes.MHR_PUBLIC_AMENDMENT:
              header += ` ${cancelledWithPublicAmendment}`
              break
            default:
              header += ` (${MhUIStatusTypes.CANCELLED})`
              break
          }
        } else if (props.note.status === UnitNoteStatusTypes.EXPIRED) {
          header += ` (${MhUIStatusTypes.EXPIRED})`
        } else if (props.note.documentType === UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION) {
          header += ' (Continued)'
        } else if (props.note.documentType === UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION) {
          header += ' (Extended)'
        }
        return header
      })
    })

    return {
      pacificDate,
      UnitNoteDocTypes,
      UnitNotesInfo,
      UnitNoteStatusTypes,
      MhUIStatusTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
h3 {
  line-height: 1.5;
}
</style>
