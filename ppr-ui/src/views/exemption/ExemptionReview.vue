<template>
  <section id="exemption-review" aria-label="exemption-review">
    <v-row no-gutters class="soft-corners-top">
      <v-col class="role" cols="auto" aria-label="exemption-review-help">
        <h2 class="mt-10">Review and Confirm</h2>
        <p class="mt-1">
          Review the information in your exemption and complete the additional information below. If you need to change
          anything, return to the previous step to make the necessary change.
        </p>
      </v-col>
    </v-row>

    <!-- Exemption Content Review -->
    <ReviewCard
      class="mt-5"
      :showIncomplete="!getMhrExemptionValidation.documentId || !getMhrExemptionValidation.remarks"
      :reviewProperties="reviewContent"
      :returnToRoutes="[RouteNames.RESIDENTIAL_EXEMPTION, RouteNames.EXEMPTION_DETAILS]"
    >
      <template #headerSlot>
        <header class="review-header">
          <img alt="exemption-icon" class="ml-0 icon-large" src="@/assets/svgs/ic_exemption.svg" />
          <label class="font-weight-bold pl-2">Residential Exemption</label>
        </header>
      </template>
    </ReviewCard>

    <div class="increment-sections mt-13" :class="{ 'increment-sections' : isRoleStaffReg }">
      <!-- Submitting Party -->
      <section>
        <h2>Submitting Party</h2>
        <p>Provide the name and contact information for the person or business submitting this exemption. You can add
          the submitting party information manually, or, if the submitting party has a Personal Property Registry party
          code, you can look up the party code or name.</p>

        <PartySearch
          isMhrPartySearch
          class="mb-8 rounded-all"
          @selectItem="handlePartySelect"
        />

        <FormCard
          label="Add Submitting party"
          :showErrors="showErrors && !getMhrExemptionValidation.submittingParty"
          :class="{ 'border-error-left': showErrors && !getMhrExemptionValidation.submittingParty }"
        >
          <template v-slot:formSlot>
            <PartyForm
              ref="exemptions-submitting-party"
              :baseParty="getMhrExemption.submittingParty"
              :schema="ExemptionPartyFormSchema"
              :showErrors="showErrors && !getMhrExemptionValidation.submittingParty"
              @isValid="updateValidation('submittingParty', $event)"
            >
            </PartyForm>
          </template>
        </FormCard>
      </section>

      <!-- Attention -->
      <section class="mt-13">
        <Attention
          sectionId="mhr-exemption-attention"
          :validate="showErrors && !getMhrExemptionValidation.attention"
          @setStoreProperty="handleValueUpdate('attentionReference', $event)"
          @isAttentionValid="updateValidation('attention', $event)"
        />
      </section>

      <!-- Confirm Requirements -->
      <section class="mt-13">
        <ConfirmCompletion
          :legalName="getCertifyInformation.legalName"
          :setShowErrors="showErrors && !getMhrExemptionValidation.confirmCompletion"
          @confirmCompletion="updateValidation('confirmCompletion', $event)"
        >
          <template #contentSlot>
            <ListRequirements
              :requirements="exConfirmRequirements"
            />
          </template>
        </ConfirmCompletion>
      </section>

      <!-- Authorization -->
      <section class="mt-13">
        <CertifyInformation
          :content="exCertifyInfoContent"
          :setShowErrors="showErrors && !getMhrExemptionValidation.authorization"
          @certifyValid="updateValidation('authorization', $event)"
        />
      </section>

      <!-- Authorization -->
      <section class="mt-13">
        <h2>Staff Payment</h2>
        <v-card flat class="mt-4 pa-8" :class="{ 'border-error-left': !getMhrExemptionValidation.staffPayment }">

          <StaffPayment
            id="staff-payment"
            :staffPaymentData="getStaffPayment"
            :validate="showErrors"
            @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
            @valid="updateValidation('staffPayment', $event)"
          />
        </v-card>
      </section>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { RouteNames } from '@/enums'
import { PartyIF } from '@/interfaces'
import { ExemptionPartyFormSchema } from '@/schemas'
import { exConfirmRequirements, exCertifyInfoContent } from '@/resources'
import { ConfirmCompletion } from '@/components/mhrTransfers'
import { ListRequirements } from '@/components/userAccess/ReviewConfirm'
import { PartySearch } from '@/components/parties/party'
import { Attention, CertifyInformation, FormCard, PartyForm, ReviewCard } from '@/components/common'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import { useExemptions, usePayment } from '@/composables'

export default defineComponent({
  name: 'ExemptionReview',
  components: {
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
      isRoleStaffReg
    } = storeToRefs(useStore())
    const { updateValidation } = useExemptions()
    const { onStaffPaymentDataUpdate } = usePayment()

    const localState = reactive({
      reviewContent: computed(() => {
        return [
          (isRoleStaffReg.value && getMhrExemption.value?.documentId)
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
      getStaffPayment,
      getMhrExemption,
      getCertifyInformation,
      updateValidation,
      handleValueUpdate,
      handlePartySelect,
      ExemptionPartyFormSchema,
      exCertifyInfoContent,
      exConfirmRequirements,
      onStaffPaymentDataUpdate,
      getMhrExemptionValidation,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
