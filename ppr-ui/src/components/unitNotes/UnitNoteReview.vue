<template>
  <div id="unit-note-review-confirm">
    <v-card flat id="unit-note-info-review" class="mt-6">
      <header class="review-header">
        <v-icon class="ml-2" color="darkBlue">mdi-message-reply-text</v-icon>
        <label class="font-weight-bold pl-2">Unit Notes</label>
      </header>

      <div>
        <section class="pa-6">
          <v-row no-gutters class="">
            <v-col cols="3">
              <h3>Unit Note Type</h3>
            </v-col>
            <v-col cols="9">
              {{ unitNoteType.header }}
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col cols="3">
              <h3>Document ID</h3>
            </v-col>
            <v-col cols="9">
              {{ getMhrUnitNote.documentId }}
            </v-col>
          </v-row>
          <v-divider class="my-3 mx-0" />
          <v-row no-gutters>
            <v-col cols="3">
              <h3>Remarks</h3>
            </v-col>
            <v-col cols="9">
              <p>{{ getMhrUnitNote.remarks }}</p>
            </v-col>
          </v-row>
          <v-divider class="my-3 mx-0" />
          <div class="px">
            <h3>Person Giving Notice</h3>

            <v-simple-table v-if="getMhrUnitNote" class="giving-notice-party-table" data-test-id="account-info-table">
              <template v-slot:default>
                <thead>
                  <tr>
                    <th class="px-0">
                      Name
                    </th>
                    <th class="px-0">
                      Mailing Address
                    </th>
                    <th class="px-0">
                      Email Address
                    </th>
                    <th class="px-0">
                      Phone Number
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="person-name">
                      <v-icon class="mt-n2">
                        {{ getMhrUnitNote.businessName ? 'mdi-domain' : 'mdi-account' }}
                      </v-icon>
                      <span class="font-weight-bold">
                        {{ givingNoticeParty.personName.first }}
                        {{ givingNoticeParty.personName.middle }}
                        {{ givingNoticeParty.personName.last }}
                      </span>
                    </td>
                    <td class="">
                      <base-address
                        :editing="false"
                        :schema="PartyAddressSchema"
                        :value="givingNoticeParty.address"
                      />
                    </td>
                    <td class="">
                      {{ givingNoticeParty.emailAddress }}
                    </td>
                    <td class="">
                      {{ toDisplayPhone(givingNoticeParty.phoneNumber) }}
                      <span v-if="givingNoticeParty.phoneExtension">
                        Ext {{ givingNoticeParty.phoneExtension }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </div>
        </section>
      </div>
    </v-card>

    <section id="mhr-unit-note-person-giving-notice" class="mt-15">
      <ContactInformation
        :contactInfo="unitNoteSubmittingParty"
        :content="{
          title: '1. Submitting Party for this Change',
          description: 'Provide the name and contact information for the person or business submitting ' +
          ' this registration. You can add the submitting party information manually, or, if the submitting ' +
          'party has a Personal Property Registry party code, you can look up the party code or name.',
          sideLabel: 'Add Submitting Party'
        }"
        :validate="validate"
        :setStoreProperty="setSubmittingParty"
        @isValid="handleComponentValid(MhrCompVal.SUBMITTING_PARTY_VALID, $event)"
      />
    </section>

    <section class="mt-15">
      <h2>2. Effective Date and Time</h2>
      <p class="mt-2">
        Select the effective date and time for this {{ unitNoteType.header }}. Custom date and time can
        be a date and time in the past. Notice of Caution will expire 90 days after the effective date.
      </p>
      // Placeholder for the component
    </section>

    <section class="mt-15">
      <Attention
        section-id="mhr-attention"
        :section-number="3"
        :validate="validate"
        @isAttentionValid="handleComponentValid(MhrCompVal.ATTENTION_VALID, $event)"
      />
    </section>

    <!-- Authorization -->
    <section id="mhr-certify-section" class="mt-15">
      <CertifyInformation
        :sectionNumber="4"
        :setShowErrors="validate"
        :content="{
          description: 'The following account information will be recorded by BC Registries upon ' +
          'registration and payment. This information is used to confirm you have the authority ' +
          'to submit this registration. The following information must be completed and confirmed ' +
          'before submitting this registration.',
        }"
        @certifyValid="handleComponentValid(MhrCompVal.AUTHORIZATION_VALID, $event)"
      />
    </section>

    <section id="staff-transfer-payment-section" class="mt-10 pt-4 pb-10" v-if="isRoleStaffReg">
      <h2>5. Staff Payment</h2>
      <v-card flat class="mt-6 pa-6" :class="{ 'border-error-left': validateStaffPayment }">
        <StaffPayment
          id="staff-payment"
          :displaySideLabel="true"
          :displayPriorityCheckbox="true"
          :staffPaymentData="staffPayment"
          :invalidSection="validateStaffPayment"
          :validate="validate"
          @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
          @valid="handleComponentValid(MhrCompVal.STAFF_PAYMENT_VALID, $event)"
        />
      </v-card>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { PartyAddressSchema } from '@/schemas'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { toDisplayPhone } from '@/utils'
