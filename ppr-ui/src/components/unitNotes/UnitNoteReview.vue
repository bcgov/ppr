<template>
  <div
    id="unit-note-review-confirm"
    class="increment-sections"
  >
    <h1>
      Review and Confirm
    </h1>
    <p class="mt-7">
      Review your changes and complete the additional information before registering.
    </p>

    <p
      v-if="isCancelUnitNote"
      class="mb-15"
      data-test-id="cancel-note-info"
    >
      <b>Note:</b> Once this Cancel Note is registered, the original
      {{ getCancelledUnitNoteType() }} will no longer
      be shown when a search result is produced for this manufactured home.
    </p>

    <p
      v-else-if="isRedemptionUnitNote"
      class="mb-15"
      data-test-id="redemption-note-info"
    >
      <b>Note:</b> Once this Notice of Redemption is registered, the original Notice of Tax Sale will no longer
      be shown when a search result is produced for this manufactured home.
    </p>

    <UnitNoteReviewDetailsTable
      :unit-note="getMhrUnitNote"
      :unit-note-type="`${unitNoteType.header} ${getCancelledUnitNoteHeader()} `"
    />

    <section
      id="mhr-unit-note-person-giving-notice"
      class="mt-15"
    >
      <ContactInformation
        :contact-info="unitNoteSubmittingParty"
        :content="isRedemptionUnitNote ? submittingPartyRegistrationContent : submittingPartyChangeContent"
        :validate="validate"
        @set-store-property="handleStoreUpdate('submittingParty', $event)"
        @is-valid="handleComponentValid(MhrCompVal.SUBMITTING_PARTY_VALID, $event)"
      />
    </section>

    <section
      v-if="hasEffectiveDateTime()"
      class="mt-15"
    >
      <EffectiveDate
        :content="{
          title: 'Effective Date',
          description: `Select the effective date for this ${unitNoteType.header}.  ` +
            'Custom date can be a date in the past.',
          sideLabel: 'Effective Date',
          dateSummaryLabel: `${unitNoteType.header} on this home effective: `
        }"
        :validate="validate"
        @set-store-property="handleEffectiveDateUpdate($event)"
        @is-valid="handleComponentValid(MhrCompVal.EFFECTIVE_DATE_TIME_VALID, $event)"
      />
    </section>

    <section
      v-if="hasExpiryDate()"
      class="mt-15"
    >
      <ExpiryDate
        :content="{
          title: 'Expiry Date',
          description: `Select the expiry date for this ${unitNoteType.header}.`,
          sideLabel: 'Expiry Date'
        }"
        :validate="validate"
        :hide-continued-expiry-date="isUnitNoteTypeCAUE"
        @set-store-property="handleExpiryDateUpdate($event)"
        @is-valid="handleComponentValid(MhrCompVal.EXPIRY_DATE_TIME_VALID, $event)"
      />
    </section>

    <section class="mt-15">
      <Attention
        section-id="mhr-unit-note-attention"
        :validate="validate"
        :initial-value="initialAttention"
        @is-attention-valid="handleComponentValid(MhrCompVal.ATTENTION_VALID, $event)"
        @set-store-property="handleStoreUpdate('attentionReference', $event)"
      />
    </section>

    <!-- Authorization -->
    <section
      id="mhr-certify-section"
      class="mt-15"
    >
      <CertifyInformation
        :content="{
          description: 'The following account information will be recorded by BC Registries upon ' +
            'registration and payment. This information is used to confirm you have the authority ' +
            'to submit this registration. The following information must be completed and confirmed ' +
            'before submitting this registration.',
        }"
        :set-show-errors="validate"
        @certify-valid="handleComponentValid(MhrCompVal.AUTHORIZATION_VALID, $event)"
      />
    </section>

    <section
      v-if="isRoleStaffReg"
      id="staff-transfer-payment-section"
      class="mt-10 pt-4"
    >
      <h3 class="fs-18">
        Staff Payment
      </h3>
      <v-card
        flat
        class="mt-6 pa-6"
        :class="{ 'border-error-left': validateStaffPayment }"
      >
        <StaffPayment
          id="staff-payment"
          :display-side-label="true"
          :display-priority-checkbox="true"
          :staff-payment-data="staffPayment"
          :invalid-section="validateStaffPayment"
          :validate="validate"
          @update:staff-payment-data="onStaffPaymentDataUpdate($event)"
          @valid="handleComponentValid(MhrCompVal.STAFF_PAYMENT_VALID, $event)"
        />
      </v-card>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import type { CancelUnitNoteIF, PartyIF, StaffPaymentIF } from '@/interfaces'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { useMhrUnitNote, useMhrValidations } from '@/composables'
