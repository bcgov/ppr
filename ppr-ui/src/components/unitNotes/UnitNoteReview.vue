<template>
  <div id="unit-note-review-confirm">

    <h1>
      Review and Confirm
    </h1>
    <p class="mt-7">
      Review your changes and complete the additional information before registering.
    </p>

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
        @setStoreProperty="handleStoreUpdate('submittingParty', $event)"
        @isValid="handleComponentValid(MhrCompVal.SUBMITTING_PARTY_VALID, $event)"
      />
    </section>

    <section v-if="hasEffectiveDateTime()" class="mt-15">
      <EffectiveDateTime
        :sectionNumber="getSectionNumber.effectiveDateTime || 2"
        :content="{
          title: 'Effective Date and Time',
          description: `Select the effective date and time for this ${unitNoteType.header}.  ` +
          'Custom date and time can be a date and time in the past.' + effectiveDateDescForCAU,
          sideLabel: 'Effective Date and Time'
        }"
        :validate="validate"
        @setStoreProperty="handleEffectiveDateUpdate($event)"
        @isValid="handleComponentValid(MhrCompVal.EFFECTIVE_DATE_TIME_VALID, $event)"
      />
    </section>

    <section v-if="hasExpiryDate()" class="mt-15">
      <ExpiryDate
        :sectionNumber="getSectionNumber.expiryDate || 2"
        :content="{
          title: 'Expiry Date',
          description: `Select the expiry date for this ${unitNoteType.header}.`,
          sideLabel: 'Expiry Date'
        }"
        :validate="validate"
        :hideContinuedExpiryDate="isUnitNoteTypeCAUE"
        @setStoreProperty="handleStoreUpdate('expiryDateTime', $event)"
        @isValid="handleComponentValid(MhrCompVal.EXPIRY_DATE_TIME_VALID, $event)"
      />

    </section>

    <section class="mt-15">
      <Attention
        sectionId="mhr-unit-note-attention"
        :sectionNumber="getSectionNumber.attention || 3"
        :validate="validate"
        :initialValue="initialAttention"
        @isAttentionValid="handleComponentValid(MhrCompVal.ATTENTION_VALID, $event)"
        @setStoreProperty="handleStoreUpdate('attentionReference', $event)"
      />
    </section>

    <!-- Authorization -->
    <section id="mhr-certify-section" class="mt-15">
      <CertifyInformation
        :sectionNumber="getSectionNumber.certifyInfo || 4"
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
      <h2>{{ getSectionNumber.staffPayment || 5 }}. Staff Payment</h2>
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
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { PartyIF } from '@/interfaces'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { useMhrUnitNote, useMhrValidations } from '@/composables'
import { Attention, CertifyInformation, ContactInformation } from '../common'
import UnitNoteReviewDetailsTable from './UnitNoteReviewDetailsTable.vue'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { UnitNoteDocTypes } from '@/enums'
import EffectiveDateTime from './EffectiveDateTime.vue'
import ExpiryDate from './ExpiryDate.vue'

export default defineComponent({
  name: 'UnitNoteReview',
  components: {
    UnitNoteReviewDetailsTable,
    ContactInformation,
    EffectiveDateTime,
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
      setMhrUnitNote,
      setMhrUnitNoteRegistration,
      setStaffPayment
    } = useStore()

    const {
      getValidation,
      setValidation
    } = useMhrValidations(toRefs(getMhrUnitNoteValidation.value))

    const {
      hasEffectiveDateTime,
      hasExpiryDate
    } = useMhrUnitNote()

    const localState = reactive({
      validateSubmittingParty: false,
      initialAttention: getMhrUnitNoteRegistration.value?.attentionReference,
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
      ),
      getSectionNumber: computed((): Object =>
        localState.unitNoteType?.reviewSectionNumber || {}
      )
    })

    const handleEffectiveDateUpdate = (val: string) => {
      setMhrUnitNote({ key: 'effectiveDateTime', value: val })
      // expiry date is 90 days from effective date
      const expiryDateTime = new Date(new Date(val).getTime() + 90 * 24 * 60 * 60 * 1000).toISOString()
      setMhrUnitNote({ key: 'expiryDateTime', value: expiryDateTime })
    }

    const handleComponentValid = (component: MhrCompVal, isValid: boolean) => {
      setValidation(MhrSectVal.UNIT_NOTE_VALID, component, isValid)
    }

    const handleStoreUpdate = (key: string, val) => {
      setMhrUnitNoteRegistration({ key: key, value: val })
    }

    const effectiveDateDescForCAU = getMhrUnitNote.value.documentType === UnitNoteDocTypes.NOTICE_OF_CAUTION
      ? ' Notice of Caution will expire 90 days after the effective date.'
      : ''

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
        document.getElementById('unit-note-review-confirm').scrollIntoView({ behavior: 'smooth' })
      }, 500)
    })

    watch(() => localState.isUnitNoteReviewValid, (val) => {
      emit('isValid', val)
    })

    return {
      isRoleStaffReg,
      MhrCompVal,
      getMhrUnitNote,
      handleEffectiveDateUpdate,
      handleComponentValid,
      handleStoreUpdate,
      onStaffPaymentDataUpdate,
      effectiveDateDescForCAU,
      hasEffectiveDateTime,
      hasExpiryDate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
</style>
