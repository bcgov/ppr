<template>
  <!-- Note Information-->
  <div>
    <v-row
      v-if="note.effectiveDateTime && hasEffectiveDateInPanel(note) && !isExemptionNoteType"
      no-gutters
      class="mt-7"
      data-test-id="effective-date-info"
    >
      <v-col cols="3">
        <h3 class="fs-14">
          Effective Date
        </h3>
      </v-col>
      <v-col cols="9">
        <div class="info-text fs-14">
          {{ shortPacificDate(note.effectiveDateTime) }}
        </div>
      </v-col>
    </v-row>

    <v-row
      v-if="isNoticeOfCautionOrRelatedDocType(note)"
      no-gutters
      class="my-6"
    >
      <v-col cols="3">
        <h3 class="fs-14">
          Expiry Date
        </h3>
      </v-col>
      <v-col cols="9">
        <span
          v-if="note.expiryDateTime"
          class="info-text fs-14"
        >
          {{ shortPacificDate(note.expiryDateTime) }}
        </span>
        <span
          v-else
          id="no-expiry"
          class="info-text fs-14"
        >
          N/A
        </span>
      </v-col>
    </v-row>

    <v-row
      v-if="note.cancelledDateTime"
      no-gutters
      class="my-6"
    >
      <v-col cols="3">
        <h3 class="fs-14">
          Cancelled Date and Time
        </h3>
      </v-col>
      <v-col cols="9">
        <div class="info-text fs-14">
          {{ pacificDate(note.cancelledDateTime, true) }}
        </div>
      </v-col>
    </v-row>

    <v-row
      no-gutters
      class="mt-6"
      :class="{ 'mb-6': !isExemptionNoteType }"
      data-test-id="remarks-info"
    >
      <v-col cols="3">
        <h3 class="fs-14">
          Remarks
        </h3>
      </v-col>
      <v-col cols="9">
        <div
          v-if="!separatedRemarks"
          class="info-text fs-14"
        >
          {{ note.remarks || '(Not Entered)' }}
        </div>
        <template v-else>
          <div
            id="separated-remarks"
            class="info-text fs-14"
          >
            {{ separatedRemarks[0] }}
            <br>
            {{ separatedRemarks[1] }}
          </div>
        </template>
      </v-col>
    </v-row>

    <v-divider
      v-if="!isExemptionNoteType && (note.effectiveDateTime || note.expiryDateTime || note.remarks)"
      class="ml-0 my-4"
    />

    <!-- Person Giving Notice or Collector Table -->
    <v-row
      v-if="!isExemptionNoteType"
      no-gutters
      class="mt-7"
      data-test-id="person-giving-notice-info"
    >
      <v-col cols="3">
        <h3 class="fs-14">
          {{ contactInfoTitle }}
        </h3>
      </v-col>
      <v-col
        v-if="!note.givingNoticeParty"
        cols="9"
      >
        <div
          id="no-person-giving-notice"
          class="info-text fs-14"
        >
          {{ hasNoPersonGivingNoticeText }}
        </div>
      </v-col>
    </v-row>
    <v-row
      v-if="note.givingNoticeParty"
      no-gutters
    >
      <v-col cols="12">
        <v-table
          id="persons-giving-notice-table"
          fixed-header
          density="comfortable"
        >
          <template #default>
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
                  <div class="mr-2">
                    <v-icon class="notice-party-icon colour-dk-text mt-n2">
                      {{ getNoticePartyIcon(note.givingNoticeParty) }}
                    </v-icon>
                  </div>
                  <span class="notice-party-name generic-label fs-14">
                    {{ getNoticePartyName(note.givingNoticeParty) }}
                  </span>
                </td>
                <td>
                  <BaseAddress :value="note.givingNoticeParty.address" />
                </td>
                <td>{{ note.givingNoticeParty.emailAddress || '(Not Entered)' }}</td>
                <td>{{ note.givingNoticeParty.phoneNumber || '(Not Entered)' }}</td>
              </tr>
            </tbody>
          </template>
        </v-table>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, reactive, toRefs } from 'vue'
import { UnitNotePanelIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'
import {
  UnitNotesInfo,
  personGivingNoticeTableHeaders,
  collectorInformationContent,
  personGivingNoticeContent,
  hasNoPersonGivingNoticeText
} from '@/resources'
import { pacificDate, shortPacificDate } from '@/utils'
import { PartyIF } from '@/interfaces'
import { BaseAddress } from '@/composables/address'
import { useMhrUnitNote, useMhrUnitNotePanel } from '@/composables'
import { UnitNoteDocTypes } from '@/enums'

export default defineComponent({
  name: 'UnitNoteContentInfo',
  components: {
    BaseAddress
  },
  props: {
    note: {
      type: Object as () => UnitNotePanelIF,
      required: true
    }
  },
  setup (props) {
    const { isNoticeOfCautionOrRelatedDocType } = useMhrUnitNotePanel()

    const {
      hasEffectiveDateInPanel
    } = useMhrUnitNote()

    const localState = reactive({
      separatedRemarks: computed(() : string[] | null => {
        if (props.note.documentType === UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION && !props.note.expiryDateTime) {
          const remarks = props.note.remarks
          const generatedRemarks = UnitNotesInfo[props.note.documentType].generatedRemarks
          // No need to separate if no additional remarks + extra safety check
          if (remarks.trim() !== generatedRemarks && remarks.startsWith(generatedRemarks)) {
            return [generatedRemarks, remarks.substring(generatedRemarks.length)]
          }
        }
        return null
      }),
      contactInfoTitle: computed((): string =>
        props.note.documentType === UnitNoteDocTypes.NOTICE_OF_TAX_SALE
          ? collectorInformationContent.title
          : personGivingNoticeContent.title
      ),
      isExemptionNoteType: computed((): boolean =>
        [UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER, UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION]
          .includes(props.note.documentType))
    })

    const getNoticePartyIcon = (givingNoticeParty: PartyIF): string => {
      return givingNoticeParty.businessName
        ? 'mdi-domain'
        : 'mdi-account'
    }

    const getNoticePartyName = (givingNoticeParty: PartyIF): string => {
      return givingNoticeParty.businessName
        ? givingNoticeParty.businessName
        : `${givingNoticeParty.personName.first} ${givingNoticeParty.personName.middle ?? ''} ${givingNoticeParty.personName.last}` // eslint-disable-line max-len
    }

    return {
      pacificDate,
      shortPacificDate,
      getNoticePartyIcon,
      getNoticePartyName,
      hasEffectiveDateInPanel,
      isNoticeOfCautionOrRelatedDocType,
      personGivingNoticeTableHeaders,
      hasNoPersonGivingNoticeText,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
table {
  th:first-child,
  td:first-child {
    padding-left: 0 !important;
  }
}
</style>
