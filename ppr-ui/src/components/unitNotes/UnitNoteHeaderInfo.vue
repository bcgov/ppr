<template>
  <v-row no-gutters>
    <v-col cols="12" class="py-3">
      <h3> {{ noteHeader }} </h3>
    </v-col>
    <v-col>
      <span class="info-text fs-14">
        Registered on {{ pacificDate(note.createDateTime, true) }}
        <v-divider vertical />
        Document Registration Number {{ note.documentRegistrationNumber }}
      </span>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { defineComponent, reactive, computed, toRefs } from 'vue-demi'
import { MhUIStatusTypes, UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums'
import { UnitNotesInfo } from '@/resources'
import { UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'
import { pacificDate } from '@/utils'

export default defineComponent({
  name: 'UnitNoteHeaderInfo',
  props: {
    note: {
      type: Object as () => UnitNoteIF,
      required: true
    }
  },
  setup (props) {
    const localState = reactive({
      noteHeader: computed(() : string => {
        let header =
        [UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION, UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]
          .includes(props.note.documentType)
          ? UnitNotesInfo[props.note.documentType].panelHeader
          : UnitNotesInfo[props.note.documentType].header

        if (props.note.status === UnitNoteStatusTypes.EXPIRED) {
          header += ` - ${MhUIStatusTypes.EXPIRED}`
        }

        if (props.note.status === UnitNoteStatusTypes.CANCELLED) {
          header += ` - ${MhUIStatusTypes.CANCELLED}`
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
@import '@/assets/styles/theme.scss';
h3 {
  line-height: 1.5;
}
</style>
