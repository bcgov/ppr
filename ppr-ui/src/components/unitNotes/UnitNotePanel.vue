<template>
  <v-expansion-panel class="unit-note-panel pb-4 px-1">
    <v-expansion-panel-header disable-icon-rotate :disabled="disabled">
      <UnitNoteHeaderInfo :note="note"/>
      <!-- Custom Panel Actions -->
      <template v-slot:actions>
        <span class="unit-note-header-action mt-n4">
          <v-menu offset-y left nudge-right="2" nudge-bottom="0" class="unit-note-menu">
            <template v-slot:activator="{ on, value }">
              <v-btn
                class="unit-note-menu-btn px-0"
                text
                color="primary"
                :disabled="disabled"
                :ripple="false"
              >
                <span class="px-4">{{ isActive ? 'Hide Note' : 'View Note' }}</span>
                <v-divider vertical class='mx-0' />
              </v-btn>
              <v-btn
                class="unit-note-menu-btn pa-0"
                text
                color="primary"
                :disabled="disabled"
                :ripple="false"
                v-on="on"
              >
                <v-icon class="menu-drop-down-icon" color="primary" :disabled="disabled">
                  {{ value ? 'mdi-menu-up' : 'mdi-menu-down' }}
                </v-icon>
              </v-btn>
            </template>

            <!-- Drop down list -->
            <v-list>

              <!-- Actions other than Cancel Note-->
              <v-list-item
                v-for="option in getNoteOptions(note)"
                :key="UnitNotesInfo[option].header"
                @click="initUnitNote(option)"
                data-test-id="unit-note-option"
              >
                <v-list-item-subtitle class="text-right">
                  <v-icon color="primary" size="1.125rem">mdi-plus</v-icon>
                  {{ UnitNotesInfo[option].dropdownText }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item
                class="cancel-unit-note-list-item"
                @click="cancelUnitNote(note)"
              >
                <v-list-item-subtitle class="text-right">
                  <v-icon color="primary" size="1.125rem">mdi-delete</v-icon>
                  Cancel Note
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>
        </span>
      </template>
    </v-expansion-panel-header>

    <v-expansion-panel-content>
      <v-divider class="ml-0 my-4"/>
      <!-- Primary Note Content-->
      <UnitNoteContentInfo :note="note"/>

      <!-- Additional Notes -->
      <div v-for="(additionalNote, index) in additionalNotes" :key="index">
          <v-divider class="fullwidth-divider mt-9"/>
          <UnitNoteHeaderInfo class="py-4" :note="additionalNote"/>
          <v-divider class="ml-0 my-4"/>
          <UnitNoteContentInfo :note="additionalNote"/>
      </div>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script lang="ts">
import { defineComponent } from 'vue-demi'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { useRouter } from 'vue2-helpers/vue-router'
import { useStore } from '@/store/store'
import { UnitNotesInfo, NoticeOfCautionDropDown } from '@/resources'
import { UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'
import { pacificDate } from '@/utils'
import UnitNoteHeaderInfo from './UnitNoteHeaderInfo.vue'
import UnitNoteContentInfo from './UnitNoteContentInfo.vue'
import { useMhrUnitNote } from '@/composables'

export default defineComponent({
  name: 'UnitNotePanel',
  props: {
    isActive: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    note: {
      type: Object as () => UnitNoteIF,
      required: true
    },
    additionalNotes: {
      type: Array as () => Array<UnitNoteIF>,
      default: () => []
    }
  },
  components: {
    UnitNoteHeaderInfo,
    UnitNoteContentInfo
  },
  setup () {
    const router = useRouter()

    const {
      setMhrUnitNoteType
    } = useStore()

    const {
      isNoticeOfCautionOrRelatedDocType
    } = useMhrUnitNote()

    const initUnitNote = (noteType: UnitNoteDocTypes): void => {
      setMhrUnitNoteType(noteType)
      router.push({ path: '/' + RouteNames.MHR_INFORMATION_NOTE })
    }

    const getNoteOptions = (unitNote: UnitNoteIF): Array<UnitNoteDocTypes> => {
      let options = []
      if (isNoticeOfCautionOrRelatedDocType(unitNote)) {
        options = [...NoticeOfCautionDropDown]
      }
      return options
    }

    const cancelUnitNote = (unitNote: UnitNoteIF): void => {
      // Request to delete unit note here
    }

    return {
      initUnitNote,
      cancelUnitNote,
      pacificDate,
      getNoteOptions,
      UnitNoteDocTypes,
      UnitNotesInfo
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
h3 {
  line-height: 1.5;
}
.unit-note-header-action {
  color: $primary-blue;
}
.unit-note-panel {
    border-bottom: 2px solid $gray1;
  }
.v-expansion-panel-header {
  padding-right: 6px;
}

::v-deep {
  .theme--light.v-btn.v-btn--disabled {
    color: $primary-blue!important;
  }
  .v-divider {
    color: $gray3;
  }

  .theme--light.v-data-table > .v-data-table__wrapper > table > thead > tr:last-child > th:first-child {
    padding-left: 0;
  }

  .fullwidth-divider {
    border:none;

    &:before {
    // full-width divider
    content: "";
    display: block;
    position: absolute;
    left: 0;
    max-width: 100%;
    width: 100%;
    border: solid $gray3;
    border-width: 2px 0 0 0;
  }
}

  tbody > tr > td {
    vertical-align: baseline;
    padding: 20px 12px 0 18px!important;
  }

  td:first-child {
    display: flex;
    align-items: flex-start;
    white-space: pre-line;
    overflow: visible;
  }
}
</style>
