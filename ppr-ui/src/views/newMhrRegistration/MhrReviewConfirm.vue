<template>
  <div
    id="mhr-review-confirm"
    class="mt-10"
  >
    <!-- Review and Confirm -->
    <h2>Review and Confirm</h2>
    <p class="mt-4">
      Review the information in your registration and complete the additional information below. If you need to
      change anything, return to the previous step to make the necessary change.
    </p>

    <!-- Mhr Corrections only -->
    <template v-if="displayMhrStatusCorrectionMsg">
      <CautionBox
        class="mt-8"
        :setMsg="mhrStatusCorrectionMsg"
      />
    </template>

    <!-- Information for manufacturers registration only -->
    <template v-if="isMhrManufacturerRegistration">
      <p class="mt-3 mb-6">
        <b>Note: </b>
        Home Owner and Location of Home information is based on the original information you provided in your
        Qualified Suppliers' Agreement and cannot be changed here. If you wish to update this information please
        contact BC Registries.
      </p>

      <ContactUsToggle
        helpText="If you require assistance with changes to your manufacturer information please contact us."
      />

      <CautionBox
        setMsg="After registering, BC Registries will mail the verification statement and registration decals
        displaying the Manufactured Home Registration Number to the Submitting Party. The registration decals
        must be affixed to the home, according to the <b>instructions on the decal envelope.</b>"
      />
    </template>

    <!-- Submitting Party Review -->
    <SubmittingPartyReview v-if="!isMhrManufacturerRegistration" />

    <!-- Your Home Summary -->
    <YourHomeReview />

    <!-- Home Owners Review -->
    <HomeOwnersReview />

    <!-- Home Location Review -->
    <HomeLocationReview :isCorrectionReview="isMhrCorrection" />

    <div id="mhr-review-confirm-components">
      <template v-if="isMhrManufacturerRegistration">
        <!-- Submitting Party based on Account-->
        <AccountInfo
          v-if="accountInfo"
          class="mt-15"
          title="Submitting Party for this Registration"
          desc="Registration verification statement and decals will be mailed to this address."
          :tooltipContent="'The default Submitting Party is based on your BC Registries user account information. ' +
            'This information can be updated within your account settings.'"
          :accountInfo="accountInfo"
        />

        <!-- Attention -->
        <section
          id="mhr-review-confirm-attention"
          class="mt-15"
        >
          <Attention
            sectionId="mhr-review-confirm-attention"
            :initialValue="getMhrAttentionReference"
            :sectionNumber="1"
            :validate="isValidatingApp"
            @isAttentionValid="setAttentionValidation"
            @setStoreProperty="setMhrAttentionReference"
          />
        </section>

        <!-- Folio or Reference Number -->
        <section
          id="mhr-folio-or-reference-number"
          class="mt-15"
        >
          <FolioOrReferenceNumber
            sectionId="mhr-folio-or-reference-number"
            :initialValue="getFolioOrReferenceNumber"
            :sectionNumber="2"
            :validate="isValidatingApp"
            @isFolioOrRefNumValid="setFolioOrReferenceNumberValidation"
            @setStoreProperty="setFolioOrReferenceNumber"
          />
        </section>
      </template>

      <!-- Authorization -->
      <section
        id="mhr-certify-section"
        class="mt-15"
      >
        <CertifyInformation
          :sectionNumber="isMhrManufacturerRegistration ? 3 : 1"
          :setShowErrors="validateAuthorization"
          @certifyValid="authorizationValid = $event"
        />
      </section>

      <!-- Staff Payment -->
      <section
        v-if="isRoleStaffReg || isRoleStaffSbc"
        id="mhr-staff-payment-section"
        class="mt-15"
      >
        <h2>
          2. Staff Payment
        </h2>
        <v-card
          flat
          class="mt-6 pa-6"
          :class="{ 'border-error-left': validateStaffPayment }"
        >
          <StaffPayment
            id="staff-payment"
            :displaySideLabel="true"
            :displayPriorityCheckbox="true"
            :staffPaymentData="staffPayment"
            :invalidSection="validateStaffPayment"
            :validate="hasStaffPaymentValues || isValidatingApp"
            @update:staff-payment-data="onStaffPaymentDataUpdate($event)"
            @valid="staffPaymentValid = $event"
          />
        </v-card>
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import {
  StaffPayment,
  AccountInfo,
  Attention,
  CertifyInformation,
  ContactUsToggle,
  CautionBox,
  FolioOrReferenceNumber
} from '@/components/common'
import {
  HomeLocationReview,
  HomeOwnersReview,
  SubmittingPartyReview,
  YourHomeReview
} from '@/components/mhrRegistration/ReviewConfirm'
import { useMhrCorrections, useMhrValidations } from '@/composables'
import { MhApiStatusTypes, RouteNames, StaffPaymentOptions } from '@/enums'

import { StaffPaymentIF } from '@/interfaces'
import { useHomeOwners } from '@/composables/mhrRegistration'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { AccountInfoIF, StepIF } from '@/interfaces'
import {
  deepChangesComparison,
  getAccountInfoFromAuth,
  parseAccountToSubmittingParty
} from '@/utils'