import { Attention, CertifyInformation, ContactInformation } from '../common'
import UnitNoteReviewDetailsTable from './UnitNoteReviewDetailsTable.vue'
import { StaffPayment } from '@/components/common'
import { StaffPaymentOptions, UnitNoteDocTypes } from '@/enums'
import EffectiveDate from './EffectiveDate.vue'
import ExpiryDate from './ExpiryDate.vue'
import { submittingPartyRegistrationContent, submittingPartyChangeContent } from '@/resources'

export default defineComponent({
  name: 'UnitNoteReview',
  components: {
    UnitNoteReviewDetailsTable,
    ContactInformation,
    EffectiveDate,
    ExpiryDate,
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
  emits: ['isValid'],
  setup (props, { emit }) {
    const {
      getMhrUnitNote,
      getMhrUnitNoteRegistration,
      getMhrUnitNoteValidation,
      isRoleStaffReg
    } = storeToRefs(useStore())

    const {
      setMhrUnitNoteProp,
      setMhrUnitNoteRegistration,
      setStaffPayment
    } = useStore()

    const {
      getValidation,
      setValidation
    } = useMhrValidations(toRefs(getMhrUnitNoteValidation.value))

    const {
      hasEffectiveDateTime,
      hasExpiryDate,
      getCancelledUnitNoteHeader,
      isCancelUnitNote,
      isRedemptionUnitNote
    } = useMhrUnitNote()

    const localState = reactive({
      validateSubmittingParty: false,
      initialAttention: isRedemptionUnitNote.value
        ? ''
        : getMhrUnitNoteRegistration.value?.attentionReference,
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
        props.validate &&
        !getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.STAFF_PAYMENT_VALID)
      }),
      isUnitNoteReviewValid: computed((): boolean =>
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.SUBMITTING_PARTY_VALID) &&
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.EFFECTIVE_DATE_TIME_VALID) &&
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.ATTENTION_VALID) &&
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.AUTHORIZATION_VALID) &&
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.STAFF_PAYMENT_VALID) && (
          hasExpiryDate()
            ? getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.EXPIRY_DATE_TIME_VALID)
            : true
        )
      ),
      isUnitNoteTypeCAUE: computed((): boolean =>
        getMhrUnitNote.value.documentType === UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION
      )
    })

    const handleEffectiveDateUpdate = (val: string) => {
      setMhrUnitNoteProp({ key: 'effectiveDateTime', value: val })
    }

    const handleExpiryDateUpdate = (val: string) => {
      setMhrUnitNoteProp({ key: 'expiryDateTime', value: val })
    }

    const handleComponentValid = (component: MhrCompVal, isValid: boolean) => {
      setValidation(MhrSectVal.UNIT_NOTE_VALID, component, isValid)
    }

    const handleStoreUpdate = (key: string, val) => {
      setMhrUnitNoteRegistration({ key, value: val })
    }

    const getCancelledUnitNoteType = (): string => {
      const cancelledUnitNote: CancelUnitNoteIF = getMhrUnitNote.value as CancelUnitNoteIF
      return UnitNotesInfo[cancelledUnitNote.cancelledDocumentType].header
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

    onMounted(() => {
      // scroll to top
      setTimeout(() => {
        document.getElementById('unit-note-review-confirm')?.scrollIntoView({ behavior: 'smooth' })
      }, 500)
    })

    watch(() => localState.isUnitNoteReviewValid, (val) => {
      emit('isValid', val)
    })

    return {
      isRoleStaffReg,
      MhrCompVal,
      getMhrUnitNote,
      getCancelledUnitNoteHeader,
      getCancelledUnitNoteType,
      handleEffectiveDateUpdate,
      handleComponentValid,
      handleStoreUpdate,
      onStaffPaymentDataUpdate,
      hasEffectiveDateTime,
      handleExpiryDateUpdate,
      hasExpiryDate,
      isCancelUnitNote,
      isRedemptionUnitNote,
      submittingPartyRegistrationContent,
      submittingPartyChangeContent,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
