<template>
  <v-card flat id="unit-note-panels" class="mt-6">

    <!-- Unit note panels header -->
    <header id="unit-notes-header" class="default-header mt-10 rounded-top">
      <v-row no-gutters align="center">
        <v-col cols="9">
          <v-icon class="ml-2" color="darkBlue">mdi-message-reply-text</v-icon>
          <span class="font-weight-bold pl-2">Unit Notes</span>
        </v-col>

        <!-- Unit note header actions -->
        <v-col cols="3" class="text-right">
          <v-menu offset-y left nudge-bottom="0" class="add-unit-note-menu">
            <template v-slot:activator="{ on, value }">
              <v-btn
                id="open-unit-notes-btn"
                text v-on="on"
                color="primary"
                class="pa-3"
                :disabled="disabled"
                :ripple="false"
              >
                <v-icon>mdi-plus</v-icon>
                <span class="fs-14">Add Unit Notes</span>
                <v-icon color="primary">
                  {{ value ? 'mdi-menu-up' : 'mdi-menu-down' }}
                </v-icon>
              </v-btn>
            </template>

            <!-- Drop down list -->
            <v-list width="350" height="305">
              <v-list-item
                v-for="item in UnitNotesDropdown"
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
        multiple flat
        v-model="activePanels"
      >
        <UnitNotePanel
            v-for="(item, index) in panelUnitNotes"
            :disabled="disabled"
            :key="index"
            :note="item"
            :additionalNotes="item.additionalUnitNotes"
            :isActive="activePanels.includes(index)"
        />
      </v-expansion-panels>
      <v-col v-else class="empty-notes-msg text-center pt-8 pb-3">
        <p class="gray7 fs-14">A Unit Note has not been filed for this manufactured home.</p>
      </v-col>
    </v-row>

  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from 'vue-demi'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { useStore } from '@/store/store'
import { UnitNotesInfo, UnitNotesDropdown } from '@/resources'
import { UnitNoteIF } from '@/interfaces/unit-note-interfaces'
import UnitNotePanel from './UnitNotePanel.vue'
import { useMhrUnitNotePanel, useNavigation } from '@/composables'

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
    }
  },
  setup (props) {
    const { goToRoute } = useNavigation()

    const {
      setMhrUnitNoteType
    } = useStore()

    const {
      createPanelUnitNotes
    } = useMhrUnitNotePanel()

    const localState = reactive({
      activePanels: [],
      panelUnitNotes: createPanelUnitNotes(props.unitNotes)
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
#unit-notes-header.default-header {
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
::v-deep {
  .theme--light.v-btn.v-btn--disabled {
    color: $primary-blue!important;
  }
}
</style>
