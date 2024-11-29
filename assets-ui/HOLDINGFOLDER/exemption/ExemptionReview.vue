<template>
  <section
    id="exemption-review"
    aria-label="exemption-review"
  >
    <LienAlert v-if="hasLien" />

    <v-row
      no-gutters
      class="soft-corners-top"
    >
      <v-col
        class="role"
        cols="auto"
        aria-label="exemption-review-help"
      >
        <h2 class="mt-10">
          Review and Confirm
        </h2>
        <p class="mt-1">
          Review the information in your exemption and complete the additional information below.
          <span v-if="isRoleStaffReg">
            If you need to change anything, return to the previous step to make the necessary change.
          </span>
        </p>
      </v-col>
    </v-row>

    <!-- Exemption Content Review -->
    <ReviewCard
      v-if="isRoleStaffReg"
      class="mt-5"
      :show-incomplete="showIncompleteError"
      :review-properties="reviewContent"
      :return-to-routes="[RouteNames.RESIDENTIAL_EXEMPTION, RouteNames.EXEMPTION_DETAILS]"
    >
      <template #headerSlot>
        <header class="review-header">
          <img
            alt="exemption-icon"
            class="ml-0 icon-large"
            src="../../src/assets/svgs/ic_exemption2.svg"
          >
          <label class="font-weight-bold pl-2">{{ exemptionLabel }}</label>
        </header>
      </template>
    </ReviewCard>

    <section
      v-if="isExemptionWithActiveTransportPermit"
      data-test-id="exemption-active-permit-section"
      class="mt-15"
    >
      <CautionBox
        class="mb-8"
        :set-msg="`The transport permit on this home will be void upon filing this ${exemptionLabel}`"
      />

      <TransportPermitDetails
        is-void-permit
        class="mt-5 void-transport-permit-details-review"
      />
    </section>

    <section
      v-if="isRoleQualifiedSupplier"
      id="exemptions-qs-submitting-party"
      class="mt-10"
    >
      <AccountInfo
        title="Submitting Party"
        tooltip-content="The default Submitting Party is based on your BC Registries user account information. This
          information can be updated within your account settings."
        :account-info="parseSubmittingPartyToAccountInfo(getMhrExemption.submittingParty)"
      />
    </section>

    <div class="increment-sections mt-13">
      <!-- Submitting Party -->
      <section v-if="isRoleStaffReg">
        <h2>Submitting Party</h2>
        <p>
          Provide the name and contact information for the person or business submitting this exemption. You can add
          the submitting party information manually, or, if the submitting party has a Personal Property Registry party
          code, you can look up the party code or name.
        </p>

        <PartySearch
          is-mhr-party-search
          class="mb-8 rounded-all"
          @select-item="handlePartySelect"
        />

        <FormCard
          label="Add Submitting party"
          :show-errors="showErrors && !getMhrExemptionValidation.submittingParty"
          :class="{ 'border-error-left': showErrors && !getMhrExemptionValidation.submittingParty }"
        >
          <template #formSlot>
            <PartyForm
              ref="exemptions-submitting-party"
              :base-party="getMhrExemption.submittingParty"
              :schema="ExemptionPartyFormSchema"
              :show-errors="showErrors && !getMhrExemptionValidation.submittingParty"
              @is-valid="updateValidation('submittingParty', $event)"
            />
          </template>
        </FormCard>
      </section>

      <!-- Attention -->
      <section
        v-if="isRoleStaffReg"
        class="mt-13"
      >
        <Attention
          section-id="mhr-exemption-attention"
          :validate="showErrors && !getMhrExemptionValidation.attention"
          :config-override="attentionExemptionConfig"
          @set-store-property="handleValueUpdate('attentionReference', $event)"
          @is-attention-valid="updateValidation('attention', $event)"
        />
      </section>

      <section
        v-if="isRoleQualifiedSupplier"
        class="mt-13"
      >
        <FolioOrReferenceNumber
          section-id="mhr-exemption-folio"
          data-test-id="attn-ref-exemptions"
          :validate="showErrors && !getMhrExemptionValidation.folio"
          @set-store-property="handleValueUpdate('clientReferenceId', $event)"
          @is-folio-or-ref-num-valid="updateValidation('folio', $event)"
        />
      </section>

      <!-- Confirm Requirements -->
      <section class="mt-13">
        <ConfirmCompletion
          :legal-name="getCertifyInformation.legalName"
          :set-show-errors="showErrors && !getMhrExemptionValidation.confirmCompletion"
          @confirm-completion="updateValidation('confirmCompletion', $event)"
        >
          <template #contentSlot>
            <ListRequirements
              class="mb-4"
              :requirements="isRoleStaffReg
                ? isNonResExemption ? nonResExConfirmRequirements : exConfirmRequirements
                : exConfirmRequirementsQs"
            />
            <p
              v-if="isRoleStaffReg && !isNonResExemption"
              class="ml-9 hint-message"
            >
              If there is a Personal Property Security Act (PPSA) security interest registered against this manufactured
              home, such registration has been discharged or consent to the exemption application of each secured party
              under the security agreement has been obtained.
            </p>
          </template>
        </ConfirmCompletion>
      </section>

      <!-- Authorization -->
      <section class="mt-13">
        <CertifyInformation
          :content="exCertifyInfoContent"
          :set-show-errors="showErrors && !getMhrExemptionValidation.authorization"
          @certify-valid="updateValidation('authorization', $event)"
        />
      </section>

      <!-- Staff Payment -->
      <section
        v-if="isRoleStaffReg && !isNonResExemption"
        class="mt-13"
      >
        <h2>Staff Payment</h2>
        <v-card
          flat
          class="mt-4 pa-8"
          :class="{ 'border-error-left': showErrors && !getMhrExemptionValidation.staffPayment }"
        >
          <StaffPayment
            id="staff-payment"
            :staff-payment-data="getStaffPayment"
            :validate="showErrors"
            :invalid-section="showErrors && !getMhrExemptionValidation.staffPayment"
            @update:staff-payment-data="onStaffPaymentDataUpdate($event)"
            @valid="updateValidation('staffPayment', $event)"
          />
        </v-card>
      </section>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useStore } from '../../src/store/store'
