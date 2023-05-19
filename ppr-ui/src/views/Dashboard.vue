<template>
  <v-container id="dashboard" class="view-container px-15 py-10 ma-0" fluid>
    <!-- Page Overlay -->
    <v-overlay :value="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>

    <base-snackbar :setMessage="snackbarMsg" :toggleSnackbar="toggleSnackbar" />
    <div v-if="appReady" class="container pa-0">
      <v-row no-gutters>
        <v-col>
          <v-row no-gutters
                  id="search-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="auto">
              <b v-if="hasPPR && hasMHR">
                Manufactured Home and Personal Property Registries Search</b>
              <b v-else-if="hasPPR">Personal Property Registry Search</b>
              <b v-else-if="hasMHR">Manufactured Home Registry Search</b>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <search-bar
              class="soft-corners-bottom"
              :isNonBillable="isNonBillable"
              :serviceFee="getUserServiceFee"
              @debtor-name="setSearchDebtorName"
              @searched-type="setSearchedType"
              @searched-value="setSearchedValue"
              @search-data="saveResults($event)"
              @search-error="emitError($event)"
            />
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class='pt-12'>
        <v-col>
          <v-row no-gutters
                  id="search-history-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="12" sm="3">
              <b>Searches</b> ({{ searchHistoryLength }})
            </v-col>
            <v-col cols="12" sm="9">
              <span :class="[$style['header-help-text'], 'float-right', 'pr-6']">
                The Searches table will display up to 1000 searches conducted within the last 14 days.
              </span>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col v-if="!appLoadingData" cols="12">
              <search-history class="soft-corners-bottom" @retry="retrieveSearchHistory" @error="emitError"/>
            </v-col>
            <v-col v-else class="pa-10" cols="12">
              <v-progress-linear color="primary" indeterminate rounded height="6" />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class="mt-4 pt-7">
        <v-col>
          <DashboardTabs
            v-if="enableDashboardTabs"
            :appLoadingData="appLoadingData"
            :appReady="appReady"
            @snackBarMsg="snackBarEvent($event)"
          />

          <RegistrationsWrapper
            v-else-if="hasPPR"
            isPpr
            :appLoadingData="appLoadingData"
            :appReady="appReady"
            @snackBarMsg="snackBarEvent($event)"
          />
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useRouter } from '@/router'
import { useStore } from '@/store/store'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { ProductCode, RouteNames } from '@/enums'
import {
  getFeatureFlag,
  searchHistory,
  navigate
} from '@/utils'
import { BaseSnackbar, RegistrationsWrapper } from '@/components/common'
import { SearchHistory } from '@/components/tables'
import { SearchBar } from '@/components/search'
import { useSearch } from '@/composables/useSearch'
import { DashboardTabs } from '@/components/dashboard'
import {
  ErrorIF, // eslint-disable-line no-unused-vars
  ManufacturedHomeSearchResponseIF, RegTableNewItemI, // eslint-disable-line no-unused-vars
  SearchResponseIF // eslint-disable-line no-unused-vars
} from '@/interfaces'

