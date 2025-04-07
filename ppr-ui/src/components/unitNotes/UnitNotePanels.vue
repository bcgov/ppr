<template>
  <v-card
    id="unit-note-panels"
    flat
    class="mt-6"
  >
    <!-- Unit note panels header -->
    <header
      id="unit-notes-header"
      class="review-header rounded-top"
    >
      <v-row
        no-gutters
        align="center"
      >
        <v-col
          cols="9"
          class="d-flex"
        >
          <v-icon
            class="ml-2"
            color="darkBlue"
          >
            mdi-message-reply-text
          </v-icon>
          <h3 class="fs-16 lh-24 ml-2">
            Unit Notes
          </h3>
        </v-col>

        <!-- Unit note header actions -->
        <v-col
          cols="3"
          class="text-right"
        >
          <v-menu
            location="bottom right"
            class="add-unit-note-menu"
          >
            <template #activator="{ props, isActive }">
              <v-btn
                id="open-unit-notes-btn"
                variant="plain"
                color="primary"
                :disabled="disabled"
                :ripple="false"
                v-bind="props"
              >
                <v-icon>mdi-plus</v-icon>
                <span class="fs-14 mx-1">Add Unit Notes</span>
                <v-icon color="primary">
                  {{ isActive ? 'mdi-menu-up' : 'mdi-menu-down' }}
                </v-icon>
              </v-btn>
            </template>

            <!-- Drop down list -->
            <v-list
              class="add-unit-note-item-list"
            >
              <v-list-item
                v-for="item in addUnitNoteDropdown"
                :key="item"
                class="unit-note-list-item"
                @click="initUnitNote(item)"
              >
                <v-list-item-subtitle class="pa-0">
                  {{ UnitNotesInfo[item].dropdownText }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-col>
      </v-row>
    </header>

    <!-- Unit notes expansion panels -->
    <v-row
      no-gutters
      justify="center"
      class="unit-note-panel-row"
    >
      <v-expansion-panels
        v-if="unitNotes.length"
        v-model="activePanels"
        multiple
      >
        <UnitNotePanel
          v-for="(item, index) in panelUnitNotes"
          :key="index"
          :disabled="disabled"
          :note="item"
          :additional-notes="item.additionalUnitNotes"
          :is-active="activePanels.includes(index)"
        />
      </v-expansion-panels>
      <v-col
        v-else
        class="empty-notes-msg text-center pt-8 pb-3"
      >
        <p class="gray7 fs-14">
          A Unit Note has not been filed for this manufactured home.
        </p>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import type { UnitNoteDocTypes } from '@/enums';
import { RouteNames } from '@/enums'
import { useStore } from '@/store/store'
import {
  UnitNotesInfo,
  UnitNotesDropdown,
  ResidentialExemptionStaffDropDown,
  ResidentialExemptionQSDropDown
}
  from '@/resources'
import type { UnitNoteIF } from '@/interfaces/unit-note-interfaces'
import UnitNotePanel from './UnitNotePanel.vue'
import { useMhrInformation, useMhrUnitNotePanel, useNavigation } from '@/composables'

export default defineComponent({
  name: 'UnitNotePanels',
  components: {
    UnitNotePanel
  },
  props: {
    unitNotes: {
      type: Array as () => Array<UnitNoteIF>,
      default: () => []
    },
    disabled: {
      type: Boolean,
      default: false
    },
    hasActiveExemption: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { goToRoute } = useNavigation()

    const {
      isRoleStaffReg,
      setMhrUnitNoteType
    } = useStore()

    const { createPanelUnitNotes } = useMhrUnitNotePanel()
    const { isCancelledMhr } = useMhrInformation()

    const localState = reactive({
      activePanels: [],
      panelUnitNotes: createPanelUnitNotes(props.unitNotes),
      addUnitNoteDropdown: computed((): UnitNoteDocTypes[] => {
        const dropdown = (isRoleStaffReg || isCancelledMhr.value)
          ? ResidentialExemptionStaffDropDown
          : ResidentialExemptionQSDropDown
        return (props.hasActiveExemption || isCancelledMhr.value) ? dropdown : UnitNotesDropdown
      })
    })

    const initUnitNote = (noteType: UnitNoteDocTypes): void => {
      setMhrUnitNoteType(noteType)
      goToRoute(RouteNames.MHR_INFORMATION_NOTE)
    }

    watch(() => localState.activePanels, () => {
      localState.activePanels.length > 1 && localState.activePanels.shift()
    })

    return {
      initUnitNote,
      UnitNotesInfo,
      UnitNotesDropdown,
      ResidentialExemptionStaffDropDown,
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

#unit-notes-header.review-header {
  padding: 10px;
  padding-left: 17px;
}

.unit-note-header-action {
  color: $primary-blue;

  .unit-note-menu-btn {
    padding-right: 10px;
  }
}

.unit-note-panel-row {
  background: $gray1;
  max-height: 750px;
  overflow-y: auto;
}

.unit-note-list-item {
  background-color: white;

  :hover {
    cursor: pointer;
  }
}

.empty-notes-msg {
  background: white;
}

:deep(.theme--light.v-btn.v-btn--disabled) {
  color: $primary-blue !important;
}
</style>
