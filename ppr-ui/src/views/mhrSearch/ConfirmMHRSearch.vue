<template>
  <v-container
    id="confirm-mhr-search"
    class="pt-14"
  >
    <v-overlay
      v-model="submitting"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="50"
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
            <SearchedResultMhr
              class="px-1"
              :is-review-mode="true"
            />
          </v-card>

          <FolioNumberSummary
            :set-show-errors="showErrors"
            :set-is-mhr="true"
            class="pt-15"
            @folioValid="setFolioValid"
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
              <StaffPaymentComponent
                id="staff-payment-dialog"
                :staff-payment-data="staffPaymentData"
                :validate="validating||showErrors"
                :display-side-label="true"
                :display-priority-checkbox="true"
                :invalid-section="showErrorAlert"
                @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
                @valid="staffPaymentValid = $event"
              />
              <v-row no-gutters>
                <v-spacer />
                <v-col
                  cols="12"
                  :sm="9"
                >
                  <v-checkbox
                    id="certify-checkbox"
                    class="mt-2"
                    label="Make this a Certified search (add $25.00)"
                    @update:model-value="setSearchCertified"
                  />
                </v-col>
              </v-row>
            </v-card>
          </section>
        </v-col>
        <v-col
          class="pl-6"
          cols="3"
        >
          <aside>
            <sticky-container
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
import { FolioNumberSummary, StickyContainer, StaffPayment as StaffPaymentComponent } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { RouteNames, UIMHRSearchTypeValues, StaffPaymentOptions } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { notCompleteSearchDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, submitSelectedMhr } from '@/utils'
import { SearchedResultMhr } from '@/components/tables'
import { uniqBy } from 'lodash'
/* eslint-disable no-unused-vars */
import { DialogOptionsIF } from '@/interfaces'
import { AdditionalSearchFeeIF } from '@/composables/fees/interfaces'
import { StaffPaymentIF } from '@/interfaces'
import { useAuth, useNavigation } from '@/composables'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'ConfirmMHRSearch',
  components: {
    BaseDialog,
    FolioNumberSummary,
    StickyContainer,
    SearchedResultMhr,
    StaffPaymentComponent
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    isJestRunning: {
      type: Boolean,
      default: false
    }
  },
  emits: ['haveData'],
  setup (props, context) {
    const router = useRouter()
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      // Actions
      setStaffPayment,
      setSearchCertified
    } = useStore()
    const {
      // Getters
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
      feeType: FeeSummaryTypes.MHSEARCH,
      options: notCompleteSearchDialog as DialogOptionsIF,
      showCancelDialog: false,
      showErrors: false,
      submitting: false,
      validFolio: true,
      staffPaymentValid: false,
      validating: false,
      paymentOption: StaffPaymentOptions.NONE,
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
              feeType: FeeSummaryTypes.MHR_COMBINED_SEARCH,
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
          getFolioOrReferenceNumber.value
        )
      }
      localState.submitting = false
      if (apiResponse === undefined || apiResponse !== 200) {
        // Expand Error Handling
        console.error('Api Error: ' + apiResponse)
      } else {
        // On success return to dashboard
        goToDash()
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
      if (!isAuthenticated.value || (!props.isJestRunning && !getFeatureFlag('mhr-ui-enabled'))) {
        goToDash()
        return
      }

      // get registration data from api and load into store
      localState.submitting = true
      localState.submitting = false

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    return {
      submit,
      showDialog,
      setFolioValid,
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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';

</style>