import { BaseAddress } from '@/composables/address'
import { PartyIF, SubmittingPartyIF } from '@/interfaces'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { useMhrValidations } from '@/composables'
import { CertifyInformation, ContactInformation } from '../common'
import { Attention } from '../mhrRegistration/ReviewConfirm'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'

export default defineComponent({
  name: 'UnitNoteReview',
  components: { BaseAddress, ContactInformation, Attention, CertifyInformation, StaffPayment },
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const {
      getMhrUnitNote,
      getMhrUnitNoteRegistration,
      getMhrUnitNoteValidation,
      isRoleStaffReg
    } = storeToRefs(useStore())

    const {
      setMhrUnitNote,
      setMhrUnitNoteRegistration,
      setStaffPayment
    } = useStore()

    const {
      getValidation,
      setValidation
    } = useMhrValidations(toRefs(getMhrUnitNoteValidation.value))

    const localState = reactive({
      validate: false,
      validateSubmittingParty: false,
      unitNoteType: UnitNotesInfo[getMhrUnitNote.value.documentType],
      givingNoticeParty: computed((): PartyIF => getMhrUnitNote.value.givingNoticeParty),
      unitNoteSubmittingParty: computed(() => getMhrUnitNoteRegistration.value.submittingParty || {}),
      staffPayment: {
        option: StaffPaymentOptions.NONE,
        routingSlipNumber: '',
        bcolAccountNumber: '',
        datNumber: '',
        folioNumber: '',
        isPriority: false
      },
      validateStaffPayment: computed(() => {
        return isRoleStaffReg.value &&
        localState.validate &&
        !getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.STAFF_PAYMENT_VALID)
      })
    })

    const setGivingNoticeParty = (val: PartyIF) => {
      setMhrUnitNote({ key: 'givingNoticeParty', value: val })
    }

    const setSubmittingParty = (val: SubmittingPartyIF) => {
      setMhrUnitNoteRegistration({ key: 'submittingParty', value: val })
    }

    const handleComponentValid = (component: MhrCompVal, isValid: boolean) => {
      setValidation(MhrSectVal.UNIT_NOTE_VALID, component, isValid)
    }

    const onStaffPaymentDataUpdate = (val: StaffPaymentIF) => {
      let staffPaymentData: StaffPaymentIF = {
        ...val
      }

      switch (staffPaymentData.option) {
        case StaffPaymentOptions.FAS:
          staffPaymentData = {
            option: StaffPaymentOptions.FAS,
            routingSlipNumber: staffPaymentData.routingSlipNumber,
            isPriority: staffPaymentData.isPriority,
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: ''
          }
          break

        case StaffPaymentOptions.BCOL:
          staffPaymentData = {
            option: StaffPaymentOptions.BCOL,
            bcolAccountNumber: staffPaymentData.bcolAccountNumber,
            datNumber: staffPaymentData.datNumber,
            folioNumber: staffPaymentData.folioNumber,
            isPriority: staffPaymentData.isPriority,
            routingSlipNumber: ''
          }
          break

        case StaffPaymentOptions.NO_FEE:
          staffPaymentData = {
            option: StaffPaymentOptions.NO_FEE,
            routingSlipNumber: '',
            isPriority: false,
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: ''
          }
          break
        case StaffPaymentOptions.NONE: // should never happen
          break
      }

      localState.staffPayment = staffPaymentData
      setStaffPayment(staffPaymentData)
    }

    return {
      isRoleStaffReg,
      MhrCompVal,
      getMhrUnitNote,
      PartyAddressSchema,
      toDisplayPhone,
      setSubmittingParty,
      setGivingNoticeParty,
      handleComponentValid,
      onStaffPaymentDataUpdate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

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
</style>
