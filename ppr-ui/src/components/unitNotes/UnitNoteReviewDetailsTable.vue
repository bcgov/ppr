<template>
  <v-card id="unit-note-review-details" class="mt-6" flat>
    <header class="review-header">
      <v-icon class="ml-2" color="darkBlue">mdi-message-reply-text</v-icon>
      <label class="font-weight-bold pl-2">Unit Notes</label>
    </header>

    <section class="unit-note-review-details-table pa-6">
      <v-row no-gutters>
        <v-col cols="3">
          <h3>Unit Note Type</h3>
        </v-col>
        <v-col cols="9" class="details">
          {{ unitNoteType }}
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="3">
          <h3>Document ID</h3>
        </v-col>
        <v-col cols="9" class="details">
          {{ unitNote.documentId }}
        </v-col>
      </v-row>
      <v-divider class="my-3 mx-0" />
      <v-row no-gutters>
        <v-col cols="3">
          <h3>Remarks</h3>
        </v-col>
        <v-col cols="9" class="remarks">
          <span v-html="unitNoteRemarks || '(Not Entered)'"></span>
        </v-col>
      </v-row>
      <v-divider class="my-3 mx-0" />
      <v-row no-gutters v-if="unitNote.hasNoPersonGivingNotice">
        <v-col cols="3">
          <h3>{{ contactInfoTitle }}</h3>
        </v-col>
        <v-col cols="9" class="no-person-giving-notice">
          {{ hasNoPersonGivingNoticeText }}
        </v-col>
      </v-row>
      <template v-else>
        <h3>{{ contactInfoTitle }}</h3>

        <v-simple-table v-if="givingNoticeParty" class="giving-notice-party-table" data-test-id="party-info-table">
          <template v-slot:default>
            <thead>
              <tr>
                <th class="px-0">Name</th>
                <th class="px-0">Mailing Address</th>
                <th class="px-0">Email Address</th>
                <th class="px-0">Phone Number</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="person-name">
                  <span>
                    <v-icon class="mt-n2">
                      {{ givingNoticeParty.businessName ? 'mdi-domain' : 'mdi-account' }}
                    </v-icon>
                    <span class="font-weight-bold">
                      {{ displayFullOrBusinessName }}
                    </span>
                  </span>
                </td>
                <td>
                  <base-address
                    :editing="false"
                    :schema="PartyAddressSchema"
                    :value="givingNoticeParty.address"
                  />
                </td>
                <td>
                  <span :class="{'text-not-entered': !givingNoticeParty.emailAddress}">
                    {{ givingNoticeParty.emailAddress || '(Not Entered)' }}
                  </span>
                </td>
                <td>
                  <span :class="{'text-not-entered': !givingNoticeParty.phoneNumber}">
                    {{ givingNoticeParty.phoneNumber ? displayPhoneAndExt : '(Not Entered)' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </template>
    </section>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { BaseAddress } from '@/composables/address'
import { PartyIF, UnitNoteIF } from '@/interfaces'
import { PartyAddressSchema } from '@/schemas'
import { toDisplayPhone } from '@/utils'
import { personGivingNoticeContent, collectorInformationContent, hasNoPersonGivingNoticeText } from '@/resources'
import { UnitNoteDocTypes } from '@/enums/unitNoteDocTypes'

export default defineComponent({
  name: 'UnitNoteReviewDetailsTable',
  components: {
    BaseAddress
  },
  props: {
    unitNote: {
      type: Object as () => UnitNoteIF,
      required: true
    },
    unitNoteType: {
      type: String,
      required: true
    }
  },
  setup (props) {
    const localState = reactive({
      givingNoticeParty: computed((): PartyIF => props.unitNote.givingNoticeParty),
      unitNoteRemarks: computed((): string =>
        props.unitNote.additionalRemarks
          ? props.unitNote.additionalRemarks + '<br/>' + props.unitNote.remarks
          : props.unitNote.remarks
      ),
      displayFullOrBusinessName: computed((): string => {
        if (localState.givingNoticeParty?.businessName?.length > 0) {
          return localState.givingNoticeParty?.businessName
        }
        const { first, middle, last } = localState.givingNoticeParty.personName
        return [first, middle, last].filter(Boolean).join(' ')
      }),
      displayPhoneAndExt: computed((): string =>
        toDisplayPhone(localState.givingNoticeParty.phoneNumber) +
        (localState.givingNoticeParty.phoneExtension ? ' Ext ' + localState.givingNoticeParty.phoneExtension : '')
      ),
      contactInfoTitle: computed((): string =>
        props.unitNote.documentType === UnitNoteDocTypes.NOTICE_OF_TAX_SALE
          ? collectorInformationContent.title
          : personGivingNoticeContent.title
      )
    })

    return {
      hasNoPersonGivingNoticeText,
      toDisplayPhone,
      PartyAddressSchema,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#unit-note-review-details {

  .unit-note-review-details-table {
    .details {
      line-height: 2em;
      color: $gray7;
    }
    .remarks {
      padding: 6px 0;
      line-height: 24px;
      color: $gray7;
    }
    .no-person-giving-notice {
      padding: 6px 0;
      line-height: 24px;
      color: $gray7;
    }
  }
  .giving-notice-party-table.v-data-table {
    thead tr th {
      padding: 0;
    }
    tbody {
      vertical-align: top;
      tr > td {
        padding-left: 0;
        padding-right: 0;
        padding-top: 25px;
      }
      .person-name,
      i {
        color: $gray9 !important;
      }
    }
  }
}
</style>
