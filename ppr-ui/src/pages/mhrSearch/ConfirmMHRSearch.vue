<template>
  <v-container
    id="confirm-mhr-search"
    class="py-14"
  >
    <v-overlay
      v-model="submitting"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="30"
        indeterminate
      />
    </v-overlay>
    <BaseDialog
      set-attach="#confirm-mhr-search"
      :set-options="options"
      :set-display="showCancelDialog"
      @proceed="handleDialogResp"
    />
    <div
      v-if="dataLoaded && !dataLoadError"
      class="container pa-0"
    >
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Review Selection(s)</h1>
          <div class="mt-6">
            <p class="ma-0">
              Review the selected manufactured home registration(s) before paying. Your search result will be available
              in your Searches list for up to 14 days. <b>Note : Search fees are charged per unique manufactured home
                registration number.</b>
            </p>
          </div>

          <v-card
            flat
            class="mt-6"
          >
            <header class="review-header">
              <v-icon color="darkBlue">
                mdi-home
              </v-icon>
              <label class="font-weight-bold pl-2">
                Selection Summary
              </label>
            </header>
            <SearchedResultsMhr
              class="px-1"
              :is-review-mode="true"
            />
          </v-card>

          <FolioNumberSummary
            :set-show-errors="showErrors"
            :set-is-mhr="true"
            class="pt-15"
            @folio-valid="setFolioValid"
          />

          <!-- Staff Payment Section -->
          <section
            v-if="getIsStaffClientPayment && !isRoleStaffSbc"
            class="mt-10"
          >
            <v-row no-gutters>
              <v-col class="generic-label">
                <h2>2. Staff Payment</h2>
              </v-col>
            </v-row>

            <v-card
              flat
              class="mt-6 pa-6"
              :class="showErrorAlert ? 'border-error-left' : ''"
            >
              <StaffPayment
                id="staff-payment-dialog"
                :staff-payment-data="staffPaymentData"
                :validate="validating||showErrors"
                :display-side-label="true"
                :display-priority-checkbox="true"
                :invalid-section="showErrorAlert"
                @update:staff-payment-data="onStaffPaymentDataUpdate($event)"
                @valid="staffPaymentValid = $event"
              >
                <template #bottom-slot>
                  <v-checkbox
                    id="certify-checkbox"
                    class="mt-n2"
                    hide-details
                    label="Make this a Certified search (add $25.00)"
                    @update:model-value="setSearchCertified"
                  />
                </template>
              </StaffPayment>
            </v-card>
          </section>
        </v-col>
        <v-col
          class="pl-6"
          cols="3"
        >
          <aside>
            <StickyContainer
              show-connect-fees
              :set-err-msg="stickyComponentErrMsg"
              :set-right-offset="true"
              :set-show-buttons="true"
              :set-show-fee-summary="true"
              :set-fee-type="feeType"
              :set-fee-quantity="feeQuantity"
              :set-back-btn="'Back'"
              :set-cancel-btn="'Cancel'"
              :set-submit-btn="'Pay and Download Result'"
              :set-additional-fees="combinedSearchFees"
              @back="goToSearchResult()"
              @cancel="showDialog()"
              @submit="submit()"
            />
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onMounted, reactive, toRefs, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { FolioNumberSummary, StaffPayment, StickyContainer } from '@/components/common'
import { ConnectPaymentMethod, ErrorCategories, RouteNames, StaffPaymentOptions, UIMHRSearchTypeValues } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { notCompleteSearchDialog } from '@/resources/dialogOptions'
import { submitSelectedMhr } from '@/utils/mhr-api-helper'
import { uniqBy } from 'lodash'

import type { DialogOptionsIF, StaffPaymentIF } from '@/interfaces'
import type { AdditionalSearchFeeIF } from '@/composables/fees/interfaces'
import { useAuth, useConnectFeesHandler, useNavigation } from '@/composables'
import { useConnectFeeStore } from '@/store/connectFee'