export default defineComponent({
  name: 'Dashboard',
  components: {
    BaseSnackbar,
    DashboardTabs,
    SearchBar,
    SearchHistory,
    RegistrationsWrapper
  },
  emits: ['error', 'haveData'],
  props: {
    appLoadingData: {
      type: Boolean,
      default: false
    },
    appReady: {
      type: Boolean,
      default: false
    },
    isJestRunning: {
      type: Boolean,
      default: false
    },
    registryUrl: {
      type: String,
      default: 'https://bcregistry.ca'
    }
  },
  setup (props, context) {
    const router = useRouter()
    const {
      isRoleStaff,
      hasMhrRole,
      hasPprRole,
      isNonBillable,
      hasMhrEnabled,
      isRoleStaffBcol,
      isRoleStaffReg,
      getSearchHistory,
      getUserServiceFee,
      getSearchHistoryLength,
      isRoleQualifiedSupplier,
      getUserProductSubscriptionsCodes
    } = useGetters([
      'isRoleStaff',
      'hasMhrRole',
      'hasPprRole',
      'isNonBillable',
      'hasMhrEnabled',
      'isRoleStaffBcol',
      'isRoleStaffReg',
      'getSearchHistory',
      'getUserServiceFee',
      'getSearchHistoryLength',
      'isRoleQualifiedSupplier',
      'getUserProductSubscriptionsCodes'
    ])
    const {
      setSearchHistory,
      setSearchResults,
      setSearchedType,
      setSearchedValue,
      setSearchDebtorName,
      setRegistrationType,
      resetNewRegistration,
      setManufacturedHomeSearchResults
    } = useActions([
      'setSearchHistory',
      'setSearchResults',
      'setSearchedType',
      'setSearchedValue',
      'setSearchDebtorName',
      'setRegistrationType',
      'resetNewRegistration',
      'setManufacturedHomeSearchResults'
    ])

    const localState = reactive({
      loading: false,
      isMHRSearchType: useSearch().isMHRSearchType,
      snackbarMsg: '',
      toggleSnackbar: false,
      enableDashboardTabs: computed((): boolean => {
        return getFeatureFlag('mhr-registration-enabled') &&
          hasPprRole.value && hasMhrRole.value && (isRoleStaff.value || isRoleQualifiedSupplier.value)
      }),
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
      searchHistoryLength: computed((): number => {
        return getSearchHistory.value?.length || 0
      }),
      hasPPR: computed((): boolean => {
        // For Staff, we check roles, for Client we check Products
        if (isRoleStaff.value || isRoleStaffBcol.value || isRoleStaffReg.value) {
          return hasPprRole.value
        } else {
          return getUserProductSubscriptionsCodes.value.includes(ProductCode.PPR)
        }
      }),
      hasMHR: computed((): boolean => {
        // For Staff, we check roles, for Client we check Products
        if (isRoleStaff.value || isRoleStaffBcol.value || isRoleStaffReg.value) {
          return hasMhrRole.value && getFeatureFlag('mhr-ui-enabled')
        } else {
          return hasMhrEnabled.value
        }
      })
    })

    onMounted(() => {
      // clear search data in the store
      setRegistrationType(null)
      setSearchedType(null)
      setSearchedValue('')
      setSearchResults(null)
      onAppReady(props.appReady)
    })

    /** Redirects browser to Business Registry home page. */
    const redirectRegistryHome = (): void => {
      navigate(props.registryUrl)
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

    const saveResults = (results: SearchResponseIF|ManufacturedHomeSearchResponseIF) => {
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
      if (!localState.isAuthenticated || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        window.alert('Personal Property Registry is under construction. Please check again later.')
        redirectRegistryHome()
        return
      }
      emitHaveData(false)
      resetNewRegistration(null) // Clear store data from any previous registration.
      await retrieveSearchHistory()

      // tell App that we're finished loading
      localState.loading = false
      emitHaveData(true)
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
      console.error(error)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: Boolean = true): void => {
      context.emit('haveData', haveData)
    }

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    watch(() => getSearchHistoryLength.value, (newVal: number, oldVal: number): void => {
      // show snackbar if oldVal was not null
      if (oldVal !== null) {
        localState.snackbarMsg = 'Your search was successfully added to your table.'
        localState.toggleSnackbar = !localState.toggleSnackbar
      }
    })

    return {
      emitError,
      saveResults,
      isNonBillable,
      snackBarEvent,
      setSearchedType,
      setSearchedValue,
      getUserServiceFee,
      setSearchDebtorName,
      redirectRegistryHome,
      retrieveSearchHistory,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.dashboard-title {
  background-color: $BCgovBlue0;
  color: $gray9;
  font-size: 1rem;
}

.header-help-text {
  color: $gray7;
  font-size: .875rem;
}
</style>
