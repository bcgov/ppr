<template>
  <div id="unit-note-review-confirm">

    <UnitNoteReviewDetailsTable
      :unitNote="getMhrUnitNote"
      :unitNoteType="unitNoteType.header"
    />

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
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { PartyIF, SubmittingPartyIF } from '@/interfaces'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { useMhrValidations } from '@/composables'
import { CertifyInformation, ContactInformation } from '../common'
import UnitNoteReviewDetailsTable from './UnitNoteReviewDetailsTable.vue'
import { Attention } from '../mhrRegistration/ReviewConfirm'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'

export default defineComponent({
  name: 'UnitNoteReview',
  components: {
    UnitNoteReviewDetailsTable,
    ContactInformation,
    Attention,
    CertifyInformation,
    StaffPayment
  },
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
      // setMhrUnitNote,
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
      setSubmittingParty,
      handleComponentValid,
      onStaffPaymentDataUpdate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
</style>
