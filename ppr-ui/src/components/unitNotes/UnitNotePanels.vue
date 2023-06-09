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
        <v-col cols="3" class="text-right pr-6">
          <v-menu offset-y left nudge-bottom="0" class="add-unit-note-menu">
            <template v-slot:activator="{ on, value }">
              <v-btn
                id="open-unit-notes-btn"
                text v-on="on"
                color="primary"
                class="pa-0"
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
            <v-list width="350" height="325">
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
      :class="{'cap-panels-height': unitNotes.length > 5}"
    >
      <v-expansion-panels
        v-if="unitNotes.length"
        multiple flat
        v-model="activePanels"
      >
        <v-expansion-panel
          v-for="(item, index) in unitNotes"
          :key="index"
          class="unit-note-panel pb-4 px-1"
        >
          <v-expansion-panel-header disable-icon-rotate :disabled="disabled">
            <v-row no-gutters>
              <v-col cols="12">
                <h3 class="py-3">
                  {{ UnitNotesInfo[item.documentType].header }}
                  {{ item.status === MhApiStatusTypes.EXPIRED ? ` - ${MhUIStatusTypes.EXPIRED}` : '' }}
                  {{ item.status === MhApiStatusTypes.CANCELLED ? ` - ${MhUIStatusTypes.CANCELLED}` : '' }}
                </h3>
              </v-col>
              <v-col>
                <span class="info-text">
                  Registered on {{ pacificDate(item.createDateTime) }}
                  <v-divider vertical />
                  Document Registration Number {{ item.documentRegistrationNumber }}
                </span>
              </v-col>
            </v-row>

            <!-- Custom Panel Actions -->
            <template v-slot:actions>
              <span class="unit-note-header-action mt-n4">
                <v-menu offset-y left nudge-bottom="0" class="unit-note-menu">
                  <template v-slot:activator="{ on, value }">
                    <v-btn
                      class="unit-note-menu-btn"
                      text
                      color="primary"
                      :disabled="disabled"
                      :ripple="false"
                    >
                      <span>{{ activePanels.includes(index) ? 'Hide Note' : 'View Note' }}</span>
                      <v-divider vertical />
                      <v-icon class="menu-drop-down-icon" color="primary" v-on="on" :disabled="disabled">
                        {{ value ? 'mdi-menu-up' : 'mdi-menu-down' }}
                      </v-icon>
                    </v-btn>
                  </template>

                  <!-- Drop down list -->
                  <v-list>
                    <v-list-item
                      class="cancel-unit-note-list-item"
                      @click="cancelUnitNote(item)"
                    >
                      <v-list-item-subtitle class="text-center">
                        <v-icon color="primary">mdi-delete</v-icon>
                        Cancel
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </span>
            </template>
          </v-expansion-panel-header>

          <v-expansion-panel-content>
            <v-divider class="ml-0 my-4"/>

            <!-- Note information -->
            <v-row v-if="item.effectiveDateTime" no-gutters class="pt-3">
              <v-col cols="3">
                <h3 class="effective-date">Effective Date and Time</h3>
              </v-col>
              <v-col cols="9">
                <span class="info-text fs-14">
                  {{ pacificDate(item.effectiveDateTime) }}
                </span>
              </v-col>
            </v-row>

            <v-row v-if="item.expiryDateTime" no-gutters class="pt-3">
              <v-col cols="3">
                <h3>Expiry Date and Time</h3>
              </v-col>
              <v-col cols="9">
                <span class="info-text fs-14">
                  {{ pacificDate(item.expiryDateTime) }}
                </span>
              </v-col>
            </v-row>

            <v-row v-if="item.remarks" no-gutters class="mt-1 py-3">
              <v-col cols="3">
                <h3>Remarks</h3>
              </v-col>
              <v-col cols="9">
                <span class="info-text fs-14">
                  {{ item.remarks }}
                </span>
              </v-col>
            </v-row>
            <v-divider class="ml-0 my-4"/>

            <!-- Person Giving Notice Table -->
            <v-row no-gutters class="pt-2">
              <v-col cols="3">
                <h3 class="py-2">Person Giving Notice</h3>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-simple-table
                  id="persons-giving-notice-table"
                  fixed-header
                >
                  <template v-slot:default>
                    <!-- Table Headers -->
                    <thead>
                      <tr>
                        <th v-for="header in personGivingNoticeTableHeaders" :key="header.value" :class="header.class">
                          {{ header.text }}
                        </th>
                      </tr>
                    </thead>

                    <!-- Table Body -->
                    <tbody v-if="item.givingNoticeParty">
                      <tr>
                        <td class="pl-0">
                          <div class="mr-2">
                            <v-icon class="notice-party-icon colour-dk-text mt-n2">
                              {{ getNoticePartyIcon(item.givingNoticeParty) }}
                            </v-icon>
                          </div>
                          <span class="notice-party-name generic-label fs-14">
                            {{ getNoticePartyName(item.givingNoticeParty) }}
                          </span>
                        </td>
                        <td>
                          <BaseAddress
                            :value="item.givingNoticeParty.address"
                          />
                        </td>
                        <td>{{ item.givingNoticeParty.emailAddress }}</td>
                        <td>{{ item.givingNoticeParty.phoneNumber }}</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-col>
            </v-row>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
      <v-col v-else class="empty-notes-msg text-center pt-8 pb-3">
        <p class="gray7 fs-14">A unit note has not been filed for this manufactured home.</p>
      </v-col>
    </v-row>

  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'
