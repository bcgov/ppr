<template>
  <v-container
    id="confirm-mhr-search"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      setAttach="#confirm-mhr-search"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
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

          <v-card flat class="mt-6">
            <v-row no-gutters class="summary-header pa-2 rounded-top">
              <v-col cols="auto" class="pa-2">
                <v-icon color="darkBlue">mdi-home</v-icon>
                <label class="pl-3" :class="$style['sectionText']">
                  <strong>Selection Summary</strong>
                </label>
              </v-col>
            </v-row>
            <searched-result-mhr class="soft-corners px-6" :isReviewMode="true" />
          </v-card>

          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            :setIsMhr="true"
            class="pt-15"
          />

          <!-- Staff Payment Section -->
          <section v-if="getIsStaffClientPayment && !isRoleStaffSbc" class="mt-10">
            <v-row no-gutters>
              <v-col class="generic-label">
                <h2>2. Staff Payment</h2>
              </v-col>
            </v-row>

            <v-card flat class="mt-6 pa-6" :class="showErrorAlert ? 'border-error-left' : ''">
              <staff-payment-component
                id="staff-payment-dialog"
                :staffPaymentData="staffPaymentData"
                :validate="validating||showErrors"
                :displaySideLabel="true"
                :displayPriorityCheckbox="true"
                :invalidSection="showErrorAlert"
                @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
                @valid="staffPaymentValid = $event"
              />
              <v-row no-gutters>
                <v-spacer></v-spacer>
                <v-col cols="12" :sm="9">
                  <v-checkbox
                    class="mt-2"
                    id="certify-checkbox"
                    label="Make this a Certified search (add $25.00)"
                    @change="setSearchCertified($event)"
                  />
                </v-col>
              </v-row>
            </v-card>
          </section>

        </v-col>
        <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
                :setErrMsg="stickyComponentErrMsg"
                :setRightOffset="true"
                :setShowButtons="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setFeeQuantity="feeQuantity"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Pay and Download Result'"
                :setAdditionalFees="combinedSearchFees"
                @back="goToSearchResult()"
                @cancel="showDialog()"
                @submit="submit()"
              />
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onMounted, reactive, toRefs, watch } from 'vue'
import { useRouter } from '@/router'
import { useStore } from '@/store/store'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { FolioNumberSummary, StickyContainer } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { StaffPayment as StaffPaymentComponent } from '@bcrs-shared-components/staff-payment'
import { RouteNames, UIMHRSearchTypeValues } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import { notCompleteSearchDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, submitSelectedMhr } from '@/utils'
import { SearchedResultMhr } from '@/components/tables'
import { uniqBy } from 'lodash'
/* eslint-disable no-unused-vars */
import { DialogOptionsIF } from '@/interfaces'
import { AdditionalSearchFeeIF } from '@/composables/fees/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
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
  emits: ['haveData'],
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
  setup (props, context) {
    const router = useRouter()
    const {
      // Getters
      isRoleStaffReg,
      isRoleStaffSbc,
      getStaffPayment,
      isSearchCertified,
      getIsStaffClientPayment,
      getFolioOrReferenceNumber,
      getSelectedManufacturedHomes,
      getManufacturedHomeSearchResults,
      // Actions
      setStaffPayment,
      setSearchCertified
    } = useStore()

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
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
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
        const searchQuantity = uniqBy(getSelectedManufacturedHomes, UIMHRSearchTypeValues.MHRMHR_NUMBER)
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
        return uniqBy(getSelectedManufacturedHomes, UIMHRSearchTypeValues.MHRMHR_NUMBER)
          .filter(result => result.selected && !result.includeLienInfo)
          .length
      }),
      staffPaymentData: computed((): StaffPaymentIF => {
        let pd = getStaffPayment
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
      if (!val) goToDashboard()
    }

    const goToDashboard = (): void => {
      router.push({
        name: RouteNames.DASHBOARD
      })
      emitHaveData(false)
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
        (getIsStaffClientPayment && !isRoleStaffSbc) && !localState.staffPaymentValid)
      ) {
        localState.showErrors = true
        document.getElementById('staff-payment-dialog').scrollIntoView({ behavior: 'smooth' })
        return
      }
      localState.submitting = true
      let apiResponse
      if (isRoleStaffReg) {
        apiResponse = await submitSelectedMhr(
          getManufacturedHomeSearchResults.searchId,
          uniqBy(getSelectedManufacturedHomes, UIMHRSearchTypeValues.MHRMHR_NUMBER),
          getFolioOrReferenceNumber,
          getStaffPayment,
          isSearchCertified
        )
      } else {
        apiResponse = await submitSelectedMhr(
          getManufacturedHomeSearchResults.searchId,
          uniqBy(getSelectedManufacturedHomes, UIMHRSearchTypeValues.MHRMHR_NUMBER),
          getFolioOrReferenceNumber
        )
      }
      localState.submitting = false
      if (apiResponse === undefined || apiResponse !== 200) {
        // Expand Error Handling
        console.error('Api Error: ' + apiResponse)
      } else {
        // On success return to dashboard
        goToDashboard()
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
      if (!localState.isAuthenticated || (!props.isJestRunning && !getFeatureFlag('mhr-ui-enabled'))) {
        router.push({
          name: RouteNames.DASHBOARD
        })
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
    const emitHaveData = (haveData: Boolean = true): void => {
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
