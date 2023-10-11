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
      :showIncomplete="false"
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

        <FormCard
          label="Add Submitting party"
          :showErrors="false"
          :class="{'border-error-left': false}"
        >
          <template v-slot:formSlot>
            <PartyForm
              ref=""
              :baseParty="getMhrExemption.submittingParty"
              :schema="PartyFormSchema"
              :orgLookupConfig="null"
              @isValid="null"
            >
            </PartyForm>
          </template>
        </FormCard>
      </section>

      <!-- Attention -->
      <section class="mt-13">
        <Attention
          sectionId="mhr-exemption-attention"
        />
      </section>

      <!-- Confirm Requirements -->
      <section class="mt-13">
        <ConfirmCompletion
          :legalName="getCertifyInformation.legalName"
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
        />
      </section>

      <!-- Authorization -->
      <section class="mt-13">
        <h2>Staff Payment</h2>
        <v-card flat class="mt-4 pa-8" :class="{ 'border-error-left': false }">
          <StaffPayment
            id="staff-payment"
            :displaySideLabel="true"
            :displayPriorityCheckbox="true"
            :staffPaymentData="staffPayment"
            :invalidSection="false"
            :validate="false"
            @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
          />
        </v-card>
      </section>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { Attention, CertifyInformation, FormCard, PartyForm, ReviewCard } from '@/components/common'
import { PartyFormSchema } from '@/schemas'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { RouteNames } from '@/enums'
import { ConfirmCompletion } from '@/components/mhrTransfers'
import { ListRequirements } from '@/components/userAccess/ReviewConfirm'
import { exConfirmRequirements, exCertifyInfoContent } from '@/resources'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'

export default defineComponent({
  name: 'ExemptionReview',
  components: {
    Attention,
    CertifyInformation,
    ConfirmCompletion,
    FormCard,
    ListRequirements,
    PartyForm,
    ReviewCard,
    StaffPayment
  },
  props: {
    showErrors: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const { setStaffPayment } = useStore()
    const { getCertifyInformation, getMhrExemption, isRoleStaffReg } = storeToRefs(useStore())
    const localState = reactive({
      staffPaymentValid: false,
      staffPayment: {
        option: StaffPaymentOptions.NONE,
        routingSlipNumber: '',
        bcolAccountNumber: '',
        datNumber: '',
        folioNumber: '',
        isPriority: false
      },
      reviewContent: computed(() => {
        return [
          isRoleStaffReg.value ? { label: 'Document ID', property: getMhrExemption.value?.documentId } : null,
          { label: 'Remarks', property: getMhrExemption.value?.note?.remarks }
        ]
      })
    })

    /** Called when component's staff payment data has been updated. */
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
          localState.staffPaymentValid = false
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
          localState.staffPaymentValid = false
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
          localState.staffPaymentValid = true
          break
        case StaffPaymentOptions.NONE: // should never happen
          break
      }

      localState.staffPayment = staffPaymentData
      setStaffPayment(staffPaymentData)
    }

    return {
      RouteNames,
      isRoleStaffReg,
      getMhrExemption,
      getCertifyInformation,
      PartyFormSchema,
      exCertifyInfoContent,
      exConfirmRequirements,
      onStaffPaymentDataUpdate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
