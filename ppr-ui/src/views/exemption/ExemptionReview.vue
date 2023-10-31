<template>
  <section
    id="exemption-review"
    aria-label="exemption-review"
  >
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
      :show-incomplete="!getMhrExemptionValidation.documentId || !getMhrExemptionValidation.remarks"
      :review-properties="reviewContent"
      :return-to-routes="[RouteNames.RESIDENTIAL_EXEMPTION, RouteNames.EXEMPTION_DETAILS]"
    >
      <template #headerSlot>
        <header class="review-header">
          <img
            alt="exemption-icon"
            class="ml-0 icon-large"
            src="@/assets/svgs/ic_exemption.svg"
          >
          <label class="font-weight-bold pl-2">Residential Exemption</label>
        </header>
      </template>
    </ReviewCard>

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
          @selectItem="handlePartySelect"
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
              @isValid="updateValidation('submittingParty', $event)"
            />
          </template>
        </FormCard>
      </section>

      <!-- Attention -->
      <section class="mt-13">
        <Attention
          section-id="mhr-exemption-attention"
          :validate="showErrors && !getMhrExemptionValidation.attention"
          :config-override="attentionExemptionConfig"
          @setStoreProperty="handleValueUpdate('attentionReference', $event)"
          @isAttentionValid="updateValidation('attention', $event)"
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
          @setStoreProperty="handleValueUpdate('clientReferenceId', $event)"
          @isFolioOrRefNumValid="updateValidation('folio', $event)"
        />
      </section>

      <!-- Confirm Requirements -->
      <section class="mt-13">
        <ConfirmCompletion
          :legal-name="getCertifyInformation.legalName"
          :set-show-errors="showErrors && !getMhrExemptionValidation.confirmCompletion"
          @confirmCompletion="updateValidation('confirmCompletion', $event)"
        >
          <template #contentSlot>
            <ListRequirements
              :requirements="isRoleStaffReg ? exConfirmRequirements : exConfirmRequirementsQs"
            />
            <p class="mt-4 ml-9 hint-message">
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
          @certifyValid="updateValidation('authorization', $event)"
        />
      </section>

      <!-- Staff Payment -->
      <section
        v-if="isRoleStaffReg"
        class="mt-13"
      >
        <h2>Staff Payment</h2>
        <v-card
          flat
          class="mt-4 pa-8"
          :class="{ 'border-error-left': !getMhrExemptionValidation.staffPayment }"
        >
          <StaffPayment
            id="staff-payment"
            :staff-payment-data="getStaffPayment"
            :validate="showErrors"
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
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { RouteNames } from '@/enums'
import { PartyIF } from '@/interfaces'
import { ExemptionPartyFormSchema } from '@/schemas'
import {
  attentionExemptionConfig,
  exCertifyInfoContent,
  exConfirmRequirements,
  exConfirmRequirementsQs
} from '@/resources'
import { ConfirmCompletion } from '@/components/mhrTransfers'
import { ListRequirements } from '@/components/userAccess/ReviewConfirm'
import { PartySearch } from '@/components/parties/party'
import {
  AccountInfo,
  Attention,
  CertifyInformation,
  FolioOrReferenceNumber,
  FormCard,
  PartyForm,
  ReviewCard,
  StaffPayment
} from '@/components/common'
import { useExemptions, usePayment } from '@/composables'
import { parseSubmittingPartyToAccountInfo } from '@/utils'

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
    StaffPayment
  },
  props: { showErrors: { type: Boolean, default: false } },
  setup () {
    const {
      setMhrExemptionValue
    } = useStore()
    const {
      getCertifyInformation,
      getMhrExemption,
      getMhrExemptionValidation,
      getStaffPayment,
      isRoleStaffReg,
      isRoleQualifiedSupplier
    } = storeToRefs(useStore())
    const { updateValidation } = useExemptions()
    const { onStaffPaymentDataUpdate } = usePayment()

    const localState = reactive({
      reviewContent: computed(() => {
        return [
          getMhrExemption.value?.documentId
            ? { label: 'Document ID', property: getMhrExemption.value?.documentId }
            : null,
          { label: 'Remarks', property: getMhrExemption.value?.note?.remarks }
        ].filter(Boolean)
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
      isRoleStaffReg,
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
      onStaffPaymentDataUpdate,
      getMhrExemptionValidation,
      parseSubmittingPartyToAccountInfo,
      attentionExemptionConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.hint-message{
  font-size: 16px !important;
}
</style>