export default defineComponent({
  name: 'MhrReviewConfirm',
  components: {
    YourHomeReview,
    SubmittingPartyReview,
    HomeOwnersReview,
    HomeLocationReview,
    AccountInfo,
    Attention,
    FolioOrReferenceNumber,
    CertifyInformation,
    StaffPayment,
    ContactUsToggle,
    CautionBox
},
  setup () {
    const {
      setStaffPayment,
      setMhrAttentionReference,
      setFolioOrReferenceNumber,
      setMhrRegistrationSubmittingParty
    } = useStore()
    const {
      getFolioOrReferenceNumber,
      getMhrAttentionReference,
      getMhrRegistrationValidationModel,
      isRoleStaffSbc,
      isRoleStaffReg,
      getMhrSteps,
      getMhrBaseline,
      getMhrStatusType,
      isMhrManufacturerRegistration
    } = storeToRefs(useStore())
    const route = useRoute()
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation,
      scrollToInvalid,
      scrollToInvalidReviewConfirm,
      getValidation,
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const { setShowGroups, isGlobalEditingMode } = useHomeOwners()
    const { isMhrCorrection } = useMhrCorrections()

    const localState = reactive({
      authorizationValid: false,
      accountInfo: null as AccountInfoIF | null,
      isValidatingApp: computed( (): boolean => {
        return getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP)
      }),
      validateAuthorization: computed(() => {
        return localState.isValidatingApp &&
          !getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.AUTHORIZATION_VALID)
      }),
      validateStaffPayment: computed(() => {
        return isRoleStaffReg && localState.isValidatingApp &&
          !getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.STAFF_PAYMENT_VALID)
      }),
      hasStaffPaymentValues: computed(() => {
        switch (localState.staffPayment.option) {
          case StaffPaymentOptions.BCOL:
            return !!localState.staffPayment.bcolAccountNumber
          case StaffPaymentOptions.FAS:
            return !!localState.staffPayment.routingSlipNumber
          case StaffPaymentOptions.NO_FEE:
          case StaffPaymentOptions.NONE:
            return true
          default:
            return false
        }
      }),
      displayMhrStatusCorrectionMsg: computed((): boolean => {
        return isMhrCorrection.value &&
          deepChangesComparison(getMhrBaseline.value?.statusType, getMhrStatusType.value)
      }),
      mhrStatusCorrectionMsg: computed((): string => {
        return getMhrStatusType.value === MhApiStatusTypes.EXEMPT
          ? `Registration status for this home was changed to <b>Exempt</b>. This will be effective after registering
             this correction.`
          : `Registration status for this home was changed to <b>Active</b>. If applicable, any Exemption Orders on
             this home will be cancelled and Exemption Unit Notes removed from search results. This will be effective
             after registering this correction.`
      }),
      paymentOption: StaffPaymentOptions.NONE,
      staffPaymentValid: false,
      staffPayment: {
        option: StaffPaymentOptions.NONE,
        routingSlipNumber: '',
        bcolAccountNumber: '',
        datNumber: '',
        folioNumber: '',
        isPriority: false
      }
    })

    onBeforeMount(async () => {
      if (isMhrManufacturerRegistration.value) {
        localState.accountInfo = await getAccountInfoFromAuth()
        setMhrRegistrationSubmittingParty(parseAccountToSubmittingParty(localState.accountInfo))
      }
    })

    const setAttentionValidation = (val : boolean) => {
      setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.ATTENTION_VALID, val)
    }

    const setFolioOrReferenceNumberValidation = (val : boolean) => {
      setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.REF_NUM_VALID, val)
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

    watch(
      () => localState.authorizationValid,
      (val: boolean) => {
        setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.AUTHORIZATION_VALID, val)
      }
    )

    watch(
      () => localState.staffPaymentValid,
      async (val: boolean) => {
        await setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.STAFF_PAYMENT_VALID, val)
      }
    )

    watch(() => route.name, () => {
      switch (route.name) {
        case RouteNames.SUBMITTING_PARTY:
          localState.isValidatingApp &&
          scrollToInvalid(MhrSectVal.SUBMITTING_PARTY_VALID, 'mhr-submitting-party')
          break
        case RouteNames.YOUR_HOME:
          localState.isValidatingApp &&
          scrollToInvalid(MhrSectVal.YOUR_HOME_VALID, 'mhr-describe-your-home')
          break
        case RouteNames.HOME_OWNERS:
          localState.isValidatingApp &&
          scrollToInvalid(MhrSectVal.HOME_OWNERS_VALID, 'mhr-home-owners-list')
          break
        case RouteNames.HOME_LOCATION:
          localState.isValidatingApp &&
          scrollToInvalid(MhrSectVal.LOCATION_VALID, 'mhr-home-location')
          break
        case RouteNames.MHR_REVIEW_CONFIRM:
          const stepsValidation = getMhrSteps.value.map((step : StepIF) => step.valid)
          stepsValidation.pop() // Removes review confirm step from stepsValidation
          localState.isValidatingApp &&
          scrollToInvalidReviewConfirm(stepsValidation)
          // Only set reviewed if add/edit form was open when review reached
          if (isGlobalEditingMode.value) {
            setValidation(MhrSectVal.ADD_EDIT_OWNERS_VALID, MhrCompVal.OWNERS_VALID, false)
          }
          setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS, true)
          break
      }
    })

    return {
      setShowGroups,
      isRoleStaffSbc,
      isMhrCorrection,
      getFolioOrReferenceNumber,
      getMhrAttentionReference,
      isMhrManufacturerRegistration,
      isRoleStaffReg,
      onStaffPaymentDataUpdate,
      setAttentionValidation,
      setFolioOrReferenceNumber,
      setMhrAttentionReference,
      setFolioOrReferenceNumberValidation,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#mhr-staff-payment-section {
  :deep(.theme--light.v-text-field.v-input--is-disabled .v-input__slot::before) {
    border-style: dashed;
  }
  :deep(.theme--light.v-label--is-disabled) {
    color: $gray7;
  }
}

:deep(#home-owners-summary) {
  .readonly-home-owners-table {
    border-left: 0 !important;
  }
}
</style>