export default defineComponent({
  name: 'ConfirmMHRSearch',
  components: {
    FolioNumberSummary,
    StickyContainer,
    StaffPayment
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    }
  },
  emits: ['haveData', 'error'],
  setup (props, { emit }) {
    const router = useRouter()
    const { goToDash, goToPay } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { feeOptions, fees, userSelectedPaymentMethod } = storeToRefs(useConnectFeeStore())
    const { setRegistrationFees, setRegistrationComboFees, setFeeQuantity } = useConnectFeesHandler()
    const {
      // Actions
      setStaffPayment,
      setSearchCertified
    } = useStore()
    const {
      // Getters
      isRoleStaff,
      isRoleStaffReg,
      isRoleStaffSbc,
      getStaffPayment,
      isSearchCertified,
      getIsStaffClientPayment,
      getFolioOrReferenceNumber,
      getSelectedManufacturedHomes,
      getManufacturedHomeSearchResults
    } = storeToRefs(useStore())

    const localState = reactive({
      dataLoaded: false,
      dataLoadError: false,
      options: notCompleteSearchDialog as DialogOptionsIF,
      showCancelDialog: false,
      showErrors: false,
      submitting: false,
      validFolio: true,
      staffPaymentValid: false,
      validating: false,
      paymentOption: StaffPaymentOptions.NONE,
      feeType: computed(() => {
        if (isRoleStaff.value && !getIsStaffClientPayment.value) return FeeSummaryTypes.NO_FEE_SEARCH
        return isRoleStaff.value
          ? FeeSummaryTypes.GOV_STAFF_MHR_SEARCH
          : FeeSummaryTypes.MHR_SEARCH
      }),
      combinedFeeType: computed(() => {
        if (isRoleStaff.value && !getIsStaffClientPayment.value) return FeeSummaryTypes.NO_FEE_SEARCH
        return isRoleStaff.value
          ? FeeSummaryTypes.GOV_STAFF_MHR_COMBINED_SEARCH
          : FeeSummaryTypes.MHR_COMBINED_SEARCH
      }),
      showErrorAlert: computed((): boolean => {
        return (!localState.validFolio || !localState.staffPaymentValid) && localState.showErrors
      }),
      stickyComponentErrMsg: computed((): string => {
        if (localState.showErrorAlert) {
          return '< Please complete required information'
        }
        return ''
      }),
      combinedSearchFees: computed((): AdditionalSearchFeeIF => {
        const searchQuantity = uniqBy(getSelectedManufacturedHomes.value, UIMHRSearchTypeValues.MHRMHR_NUMBER)
          .filter(item => item.includeLienInfo === true)
          .length
        return searchQuantity > 0
          ? {
            feeType: localState.combinedFeeType,
            quantity: searchQuantity
          }
          : null
      }),
      feeQuantity: computed((): number => {
        // Return selected quantity that is not a combination search
        return uniqBy(getSelectedManufacturedHomes.value, UIMHRSearchTypeValues.MHRMHR_NUMBER)
          .filter(result => result.selected && !result.includeLienInfo)
          .length
      }),
      staffPaymentData: computed((): StaffPaymentIF => {
        let pd = getStaffPayment.value
        if (!pd) {
          pd = {
            option: StaffPaymentOptions.NONE,
            routingSlipNumber: '',
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: '',
            isPriority: false
          }
        }
        return pd
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
    })

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) goToDash()
    }

    const goToSearchResult = (): void => {
      router.push({
        name: RouteNames.MHRSEARCH
      })
    }

    const setFolioValid = (valid: boolean): void => {
      localState.validFolio = valid
    }

    const showDialog = (): void => {
      localState.showCancelDialog = true
    }

    const submit = async (): Promise<void> => {
      localState.validating = true
      await nextTick()
      if (!localState.validFolio || (
        (getIsStaffClientPayment.value && !isRoleStaffSbc.value) && !localState.staffPaymentValid)
      ) {
        localState.showErrors = true
        document.getElementById('staff-payment-dialog').scrollIntoView({ behavior: 'smooth' })
        return
      }
      localState.submitting = true
      let apiResponse
      if (isRoleStaffReg.value) {
        apiResponse = await submitSelectedMhr(
          getManufacturedHomeSearchResults.value.searchId,
          uniqBy(getSelectedManufacturedHomes.value, UIMHRSearchTypeValues.MHRMHR_NUMBER),
          getFolioOrReferenceNumber.value,
          getStaffPayment.value,
          isSearchCertified.value
        )
      } else {
        apiResponse = await submitSelectedMhr(
          getManufacturedHomeSearchResults.value.searchId,
          uniqBy(getSelectedManufacturedHomes.value, UIMHRSearchTypeValues.MHRMHR_NUMBER),
          getFolioOrReferenceNumber.value,
          null, null, userSelectedPaymentMethod.value === ConnectPaymentMethod.DIRECT_PAY
        )
      }
      localState.submitting = false
      if (apiResponse === undefined || apiResponse.status !== 200) {
        emit('error', { category: ErrorCategories.SEARCH })
      } else {
        // Reset the certified search checkbox after a successful response
        setSearchCertified(false)
        // On success return to dashboard
        if (apiResponse?.data.paymentPending) {
          goToPay(
            apiResponse.data.payment?.invoiceId,
            null, `search-${getManufacturedHomeSearchResults.value.searchId}`
          )
        } else goToDash()
      }
    }

    /** Called when component's staff payment data has been updated. */
    const onStaffPaymentDataUpdate = (val: StaffPaymentIF) => {
      let staffPaymentData: StaffPaymentIF = {
        ...val
      }

      if (staffPaymentData.routingSlipNumber || staffPaymentData.bcolAccountNumber || staffPaymentData.datNumber) {
        localState.validating = true
      } else {
        if (staffPaymentData.option !== localState.paymentOption) {
          localState.validating = false
          localState.paymentOption = staffPaymentData.option
        }
      }

      // disable validation
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

      setStaffPayment(staffPaymentData)
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return

      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value) {
        goToDash()
        return
      }

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      emit('haveData', haveData)
    }

    onMounted(() => {
      // Set Fees
      feeOptions.value.showServiceFees = !isRoleStaff.value
      setRegistrationFees(localState.feeType)
      setFeeQuantity(localState.feeType, localState.feeQuantity)
    })

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })
    watch(() => localState.feeQuantity, (count: number) => {
      setFeeQuantity(localState.feeType,
        localState.feeType === FeeSummaryTypes.NO_FEE_SEARCH
          ? 1
          : count
      )
    })
    watch(() => localState.combinedSearchFees, (comboSearch: any) => {
      localState.feeType !== FeeSummaryTypes.NO_FEE_SEARCH  && setRegistrationComboFees(
        localState.combinedFeeType,
        comboSearch
          ? comboSearch?.quantity
          : null
      )
    })

    return {
      submit,
      showDialog,
      setFolioValid,
      isRoleStaffReg,
      isRoleStaffSbc,
      handleDialogResp,
      goToSearchResult,
      setSearchCertified,
      getIsStaffClientPayment,
      onStaffPaymentDataUpdate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