import { MhApiStatusTypes, MhUIStatusTypes, RouteNames, UnitNoteDocTypes } from '@/enums'
import { useRouter } from 'vue2-helpers/vue-router'
import { useStore } from '@/store/store'
import { personGivingNoticeTableHeaders, UnitNotesInfo, UnitNotesDropdown } from '@/resources'
import { UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'
import { pacificDate } from '@/utils'
import { PartyIF } from '@/interfaces'
import { BaseAddress } from '@/composables/address'

export default defineComponent({
  name: 'UnitNotePanels',
  components: {
    BaseAddress
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
  setup () {
    const router = useRouter()

    const {
      setMhrUnitNoteType
    } = useStore()

    const localState = reactive({
      activePanels: []
    })

    const initUnitNote = (noteType: UnitNoteDocTypes): void => {
      setMhrUnitNoteType(noteType)
      router.push({ path: '/' + RouteNames.MHR_INFORMATION_NOTE })
    }

    const getNoticePartyIcon = (givingNoticeParty: PartyIF): string => {
      return givingNoticeParty.businessName
        ? 'mdi-domain'
        : 'mdi-account'
    }

    const getNoticePartyName = (givingNoticeParty: PartyIF): string => {
      return givingNoticeParty.businessName
        ? givingNoticeParty.businessName
        : `${givingNoticeParty.personName.first}${givingNoticeParty.personName.middle}
          ${givingNoticeParty.personName.last}`
    }

    const cancelUnitNote = (unitNote: UnitNoteIF): void => {
      // Request to delete unit note here
    }

    return {
      initUnitNote,
      cancelUnitNote,
      pacificDate,
      getNoticePartyIcon,
      getNoticePartyName,
      UnitNotesInfo,
      UnitNotesDropdown,
      MhUIStatusTypes,
      MhApiStatusTypes,
      personGivingNoticeTableHeaders,
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
.unit-note-header-action {
  color: $primary-blue;
}
.unit-note-panel-row {
  background: $gray1;
  .unit-note-panel {
    border-bottom: 2px solid $gray1;
  }
}
.unit-note-list-item {
    background-color: white;
    :hover {
      cursor: pointer;
    }
  }
.cap-panels-height {
  max-height: 750px;
  overflow-y: auto;
}
.empty-notes-msg {
  background: white;
}
::v-deep {
  .theme--light.v-btn.v-btn--disabled {
    color: $primary-blue!important;
  }
  .v-divider {
    color: $gray3
  }
  .theme--light.v-data-table > .v-data-table__wrapper > table > thead > tr:last-child > th:first-child {
    padding-left: 0;
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
