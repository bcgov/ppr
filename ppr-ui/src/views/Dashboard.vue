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
      :setMessage="snackbarMsg"
      :toggleSnackbar="toggleSnackbar"
    />
    <div
      v-if="appReady"
      class="container pa-0"
    >
      <!-- Qualified Supplier application messages -->
      <CautionBox
        v-if="!!qsMsgContent"
        class="mb-10"
        setImportantWord="Note"
        :setAlert="qsMsgContent.status === ProductStatus.REJECTED"
        :setMsg="qsMsgContent.msg"
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
          <v-row noGutters>
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

      <!-- Search Selector -->
      <header
        id="search-header"
        class="review-header rounded-top py-3"
      >
        <b v-if="hasPPR && hasMHR">
          Manufactured Home and Personal Property Registries Search</b>
        <b v-else-if="hasPPR">Personal Property Registry Search</b>
        <b v-else-if="hasMHR">Manufactured Home Registry Search</b>
      </header>
      <v-row noGutters>
        <SearchBar
          class="rounded-bottom"
          :isNonBillable="isNonBillable"
          :serviceFee="getUserServiceFee"
          @debtorName="setSearchDebtorName"
          @searchedType="setSearchedType"
          @searchedValue="setSearchedValue"
          @searchData="saveResults($event)"
          @searchError="emitError($event)"
        />
      </v-row>

      <!-- Search History -->
      <header
        id="search-history-header"
        class="review-header rounded-top mt-12 py-3"
      >
        <v-row noGutters>
          <v-col
            cols="12"
            sm="3"
          >
            <b>Searches</b> ({{ searchHistoryLength }})
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
        :searchAdded="toggleSearchAdded"
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
        noGutters
        class="mt-n1"
      >
        <v-col>
          <DashboardTabs
            v-if="enableDashboardTabs"
            class="mt-13"
            :appLoadingData="loading"
            :appReady="appReady"
            @snack-bar-msg="snackBarEvent($event)"
          />

          <RegistrationsWrapper
            v-else-if="hasPPR"
            isPpr
            :appLoadingData="loading"
            :appReady="appReady"
            @snack-bar-msg="snackBarEvent($event)"
          />

          <RegistrationsWrapper
            v-else-if="hasMhrTableEnabled"
            isMhr
            :appLoadingData="loading"
            :appReady="appReady"
            @snack-bar-msg="snackBarEvent($event)"
          />
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { ProductStatus, RouteNames } from '@/enums'
import { getFeatureFlag, searchHistory } from '@/utils'
import { BaseSnackbar, CautionBox, RegistrationsWrapper } from '@/components/common'
import { SearchHistory } from '@/components/tables'
import { SearchBar } from '@/components/search'
import { useSearch } from '@/composables/useSearch'
import { DashboardTabs } from '@/components/dashboard'
import {
  ErrorIF,
  ManufacturedHomeSearchResponseIF,
  SearchResponseIF
} from '@/interfaces'
import { useAuth, useNavigation, useTransportPermits, useUserAccess } from '@/composables'

export default defineComponent({
  name: 'Dashboard',
  components: {
    BaseSnackbar,
    CautionBox,
    DashboardTabs,
    SearchBar,
    SearchHistory,
    RegistrationsWrapper
  },
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
  emits: ['error', 'haveData'],
  setup (props, context) {
    const router = useRouter()
    const { navigateTo } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { qsMsgContent, hideStatusMsg } = useUserAccess()
    const {
      // Actions
      setSearchHistory,
      setSearchResults,
      setMhrDraftNumber,
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
      getSearchHistory,
      getUserServiceFee,
      getSearchHistoryLength,
      isRoleQualifiedSupplier
    } = storeToRefs(useStore())

    const localState = reactive({
      loading: false,
      isMHRSearchType: useSearch().isMHRSearchType,
      snackbarMsg: '',
      toggleSnackbar: false,
      toggleSearchAdded: false,
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
      hasMhrTableEnabled: computed((): boolean => {
        return getFeatureFlag('mhr-registration-enabled') && localState.hasMHR &&
          (isRoleStaff.value || isRoleQualifiedSupplier.value) // Ensures that search only clients can't view table
      }),
      enableDashboardTabs: computed((): boolean => {
        return localState.hasPPR && localState.hasMhrTableEnabled
      })
    })

    onMounted(() => {
      // clear search data in the store
      setRegistrationType(null)
      setSearchedType(null)
      setSearchedValue('')
      setSearchResults(null)
      setMhrDraftNumber('')
      useTransportPermits().setLocationChange(false)
      onAppReady(props.appReady)
    })

    /** Redirects browser to Business Registry home page. */
    const redirectRegistryHome = (): void => {
      navigateTo(props.registryUrl)
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
      localState.loading = true
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
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    watch(() => props.appReady, (val: boolean) => {
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
      qsMsgContent,
      hideStatusMsg,
      getUserServiceFee,
      setSearchDebtorName,
      redirectRegistryHome,
      retrieveSearchHistory,
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
@import '@/assets/styles/theme.scss';
.msg-hide-icon {
  min-height: 0!important;
  height: 0!important;
}
</style>
