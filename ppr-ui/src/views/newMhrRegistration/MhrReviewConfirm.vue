<template>
  <div id="mhr-review-confirm" class="mt-10">
    <!-- Review and Confirm -->
    <h2>Review and Confirm</h2>
    <p class="mt-4">
      Review the information in your registration and complete the additional information below. If you need to
      change anything, return to the previous step to make the necessary change.
    </p>

    <!-- Information for manufacturers registration only -->
    <template v-if="isMhrManufacturerRegistration">

      <p class="mt-3 mb-6">
        <b>Note: </b>
        Submitting Party, Home Owner and Location of Home information is based on your manufacturer information
        and cannot be changed here. If you wish to update this information please contact BC Registries.
      </p>

      <ContactUsToggle
        helpText="If you require assistance with changes to your manufacturer information please contact us."
      />

      <CautionBox
        setMsg="After registering, the verification statement and decals will be sent to the Submitting Party."
      />

    </template>

    <!-- Your Home Summary -->
    <YourHomeReview />

    <!-- Submitting Party Review -->
    <SubmittingPartyReview v-if="!isMhrManufacturerRegistration"/>

    <!-- Home Owners Review -->
    <HomeOwnersReview />

    <!-- Home Location Review -->
    <HomeLocationReview />

    <div id="mhr-review-confirm-components">
      <template  v-if="isMhrManufacturerRegistration">
        <!-- Submitting Party based on Account-->
        <AccountInfo
          class="mt-15"
          title="Submtting Party for this Registration"
          :tooltipContent="'The default Submitting Party is based on your BC Registries user account information. ' +
                            'This information can be updated within your account settings.'"
          :accountInfo="accountInfo"
        />

        <!-- Attention -->
        <section id="mhr-review-confirm-attention" class="mt-15">
          <Attention
            sectionId="mhr-review-confirm-attention"
            :intialValue="getMhrAttentionReference"
            :sectionNumber="1"
            :validate="isValidatingApp"
            @isAttentionValid="setAttentionValidation"
            @setStoreProperty="setMhrAttentionReference"
          />
        </section>

        <!-- Folio or Reference Number -->
        <section id="mhr-folio-or-reference-number" class="mt-15">
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
      <section id="mhr-certify-section" class="mt-15">
        <CertifyInformation
          :sectionNumber="isMhrManufacturerRegistration ? 3 : 1"
          :setShowErrors="validateAuthorization"
          @certifyValid="authorizationValid = $event"
        />
      </section>

      <!-- Staff Payment -->
      <section id="mhr-staff-payment-section" class="mt-15" v-if="isRoleStaffReg">
        <h2>
          2. Staff Payment
        </h2>
        <v-card flat class="mt-6 pa-6" :class="{ 'border-error-left': validateStaffPayment }">
          <StaffPayment
            id="staff-payment"
            :displaySideLabel="true"
            :displayPriorityCheckbox="true"
            :staffPaymentData="staffPayment"
            :invalidSection="validateStaffPayment"
            :validate="hasStaffPaymentValues || isValidatingApp"
            @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
            @valid="staffPaymentValid = $event"
          />
        </v-card>
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import {
  HomeLocationReview,
  HomeOwnersReview,
  SubmittingPartyReview,
  YourHomeReview
} from '@/components/mhrRegistration/ReviewConfirm'
import {
  AccountInfo,
  Attention,
  CertifyInformation,
  ContactUsToggle,
  CautionBox,
  FolioOrReferenceNumber
} from '@/components/common'
import { useMhrValidations } from '@/composables'
import { RouteNames } from '@/enums'
/* eslint-disable no-unused-vars */
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import { useHomeOwners } from '@/composables/mhrRegistration'
import { useRoute } from 'vue2-helpers/vue-router'
import { storeToRefs } from 'pinia'
import { AccountInfoIF, StepIF } from '@/interfaces'
import { getAccountInfoFromAuth, parseAccountToSubmittingParty } from '@/utils'
/* eslint-enable no-unused-vars */

/* eslint-disable */
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
      isRoleStaffReg,
      getMhrSteps,
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
        }
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

    watch(() => route.name, (route: string) => {
      switch (route) {
        case RouteNames.YOUR_HOME:
          scrollToInvalid(MhrSectVal.YOUR_HOME_VALID, 'mhr-describe-your-home')
          break
        case RouteNames.SUBMITTING_PARTY:
          scrollToInvalid(MhrSectVal.SUBMITTING_PARTY_VALID, 'mhr-submitting-party')
          break
        case RouteNames.HOME_OWNERS:
          scrollToInvalid(MhrSectVal.HOME_OWNERS_VALID, 'mhr-home-owners-list')
          break
        case RouteNames.HOME_LOCATION:
          scrollToInvalid(MhrSectVal.LOCATION_VALID, 'mhr-home-location')
          break
        case RouteNames.MHR_REVIEW_CONFIRM:
          let stepsValidation = getMhrSteps.value.map((step : StepIF) => step.valid)
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
  ::v-deep {
    .theme--light.v-text-field.v-input--is-disabled .v-input__slot::before {
      border-style: dashed;
    }
    .theme--light.v-label--is-disabled {
      color: $gray7;
    }
  }
}

#home-owners-summary ::v-deep {
  .readonly-home-owners-table {
    border-left: 0 !important;
  }
}
</style>
