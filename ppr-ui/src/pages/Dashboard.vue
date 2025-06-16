<template>
  <v-container
    id="dashboard"
    class="py-12 ma-0 px-0"
  >
    <!-- Page Overlay -->
    <v-overlay
      v-model="loading"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="30"
        :indeterminate="true"
      />
    </v-overlay>

    <BaseSnackbar
      :set-message="snackbarMsg"
      :toggle-snackbar="toggleSnackbar"
    />
    <div
      v-if="appReady"
      class="container pa-0"
    >
      <!-- Payment method messaging -->
      <CautionBox
        v-if="showCcPaymentMsg && !isCreditCardPreferredPayment"
        class="mb-10 bg-white !border-white"
        set-important-word="Updates to Preferred Payment Method"
        :set-msg="`You can now pay by credit card. To update your current payment method,
        <a class='px-0' href=${accountPaymentUrl}>click here</a>.`"
      >
        <template #prependSLot>
          <v-icon
            class="mr-2 pt-n1"
            color="primary"
          >
            mdi-information-outline
          </v-icon>
        </template>

        <template #appendSLot>
          <v-row no-gutters>
            <v-col>
              <v-btn
                variant="plain"
                class="msg-hide-icon float-right"
                :ripple="false"
                @click="hideCcStatusMsg(true)"
              >
                <v-icon color="primary">
                  mdi-close
                </v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </template>
      </CautionBox>

      <CautionBox
        v-if="showCcPaymentMsg && isCreditCardPreferredPayment"
        class="mb-10 bg-white !border-white"
        set-important-word="Important"
        :set-msg="`Credit card has been selected as the preferred payment method. Once ‘Register and Pay’ is clicked, no
         changes can be made to the registration until payment is completed.`"
      >
        <template #prependSLot>
          <v-icon
            class="mr-2 pt-n1"
            color="primary"
          >
            mdi-information-outline
          </v-icon>
        </template>

        <template #appendSLot>
          <v-row no-gutters>
            <v-col>
              <v-btn
                variant="plain"
                class="msg-hide-icon float-right"
                :ripple="false"
                @click="hideCcStatusMsg(true)"
              >
                <v-icon color="primary">
                  mdi-close
                </v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </template>
      </CautionBox>

      <!-- Qualified Supplier application messages -->
      <CautionBox
        v-if="!!qsMsgContent"
        class="mb-10"
        set-important-word="Note"
        :set-alert="qsMsgContent.status === ProductStatus.REJECTED"
        :set-msg="qsMsgContent.msg"
      >
        <template #prependSLot>
          <v-icon
            class="mr-2"
            :class="{ 'mt-n1': qsMsgContent.status === ProductStatus.REJECTED }"
            :color="qsMsgContent.color"
          >
            {{ qsMsgContent.icon }}
          </v-icon>
        </template>

        <template
          v-if="qsMsgContent.status != ProductStatus.PENDING"
          #appendSLot
        >
          <v-row no-gutters>
            <v-col>
              <v-btn
                variant="plain"
                class="msg-hide-icon float-right"
                :ripple="false"
                @click="hideStatusMsg(true)"
              >
                <v-icon color="primary">
                  mdi-close
                </v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </template>
      </CautionBox>

      <CautionBox
        v-if="showCommercialLiensMessaging"
        class="mb-10"
      >
        <template #contentSLot>
          <!-- Post Message to be enabled following the CLA Launch -->
          <PostClaMessage v-if="getFeatureFlag('cla-enabled')" />
          <PreClaMessage v-else />
        </template>
        <template
          v-if="true"
          #appendSLot
        >
          <v-row no-gutters>
            <v-col>
              <v-btn
                variant="plain"
                class="msg-hide-icon float-right mt-1"
                :ripple="false"
                @click="hideRlMessage(true)"
              ><a href="">Dismiss</a>
                <v-icon class="mt-[1px]" color="primary">
                  mdi-close
                </v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </template>
      </CautionBox>

      <!-- Only Render for DEALERS who have NOT accepted the Updated Qualified Supplier Agreement Terms -->
      <DealerInfo
        v-if="displayDealerInfo"
        class="mt-0 mb-10"
        @confirm-qs-requirements="confirmQsRequirements"
      />

      <!-- Search Selector -->
      <header
        id="search-header"
        class="review-header rounded-top py-3"
      >
        <h2 class="fs-16 lh-24">
          {{ headerTitle }}
        </h2>
      </header>
      <v-row no-gutters>
        <SearchBar
          class="rounded-bottom"
          :is-non-billable="isNonBillable"
          :service-fee="getUserServiceFee"
          @debtor-name="setSearchDebtorName"
          @searched-type="setSearchedType"
          @searched-value="setSearchedValue"
          @search-data="saveResults($event)"
          @search-error="emitError($event)"
        />
      </v-row>

      <!-- Search History -->
      <header
        id="search-history-header"
        class="review-header rounded-top mt-12 py-3"
      >
        <v-row no-gutters>
          <v-col
            class="d-flex"
            cols="12"
            sm="3"
          >
            <h2 class="fs-16 lh-24 mr-1">
              Searches
            </h2> ({{ searchHistoryLength }})
          </v-col>
          <v-col
            cols="12"
            sm="9"
          >
            <p class="fs-14 float-right mb-0">
              The Searches table will display up to 1000 searches conducted within the last 14 days.
            </p>
          </v-col>
        </v-row>
      </header>
      <SearchHistory
        v-if="!loading"
        :search-added="toggleSearchAdded"
        @retry="retrieveSearchHistory"
        @error="emitError"
      />
      <v-progress-linear
        v-else
        color="primary"
        :indeterminate="true"
        rounded
        height="6"
      />

      <!-- Registrations -->
      <v-row
        no-gutters
        class="mt-n1"
      >
        <v-col>
          <DashboardTabs
            v-if="enableDashboardTabs"
            class="mt-13"
            :app-loading-data="loading"
            :app-ready="appReady"
            @snack-bar-msg="snackBarEvent($event)"
          />

          <RegistrationsWrapper
            v-else-if="hasPPR"
            is-ppr
            :app-loading-data="loading"
            :app-ready="appReady"
            @snack-bar-msg="snackBarEvent($event)"
          />

          <RegistrationsWrapper
            v-else-if="hasMhrTableEnabled"
            is-mhr
            :app-loading-data="loading"
            :app-ready="appReady"
            @snack-bar-msg="snackBarEvent($event)"
          />
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, onBeforeMount, reactive, toRefs, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { ProductStatus, RouteNames, SettingOptions } from '@/enums'
import { getFeatureFlag } from '@/utils'
import { searchHistory } from '@/utils/ppr-api-helper'
import { getQualifiedSupplier, updateQualifiedSupplier } from '@/utils/mhr-api-helper'
import type {
  ErrorIF,
  ManufacturedHomeSearchResponseIF,
  SearchResponseIF
} from '@/interfaces'

export default defineComponent({
  name: 'Dashboard',
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    registryUrl: {
      type: String,
      default: 'https://bcregistry.ca'
    }
  },
  definePageMeta: { keepalive: true },
  emits: ['error', 'haveData'],
  setup (props, context) {
    const router = useRouter()
    const { navigateToUrl } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { fetchIsAccountAdmin, qsMsgContent, hideStatusMsg, updateUserMiscSettings } = useUserAccess()
    const {
      // Actions
      setSearchHistory,
      setSearchResults,
      setMhrDraftNumber,
      setMhrGenerateDocId,
      setSearchedType,
      setSearchedValue,
      setSearchDebtorName,
      setRegistrationType,
      resetNewRegistration,
      setManufacturedHomeSearchResults
    } = useStore()
    const {
      // Getters
      isRoleStaff,
      hasMhrRole,
      hasPprRole,
      isNonBillable,
      hasMhrEnabled,
      hasPprEnabled,
      isRoleStaffBcol,
      isRoleStaffReg,
      getUserSettings,
      getAccountId,
      getSearchHistory,
      getUserServiceFee,
      getSearchHistoryLength,
      isRoleQualifiedSupplier,
      hasEnhancedDealerEnabled,
      isCreditCardPreferredPayment
    } = storeToRefs(useStore())

    const localState = reactive({
      loading: false,
      isMHRSearchType: useSearch().isMHRSearchType,
      snackbarMsg: '',
      toggleSnackbar: false,
      toggleSearchAdded: false,
      dealerRecord: null,
      displayDealerInfo: false,
      searchHistoryLength: computed((): number => {
        return (getSearchHistory.value as SearchResponseIF[])?.length || 0
      }),
      hasPPR: computed((): boolean => {
        // For Staff, we check roles, for Client we check Products
        if (isRoleStaff.value || isRoleStaffBcol.value || isRoleStaffReg.value) {
          return hasPprRole.value
        } else {
          return hasPprEnabled.value
        }
      }),
      hasMHR: computed((): boolean => {
        // For Staff, we check roles, for Client we check Products
        if (isRoleStaff.value || isRoleStaffBcol.value || isRoleStaffReg.value) {
          return hasMhrRole.value && getFeatureFlag('mhr-ui-enabled')
        } else {
          return hasMhrEnabled.value
        }
      }),
      headerTitle: computed((): string => {
        if (localState.hasPPR && localState.hasMHR) {
          return 'Manufactured Home and Personal Property Registries Search'
        } else if (localState.hasPPR) {
          return 'Personal Property Registry Search'
        } else if (localState.hasMHR) {
          return 'Manufactured Home Registry Search'
        }
        return ''
    }),
      hasMhrTableEnabled: computed((): boolean => {
        return getFeatureFlag('mhr-registration-enabled') && localState.hasMHR &&
          (isRoleStaff.value || isRoleQualifiedSupplier.value) // Ensures that search only clients can't view table
      }),
      enableDashboardTabs: computed((): boolean => {
        return localState.hasPPR && localState.hasMhrTableEnabled
      }),
      showCommercialLiensMessaging: computed((): boolean => {
        return !getUserSettings.value[SettingOptions.MISCELLANEOUS_PREFERENCES]?.some(
          setting => setting.accountId === getAccountId.value && !!setting[SettingOptions.RL_MSG_HIDE]
        )
      }),
      showCcPaymentMsg: computed((): boolean => {
        return getFeatureFlag('mhr-credit-card-enabled') && !isRoleStaff.value &&
          !getUserSettings.value[SettingOptions.MISCELLANEOUS_PREFERENCES]?.some(
            setting => setting?.accountId === getAccountId.value && setting[SettingOptions.CC_MSG_HIDE] === true
          )
      }),
      accountPaymentUrl: computed((): string => {
        return useRuntimeConfig().public?.VUE_APP_AUTH_WEB_URL + '/account/' + getAccountId.value +
          '/settings/product-settings'
      })
    })

    onBeforeMount(() => {
      onAppReady(props.appReady)
    })

    onMounted(() => {
      // clear search data in the store
      setRegistrationType(null)
      setSearchedType(null)
      setSearchedValue('')
      setSearchResults(null)
      setMhrDraftNumber('')
      setMhrGenerateDocId(false)
      useTransportPermits().setLocationChange(false)
      useTransportPermits().setExtendLocationChange(false)
      useTransportPermits().setNewPermitChange(false)
    })

    /** Redirects browser to Business Registry home page. */
    const redirectRegistryHome = (): void => {
      navigateToUrl(props.registryUrl)
    }

    const retrieveSearchHistory = async (): Promise<void> => {
      // get/set search history
      const resp = await searchHistory()
      if (!resp || resp?.error) {
        setSearchHistory(null)
      } else {
        setSearchHistory(resp?.searches)
      }
    }

    const saveResults = (results: SearchResponseIF | ManufacturedHomeSearchResponseIF) => {
      if (results) {
        if (localState.isMHRSearchType(results.searchQuery.type)) {
          setManufacturedHomeSearchResults(results)
          router.replace({
            name: RouteNames.MHRSEARCH
          })
        } else {
          setSearchResults(results)
          router.replace({
            name: RouteNames.SEARCH
          })
        }
      }
    }

    const snackBarEvent = (msg: string): void => {
      localState.snackbarMsg = msg
      localState.toggleSnackbar = !localState.toggleSnackbar
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return

      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || !getFeatureFlag('ppr-ui-enabled')) {
        window.alert('Personal Property Registry is under construction. Please check again later.')
        redirectRegistryHome()
        return
      }
      emitHaveData(false)
      resetNewRegistration() // Clear store data from any previous registration.
      await retrieveSearchHistory()

      // tell App that we're finished loading
      localState.loading = false
      emitHaveData(true)

      if (hasEnhancedDealerEnabled.value) {
        // Fetch and set account admin status
        await fetchIsAccountAdmin()
        localState.dealerRecord = await getQualifiedSupplier()
        localState.displayDealerInfo = !localState.dealerRecord?.confirmRequirements
      }
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    const confirmQsRequirements = async (): Promise<void> => {
      localState.loading = true
      await updateQualifiedSupplier({ ...localState.dealerRecord, confirmRequirements: true })
      localState.displayDealerInfo = false
      localState.loading = false
    }

    /** Update Qualified Supplier status message - locally and user settings **/
    const hideRlMessage = async (hideMsg: boolean): Promise<void> => {
      await updateUserMiscSettings(SettingOptions.RL_MSG_HIDE, hideMsg)
    }

    const hideCcStatusMsg = async (hideMsg: boolean): Promise<void> => {
      await updateUserMiscSettings(SettingOptions.CC_MSG_HIDE, hideMsg)
    }

    watch(() => props.appReady, (val: boolean) => {
      localState.loading = !val && val !== null
      onAppReady(val)
    })

    watch(() => getSearchHistoryLength.value, (newVal: number, oldVal: number): void => {
      // show snackbar if oldVal was not null and highlight new search
      if (oldVal !== null) {
        localState.snackbarMsg = 'Your search was successfully added to your table.'
        localState.toggleSnackbar = !localState.toggleSnackbar
        localState.toggleSearchAdded = !localState.toggleSearchAdded

        // Remove search added styling after timeout
        setTimeout(() => { localState.toggleSearchAdded = !localState.toggleSearchAdded }, 5000)
      }
    })

    return {
      emitError,
      saveResults,
      isNonBillable,
      snackBarEvent,
      setSearchedType,
      setSearchedValue,
      hideRlMessage,
      qsMsgContent,
      hideStatusMsg,
      hideCcStatusMsg,
      getFeatureFlag,
      getUserServiceFee,
      setSearchDebtorName,
      redirectRegistryHome,
      retrieveSearchHistory,
      confirmQsRequirements,
      hasEnhancedDealerEnabled,
      isCreditCardPreferredPayment,
      ...toRefs(localState)
    }
  },
  computed: {
    ProductStatus () {
      return ProductStatus
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme';
.msg-hide-icon {
  min-height: 0!important;
  height: 0!important;
}
</style>
