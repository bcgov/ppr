<template>
  <div id="mhr-review-confirm">
    <!-- Review and Confirm -->
    <div class="mt-10">
      <h2>Review and Confirm</h2>
      <p class="mt-4">
        Review the information in your registration and complete the additional information below. If you need to
        change anything, return to the previous step to make the necessary change.
      </p>

      <!-- Your Home Summary -->
      <YourHomeReview />

      <!-- Submitting Party Review -->
      <SubmittingPartyReview />

      <!-- Home Owners Review -->
      <HomeOwnersReview />

      <!-- Home Location Review -->
      <HomeLocationReview />
    </div>

    <!-- Authorization -->
    <section id="mh-certify-section" class="mt-10 pt-4">
      <CertifyInformation
        isMhr
        :setShowErrors="validateAuthorization"
        @certifyValid="authorizationValid = $event"
      />
    </section>

    <!-- Staff Payment -->
    <section id="mhr-staff-payment-section" class="mt-10" v-if="isRoleStaffReg">
      <h2>
        2. Staff Payment
      </h2>
      <v-card flat class="mt-6 pa-6" :class="{ 'border-error-left': validateStaffPayment }">
        <StaffPayment
          id="staff-payment"
          :staffPaymentData="staffPayment"
          :validate="isValidatingApp"
          :displaySideLabel="true"
          :displayPriorityCheckbox="true"
          :invalidSection="validateStaffPayment"
          @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
          @valid="staffPaymentValid = $event"
        />
      </v-card>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import {
  HomeLocationReview,
  HomeOwnersReview,
  SubmittingPartyReview,
  YourHomeReview
} from '@/components/mhrRegistration/ReviewConfirm'
import { CertifyInformation } from '@/components/common'
import { useMhrValidations } from '@/composables'
import { RouteNames } from '@/enums'
import { useActions, useGetters } from 'vuex-composition-helpers'
/* eslint-disable no-unused-vars */
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
/* eslint-enable no-unused-vars */

/* eslint-disable */
export default defineComponent({
  name: 'MhrReviewConfirm',
  components: {
    YourHomeReview,
    SubmittingPartyReview,
    HomeOwnersReview,
    HomeLocationReview,
    CertifyInformation,
    StaffPayment
  },
  props: {},
  setup (props, context) {
    const { getMhrRegistrationValidationModel, getStaffPayment, isRoleStaffReg } = useGetters<any>([
      'isRoleStaffReg',
      'getMhrRegistrationValidationModel',
      'getStaffPayment'
    ])

    const { setStaffPayment } = useActions<any>(['setStaffPayment'])

    const {
      MhrCompVal,
      MhrSectVal,
      setValidation,
      scrollToInvalid,
      getValidation,
      getStepValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      isMhr: true,
      authorizationValid: false,
      isValidatingApp: computed( (): boolean => {
        return getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP)
      }),
      validateAuthorization: computed(() => {
        return localState.isValidatingApp &&
          !getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.AUTHORIZATION_VALID)
      }),
      validateStaffPayment: computed(() => {
        return localState.isValidatingApp &&
          !getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.STAFF_PAYMENT_VALID)
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

    const onStaffPaymentDataUpdate = (val: StaffPaymentIF) => {
      let staffPaymentData: StaffPaymentIF = {
        ...val
      }

      if (staffPaymentData.routingSlipNumber || staffPaymentData.bcolAccountNumber || staffPaymentData.datNumber) {
        localState.staffPaymentValid = true
      } else {
        if (staffPaymentData.option !== localState.paymentOption) {
          localState.staffPaymentValid = false
          localState.paymentOption = staffPaymentData.option
        }
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
      (val: boolean) => {
        setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.STAFF_PAYMENT_VALID, val)
      }
    )

    watch(() => context.root.$route.name, (route: string) => {
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
          localState.isValidatingApp &&
          scrollToInvalid(MhrSectVal.REVIEW_CONFIRM_VALID, 'mhr-review-confirm',
            [
              getStepValidation(MhrSectVal.YOUR_HOME_VALID),
              getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID),
              getStepValidation(MhrSectVal.HOME_OWNERS_VALID),
              getStepValidation(MhrSectVal.LOCATION_VALID)
            ])
          setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS, true)
          break
      }
    })

    return {
      isRoleStaffReg,
      onStaffPaymentDataUpdate,
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
</style>
