<template>
  <v-expansion-panel
    class="unit-note-panel"
    v-model="isExpanded"
  >
    <v-expansion-panel-title
      disableIconRotate
      :disabled="disabled"
      class="mb-2"
    >
      <UnitNoteHeaderInfo :note="note" />
      <!-- Custom Panel Actions -->
      <template #actions>
        <span class="unit-note-header-action mt-n4 mr-n2">
          <v-btn
            class="unit-note-menu-btn px-0"
            variant="plain"
            color="primary"
            :disabled="disabled"
            :ripple="false"
          >
            <span class="pr-4">{{ isActive ? 'Hide Note' : 'View Note' }}</span>
            <v-divider
              v-if="noteOptions.length > 0"
              vertical
            />
          </v-btn>
          <v-menu
            location="bottom right"
            class="unit-note-menu"
          >
            <template #activator="{ props, isActive }">
              <v-btn
                v-if="noteOptions.length > 0"
                class="unit-note-menu-btn px-0"
                variant="plain"
                color="primary"
                :disabled="disabled"
                :ripple="false"
                v-bind="props"
                minWidth="10"
                width="45"
              >
                <v-icon
                  class="menu-drop-down-icon"
                  color="primary"
                >
                  {{ isActive ? 'mdi-menu-up' : 'mdi-menu-down' }}
                </v-icon>
              </v-btn>
            </template>

            <!-- Drop down list -->
            <v-list>

              <!-- Actions other than Cancel Note-->
              <v-list-item
                v-for="option in noteOptions"
                :key="UnitNotesInfo[option].header"
                :data-test-id="`unit-note-option-${option}`"
                @click="handleOptionSelection(option, note)"
              >
                <v-list-item-subtitle class="text-right">
                  <v-icon
                    color="primary"
                    size="1.125rem"
                  >{{ UnitNotesInfo[option].dropdownIcon }}</v-icon>
                  {{ UnitNotesInfo[option].dropdownText }}
                </v-list-item-subtitle>
              </v-list-item>

            </v-list>
          </v-menu>
        </span>
      </template>
    </v-expansion-panel-title>

    <v-expansion-panel-text class="mb-2">
      <v-divider class="ml-0 mt-n2 mb-4" />
      <!-- Primary Note Content-->
      <UnitNoteContentInfo :note="isCancelledTaxSaleNote(note) ? addRedemptionNoteInfo(note) : note" />
    </v-expansion-panel-text>
    <template
      v-for="(additionalNote, index) in note.additionalUnitNotes"
      :key="index"
    >
      <v-divider
        v-if="isActive"
        class="fullwidth-divider mt-9"
        thickness="5"
      />
      <!-- Additional Notes -->
      <v-expansion-panel-text>
        <UnitNoteHeaderInfo
          class="py-4"
          :note="additionalNote"
        />
        <v-divider class="ml-0 my-4" />
        <UnitNoteContentInfo :note="additionalNote" />
      </v-expansion-panel-text>
    </template>
  </v-expansion-panel>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { RouteNames, UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { UnitNotesInfo } from '@/resources'
import { UnitNoteIF, UnitNotePanelIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'
import UnitNoteHeaderInfo from './UnitNoteHeaderInfo.vue'
import UnitNoteContentInfo from './UnitNoteContentInfo.vue'
import { useMhrUnitNote, useMhrUnitNotePanel } from '@/composables'

export default defineComponent({
  name: 'UnitNotePanel',
  components: {
    UnitNoteHeaderInfo,
    UnitNoteContentInfo
  },
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
      type: Object as () => UnitNotePanelIF,
      required: true
    }
  },
  setup (props) {
    const router = useRouter()

    const {
      setMhrUnitNoteType,
      setMhrUnitNote
    } = useStore()

    const {
      getNoteOptions
    } = useMhrUnitNotePanel()
    
    const { initCancelUnitNote, prefillUnitNote, addRedemptionNoteInfo } = useMhrUnitNote()

    const noteOptions = getNoteOptions(props.note)

    const initUnitNote = (noteType: UnitNoteDocTypes): void => {
      setMhrUnitNoteType(noteType)
      router.push({ path: '/' + RouteNames.MHR_INFORMATION_NOTE })
    }

    const cancelUnitNote = (note: UnitNoteIF): void => {
      setMhrUnitNote(initCancelUnitNote(note))
      router.push({ path: '/' + RouteNames.MHR_INFORMATION_NOTE })
    }

    const handleOptionSelection = (option: UnitNoteDocTypes, note: UnitNoteIF): void => {
      switch (option) {
        case UnitNoteDocTypes.NOTE_CANCELLATION:
          cancelUnitNote(note)
          break
        case UnitNoteDocTypes.NOTICE_OF_REDEMPTION:
          setMhrUnitNote(prefillUnitNote(note, option))
          router.push({ path: '/' + RouteNames.MHR_INFORMATION_NOTE })
          break
        default:
          initUnitNote(option)
      }
    }

    const isCancelledTaxSaleNote = (note: UnitNoteIF): boolean => {
      return note.documentType === UnitNoteDocTypes.NOTICE_OF_TAX_SALE &&
        note.status === UnitNoteStatusTypes.CANCELLED
    }

    return {
      handleOptionSelection,
      isCancelledTaxSaleNote,
      addRedemptionNoteInfo,
      UnitNoteDocTypes,
      UnitNotesInfo,
      noteOptions
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