import { storeToRefs } from 'pinia'
import { RouteNames } from '../../src/enums'
import type { PartyIF } from '../../src/interfaces'
import { ExemptionPartyFormSchema } from '../../src/schemas'
import {
  attentionExemptionConfig,
  exCertifyInfoContent,
  exConfirmRequirements,
  exConfirmRequirementsQs,
  nonResExConfirmRequirements
} from '../../src/resources'
import { ConfirmCompletion } from '../../src/components/mhrTransfers'
import { ListRequirements } from '../../src/components/userAccess/ReviewConfirm'
import { PartySearch } from '../../src/components/parties/party'
import {
  AccountInfo,
  Attention,
  CertifyInformation,
  FolioOrReferenceNumber,
  FormCard,
  PartyForm,
  ReviewCard,
  LienAlert,
  StaffPayment
} from '../../src/components/common'
import { useExemptions, usePayment } from '../../src/composables'
import { parseSubmittingPartyToAccountInfo, yyyyMmDdToPacificDate } from '../../src/utils'
import { TransportPermitDetails } from '../../src/components/mhrTransportPermit'
import CautionBox from '../../src/components/common/CautionBox.vue'

export default defineComponent({
  name: 'ExemptionReview',
  components: {
    FolioOrReferenceNumber,
    AccountInfo,
    PartySearch,
    Attention,
    CertifyInformation,
    ConfirmCompletion,
    FormCard,
    ListRequirements,
    PartyForm,
    ReviewCard,
    StaffPayment,
    LienAlert,
    TransportPermitDetails,
    CautionBox
  },
  props: { showErrors: { type: Boolean, default: false } },
  setup () {
    const {
      setMhrExemptionValue
    } = useStore()
    const {
      getCertifyInformation,
      getMhrExemption,
      getMhrExemptionNote,
      getMhrExemptionValidation,
      getStaffPayment,
      isRoleStaffReg,
      isRoleQualifiedSupplier,
      hasLien,
      getMhrGenerateDocId
    } = storeToRefs(useStore())
    const {
      exemptionLabel,
      isNonResExemption,
      updateValidation,
      isExemptionWithActiveTransportPermit
    } = useExemptions()
    const { onStaffPaymentDataUpdate } = usePayment()

    const localState = reactive({
      nonResidentialDisplayReason: computed((): string => {
        const reason = getMhrExemptionNote.value?.nonResidentialReason === 'Other'
          ? `${getMhrExemptionNote.value?.nonResidentialOther || '(Not Entered)'}`
          : getMhrExemptionNote.value?.nonResidentialReason
        return`Reason for the Non-Residential Exemption: ${getMhrExemptionNote.value?.nonResidentialOption} - ${reason}`
      }),
      reviewContent: computed(() => {
        return [
          (getMhrExemption.value?.documentId || getMhrGenerateDocId.value)
            ? { label: 'Document ID', property: getMhrExemption.value?.documentId ||
                'Generate a Document ID Number upon filing' }
            : null,
          getMhrExemptionNote.value?.nonResidentialReason
            ? { label: 'Declaration Details', property: localState.nonResidentialDisplayReason }
            : null,
          getMhrExemptionNote.value?.nonResidentialOption
            ? {
                label: `Date Home was ${getMhrExemptionNote.value?.nonResidentialOption}`,
                property: yyyyMmDdToPacificDate(getMhrExemptionNote.value?.expiryDateTime, true)
              }
            : null,
          getMhrExemptionNote.value?.documentId
            ? { label: 'Document ID', property: getMhrExemption.value?.documentId }
            : null,
          { label: 'Remarks', property: getMhrExemption.value?.note?.remarks }
        ].filter(Boolean)
      }),
      showIncompleteError: computed(() => {
        const staffReview = !getMhrExemptionValidation.value?.documentId || !getMhrExemptionValidation.value?.remarks
        const nonResReview = !getMhrExemptionNote.value?.expiryDateTime ||
          !getMhrExemptionNote.value?.nonResidentialReason
        return isNonResExemption.value ? staffReview || nonResReview : staffReview
      })
    })

    /** Populate store with data from Party Search **/
    const handlePartySelect = async (party: PartyIF): Promise<void> => {
      const partyState: PartyIF = {
        personName: {
          first: party.personName.first,
          last: party.personName.last,
          middle: party.personName.middle
        },
        businessName: party.businessName,
        address: party.address,
        emailAddress: party.emailAddress,
        phoneNumber: party.contact.phoneNumber ? `${party.contact.areaCode}${party.contact.phoneNumber}` : '',
        phoneExtension: ''
      }
      setMhrExemptionValue({ key: 'submittingParty', value: partyState })
    }

    const handleValueUpdate = (key: string, value: string): void => {
      setMhrExemptionValue({ key, value })
    }

    return {
      RouteNames,
      exemptionLabel,
      isRoleStaffReg,
      isNonResExemption,
      isRoleQualifiedSupplier,
      getStaffPayment,
      getMhrExemption,
      getCertifyInformation,
      updateValidation,
      handleValueUpdate,
      handlePartySelect,
      ExemptionPartyFormSchema,
      exCertifyInfoContent,
      exConfirmRequirements,
      exConfirmRequirementsQs,
      nonResExConfirmRequirements,
      onStaffPaymentDataUpdate,
      getMhrExemptionValidation,
      parseSubmittingPartyToAccountInfo,
      attentionExemptionConfig,
      hasLien,
      isExemptionWithActiveTransportPermit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '../../src/assets/styles/theme';

.hint-message{
  font-size: 16px !important;
}

.void-transport-permit-details-review {
  border-radius: 4px;
  border: 1px solid $gray3;
}
</style>
