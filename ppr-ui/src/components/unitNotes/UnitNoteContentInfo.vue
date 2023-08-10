<template>
  <!-- Note Information-->
  <div>
    <v-row v-if="note.effectiveDateTime" no-gutters class="pt-3">
      <v-col cols="3">
        <h3 class="fs-14">Effective Date and Time</h3>
      </v-col>
      <v-col cols="9">
        <span class="info-text fs-14">
          {{ pacificDate(note.effectiveDateTime) }}
        </span>
      </v-col>
    </v-row>

    <v-row v-if="note.expiryDateTime" no-gutters class="pt-3">
      <v-col cols="3">
        <h3 class="fs-14">Expiry Date and Time</h3>
      </v-col>
      <v-col cols="9">
        <span class="info-text fs-14">
          {{ pacificDate(note.expiryDateTime) }}
        </span>
      </v-col>
    </v-row>

    <v-row v-if="note.remarks" no-gutters class="mt-1 py-3">
      <v-col cols="3">
        <h3 class="fs-14">Remarks</h3>
      </v-col>
      <v-col cols="9">
        <span class="info-text fs-14">
          {{ note.remarks }}
        </span>
      </v-col>
    </v-row>

    <v-divider
      v-if="note.effectiveDateTime || note.expiryDateTime || note.remarks"
      class="ml-0 my-4"
    />

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
                <th
                  v-for="header in personGivingNoticeTableHeaders"
                  :key="header.value"
                  :class="header.class"
                >
                  {{ header.text }}
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody>
              <tr>
                <td class="pl-0">
                  <template  v-if="getPartyData('personName') || getPartyData('businessName')">
                    <div class="mr-2">
                      <v-icon
                        class="notice-party-icon colour-dk-text mt-n2">
                        {{ getNoticePartyIcon(note.givingNoticeParty) }}
                      </v-icon>
                    </div>
                    <span class="notice-party-name generic-label fs-14">
                        {{ getNoticePartyName(note.givingNoticeParty) }}
                    </span>
                  </template>
                  <span v-else>(Not Entered)</span>
                </td>
                <td>
                  <BaseAddress v-if="getPartyData('address')" :value="note.givingNoticeParty.address"/>
                  <span v-else>(Not Entered)</span>
                </td>
                <td>{{ getPartyData('emailAddress') || '(Not Entered)' }}</td>
                <td>{{ getPartyData('phoneNumber') || '(Not Entered)'  }}</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>
 </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue-demi'
import { personGivingNoticeTableHeaders } from '@/resources'
import { UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'
import { pacificDate } from '@/utils'
import { PartyIF } from '@/interfaces'
import { BaseAddress } from '@/composables/address'

export default defineComponent({
  name: 'UnitNoteContentInfo',
  props: {
    note: {
      type: Object as () => UnitNoteIF,
      required: true
    }
  },
  components: {
    BaseAddress
  },
  setup (props) {
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

    const getPartyData = (property: keyof(PartyIF)): any => {
      return props.note?.givingNoticeParty?.[property]
    }

    return {
      pacificDate,
      getPartyData,
      getNoticePartyIcon,
      getNoticePartyName,
      personGivingNoticeTableHeaders
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
h3 {
  line-height: 1.5;
}
::v-deep {
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
