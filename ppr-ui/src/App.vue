<template>
  <v-app class="app-container" id="app">
    <!-- Dialogs -->
    <base-dialog
      id="errorDialogApp"
      :setDisplay="errorDisplay"
      :setOptions="errorOptions"
      @proceed="proceedAfterError"
    />
    <base-dialog
      id="payErrorDialogApp"
      :setDisplay="payErrorDisplay"
      :setOptions="payErrorOptions"
      @proceed="payErrorDialogHandler($event)"
    />

    <sbc-header
        class="sbc-header"
        :in-auth="false"
        :show-login-menu="false"
      />

    <div class="app-body">
      <main>
        <sbc-system-banner
          v-if="bannerText != null"
          v-bind:show="bannerText != null"
          v-bind:type="null"
          v-bind:message="bannerText"
          icon=" "
        ></sbc-system-banner>
        <breadcrumb :setCurrentPath="currentPath" :setCurrentPathName="currentPathName" v-if="haveData" />
        <tombstone :setCurrentPath="currentPath" v-if="haveData" />
        <v-container class="view-container pa-0 ma-0">
          <v-row no-gutters>
            <v-col cols="12">
              <router-view
                :appLoadingData="!haveData"
                :appReady="appReady"
                :isJestRunning="isJestRunning"
                :saveDraftExit="saveDraftExitToggle"
                :registryUrl="registryUrl"
                @profileReady="profileReady = true"
                @error="handleError($event)"
                @haveData="haveData = $event"
              />
            </v-col>
          </v-row>
        </v-container>
      </main>
    </div>

    <sbc-footer :aboutText=aboutText />
  </v-app>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from 'vue'
import { useStore } from './store/store'
import { useRoute, useRouter } from '@/router'
import { storeToRefs } from 'pinia'

import { StatusCodes } from 'http-status-codes'
import KeycloakService from 'sbc-common-components/src/services/keycloak.services'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcSystemBanner from 'sbc-common-components/src/components/SbcSystemBanner.vue'
import * as Dialogs from '@/components/dialogs'
import { Breadcrumb } from '@/components/common'
import { Tombstone } from '@/components/tombstone'
import * as Views from '@/views'
import {
  authPprError, authAssetsError, draftDeleteError, historyRegError, loginError, openDocError, paymentErrorReg,
  paymentErrorSearch, registrationCompleteError, registrationDeleteError, registrationLoadError,
  registrationOpenDraftError, registrationSaveDraftError, searchResultsError
} from '@/resources/dialogOptions'
import {
  getFees,
  getFeatureFlag,
  getKeycloakRoles,
  getProductSubscription,
  getPPRUserSettings,
  getSbcFromAuth,
  navigate,
  updateLdUser,
  fetchAccountProducts,
  axios,
  parsePayDetail
} from '@/utils'
import { FeeCodes } from '@/composables/fees/enums'
import {
  AccountProductCodes, AccountProductMemberships, AccountProductRoles, APIRegistrationTypes,
  ErrorCategories,
  ErrorCodes, ProductStatus, RegistrationFlowType, RouteNames, ProductCode
} from '@/enums'
import {
  AccountProductSubscriptionIF, DialogOptionsIF, // eslint-disable-line
  ErrorIF, RegistrationTypeIF, UserInfoIF, UserSettingsIF // eslint-disable-line
} from '@/interfaces'

export default defineComponent({
  name: 'App',
  components: {
    SbcHeader,
    SbcFooter,
    Breadcrumb,
    SbcSystemBanner,
    Tombstone,
    ...Dialogs,
    ...Views
  },
  setup () {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    const {
      // Actions
      setRoleSbc,
      setUserInfo,
      setAuthRoles,
      setRegistrationNumber,
      setAccountInformation,
      setUserProductSubscriptions,
      setAccountProductSubscription,
      setUserProductSubscriptionsCodes
    } = store
    const {
      // Getters
      isRoleStaff,
      isRoleStaffBcol,
      isRoleStaffReg,
      hasPprEnabled,
      hasMhrEnabled,
      getAccountId,
      getUserEmail,
      getUserFirstName,
      getUserLastName,
      getUserRoles,
      getUserUsername,
      hasUnsavedChanges,
      getRegistrationType,
      getRegistrationOther,
      getRegistrationFlowType,
      getUserProductSubscriptionsCodes
    } = storeToRefs(store)

    const localState = reactive({
      currentPath: '',
      currentPathName: null as RouteNames,
      errorDisplay: false,
      errorOptions: loginError as DialogOptionsIF,
      saveDraftExitToggle: false,
      payErrorDisplay: false,
      payErrorOptions: null as DialogOptionsIF,
      profileReady: false,
      appReady: false,
      haveData: false,
      loggedOut: false,
      tokenService: false,
      registryUrl: computed((): string => {
        // if REGISTRY_URL does not exist this will return 'undefined'. Needs to be null or str
        const configRegistryUrl = sessionStorage.getItem('REGISTRY_URL')
        if (configRegistryUrl) return configRegistryUrl
        return null
      }),
      bannerText: computed((): string => {
        // if banner text does not exist this will return 'undefined'. Needs to be null or str
        const bannerText = getFeatureFlag('banner-text')
        if (bannerText.trim().length > 0) return bannerText
        return null
      }),
      isJestRunning: computed((): boolean => {
        return (process.env.JEST_WORKER_ID !== undefined)
      }),
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
      aboutText: computed((): string => {
        return process.env.ABOUT_TEXT
      }),
      isProd: computed((): boolean => {
        const env = sessionStorage.getItem('POD_NAMESPACE')
        if (env != null && env.trim().length > 0) {
          return Boolean(env.toLowerCase().endsWith('prod'))
        }
        return Boolean(false)
      }),
      registrationTypeUI: computed((): string => {
        const regType = getRegistrationType.value as unknown as RegistrationTypeIF
        const regOther = getRegistrationOther.value as unknown as string
        if (regType.registrationTypeAPI === APIRegistrationTypes.OTHER) {
          return regOther || ''
        }
        return regType?.registrationTypeUI || ''
      })
    })

    onBeforeMount((): void => {
      if (route?.query?.logout) {
        localState.loggedOut = true
        sessionStorage.removeItem(SessionStorageKeys.KeyCloakToken)
        router.push(`${window.location.origin}`)
      } else {
        localState.loggedOut = false
        // before unloading this page, if there are changes then prompt user
        window.onbeforeunload = (event) => {
          const changeRoutes = [
            RouteNames.RENEW_REGISTRATION,
            RouteNames.CONFIRM_RENEWAL,
            RouteNames.REVIEW_DISCHARGE,
            RouteNames.CONFIRM_DISCHARGE
          ]
          const newAmendRoutes = [
            RouteNames.AMEND_REGISTRATION,
            RouteNames.CONFIRM_AMENDMENT,
            RouteNames.LENGTH_TRUST,
            RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
            RouteNames.ADD_COLLATERAL,
            RouteNames.REVIEW_CONFIRM
          ]
          const mhrRoutes = [
            RouteNames.YOUR_HOME,
            RouteNames.SUBMITTING_PARTY,
            RouteNames.HOME_OWNERS,
            RouteNames.HOME_LOCATION,
            RouteNames.MHR_REVIEW_CONFIRM,
            RouteNames.MHR_INFORMATION,
            RouteNames.MHRSEARCH,
            RouteNames.MHRSEARCH_CONFIRM
          ]

          const routeName = router.currentRoute.name as RouteNames
          if (
            (changeRoutes.includes(routeName) || newAmendRoutes.includes(routeName) || mhrRoutes.includes(routeName)) &&
            hasUnsavedChanges.value) {
            // browser popup
            event.preventDefault()
            // NB: custom text is no longer supported in any major browsers due to security reasons.
            // 'event.returnValue' is treated as a flag
            event.returnValue = 'You have unsaved changes. Are you sure you want to leave?'
          }
        }

        // When we are authenticated, allow time for session storage propagation from auth, then initialize application
        // (since we won't get the event from Signin component)
        if (localState.isAuthenticated) {
          setTimeout(() => { onProfileReady(true) }, localState.isJestRunning ? 0 : 1000)
        }
      }
    })

    const payErrorDialogHandler = (confirmed: boolean) => {
      const flowType = getRegistrationFlowType.value as unknown as RegistrationFlowType
      localState.payErrorDisplay = false
      if (confirmed) {
        if ([RegistrationFlowType.NEW, RegistrationFlowType.AMENDMENT].includes(flowType)) {
          localState.saveDraftExitToggle = !localState.saveDraftExitToggle
        } else {
          setRegistrationNumber(null)
          router.push({ name: RouteNames.DASHBOARD })
        }
      }
    }

    /** Initializes application. Also called for retry. */
    const initApp = async (): Promise<void> => {
      // reset errors in case of retry
      resetFlags()

      // ensure user is authorized for this profile
      const authResp = await loadAuth()
      if (authResp.statusCode !== StatusCodes.OK) {
        console.error(authResp.message)
        handleError(authResp)
        // show stopper so return
        return
      }

      // load user info
      const userInfoResp = await loadUserInfo()
      if (userInfoResp.statusCode !== StatusCodes.OK) {
        console.error(userInfoResp.message)
        handleError(userInfoResp)
        // show stopper so return
        return
      }

      try {
        await loadAccountProductSubscriptions()
      } catch (error) {
        console.error('Auth product subscription error = ', error)
        // not a show stopper so continue
        // this.handleError({
        //   message: String(error),
        //   statusCode: StatusCodes.INTERNAL_SERVER_ERROR
        //   // TODO: add error code for get subscriptions error
        // })
      }

      // update Launch Darkly
      if (!localState.isJestRunning) {
        try {
          await updateLaunchDarkly()
        } catch (error) {
          // just log the error -- no need to halt app
          console.error('Launch Darkly update error = ', error)
        }
      }

      if (!isRoleStaff.value && !isRoleStaffReg.value && !isRoleStaffBcol.value && !hasPprEnabled.value &&
        !hasMhrEnabled.value) {
        handleError({
          category: ErrorCategories.PRODUCT_ACCESS,
          message: '',
          statusCode: StatusCodes.UNAUTHORIZED
        })
        return
      }

      // finally, let router views know they can load their data
      localState.appReady = true
    }

    /** Starts token service that refreshes KC token periodically. */
    const startTokenService = async (): Promise<void> => {
      // only initialize once
      // don't start during Jest tests as it messes up the test JWT
      if (localState.tokenService || localState.isJestRunning) return

      try {
        console.info('Starting token refresh service...')
        await KeycloakService.initializeToken()
        localState.tokenService = true
      } catch (e) {
        // this happens when the refresh token has expired
        // 1. clear flags and keycloak data
        localState.tokenService = false
        localState.profileReady = false
        sessionStorage.removeItem(SessionStorageKeys.KeyCloakToken)
        sessionStorage.removeItem(SessionStorageKeys.KeyCloakRefreshToken)
        sessionStorage.removeItem(SessionStorageKeys.KeyCloakIdToken)
        sessionStorage.removeItem(SessionStorageKeys.CurrentAccount)
        // 2. reload app to get new tokens
        location.reload()
      }
    }

    /** Resets all error flags/states. */
    const resetFlags = (): void => {
      localState.appReady = false
      localState.haveData = false
      localState.errorDisplay = false
      localState.payErrorDisplay = false
    }

    /** Fetches authorizations and verifies and stores roles. */
    const loadAuth = async (): Promise<ErrorIF> => {
      // save roles from the keycloak token
      let message = ''
      let statusCode = StatusCodes.OK
      try {
        const authRoles = getKeycloakRoles()
        if (authRoles && authRoles.length > 0) {
          if (authRoles.includes('gov_account_user')) {
            // if staff make call to check for sbc
            const isSbc = await getSbcFromAuth()
            setRoleSbc(isSbc)
            isSbc && authRoles.push('sbc')
          }
          if (!authRoles.includes('ppr') && !authRoles.includes('mhr')) {
            throw new Error('No access to Assets')
          }
          setAuthRoles(authRoles)
        } else {
          throw new Error('Invalid auth roles')
        }
      } catch (error) {
        message = String(error)
        statusCode = StatusCodes.UNAUTHORIZED
      }

      return {
        category: ErrorCategories.ACCOUNT_ACCESS,
        message: message,
        statusCode: statusCode
      }
    }

    /** Fetches current user info and stores it. */
    const loadUserInfo = async (): Promise<ErrorIF> => {
      // auth api user info
      const response = await fetchCurrentUser()
      let message = ''
      let statusCode = response.status
      const userInfo: UserInfoIF = response?.data
      if (userInfo && statusCode === StatusCodes.OK) {
        // set ppr api user settings
        const settings: UserSettingsIF = await getPPRUserSettings()
        userInfo.settings = settings
        if (settings?.error) {
          message = 'Unable to get user settings.'
          statusCode = settings.error.statusCode
        } else if (!isRoleStaff.value) {
          // check if non-billable
          userInfo.feeSettings = null
          const fees = await getFees(FeeCodes.SEARCH)
          if (fees.error) {
            message = 'Unable to check if user is non billable.'
            statusCode = fees.error.statusCode
          } else if (fees?.filingFees === 0) {
            userInfo.feeSettings = {
              isNonBillable: true,
              serviceFee: fees?.serviceFees || 1.50
            }
          }
        }
        setUserInfo(userInfo)

        if (getAccountId.value) {
          const subscribedProducts = await fetchAccountProducts((getAccountId.value as unknown as number))
          if (subscribedProducts) {
            setUserProductSubscriptions(subscribedProducts)

            const activeProductCodes = subscribedProducts
              .filter(product => product.subscriptionStatus === ProductStatus.ACTIVE)
              .map(product => product.code)
            setUserProductSubscriptionsCodes(activeProductCodes)
          } else {
            throw new Error('Unable to get Products for the User')
          }
        }
      } else {
        message = 'Unable to get user info.'
      }
      const resp: ErrorIF = {
        category: ErrorCategories.ACCOUNT_SETTINGS,
        message: message,
        statusCode: statusCode
      }
      return resp
    }

    /**
     * Fetches current user data.
     * @returns a promise to return the user data
     */
    const fetchCurrentUser = (): Promise<any> => {
      const authUrl = sessionStorage.getItem('AUTH_API_URL')
      const config = { baseURL: authUrl }
      return axios.get('users/@me', config)
    }

    /** Gets user products and sets browser title accordingly. */
    const setBrowserTitle = (): void => {
      const userProducts = Array.from(getUserProductSubscriptionsCodes.value) as unknown as ProductCode[]
      if (userProducts.includes(ProductCode.PPR) &&
        userProducts.includes(ProductCode.MHR)) {
        document.title = 'BC Asset Registries (MHR/PPR)'
      } else if (userProducts.includes(ProductCode.MHR)) {
        document.title = 'BC Manufactured Home Registry'
      }
    }

    /** Gets account information (e.g. Premium account) and stores it. */
    const loadAccountInformation = (): void => {
      const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
      if (currentAccount) {
        const accountInfo = JSON.parse(currentAccount)
        setAccountInformation(accountInfo)
      }
    }

    /** Gets product subscription autorizations (for now just RPPR) and stores it. */
    const loadAccountProductSubscriptions = async (): Promise<any> => {
      let rpprSubscription = {} as AccountProductSubscriptionIF
      if (isRoleStaff.value) {
        rpprSubscription = {
          [AccountProductCodes.RPPR]: {
            membership: AccountProductMemberships.MEMBER,
            roles: [AccountProductRoles.PAY, AccountProductRoles.SEARCH]
          }
        }
        if (isRoleStaffBcol.value || isRoleStaffReg.value) {
          rpprSubscription.RPPR.roles.push(AccountProductRoles.EDIT)
        }
      } else rpprSubscription = await getProductSubscription(AccountProductCodes.RPPR)
      setAccountProductSubscription(rpprSubscription)
    }

    /** Updates Launch Darkly with user info. */
    const updateLaunchDarkly = async (): Promise<any> => {
      // since username is unique, use it as the user key
      const key: string = getUserUsername.value as unknown as string
      const email: string = getUserEmail.value as unknown as string
      const firstName: string = getUserFirstName.value as unknown as string
      const lastName: string = getUserLastName.value as unknown as string
      // remove leading { and trailing } and tokenize string
      const custom: any = { roles: getUserRoles.value }

      await updateLdUser(key, email, firstName, lastName, custom)
    }

    const handleError = (error: ErrorIF): void => {
      switch (error.category) {
        case ErrorCategories.ACCOUNT_ACCESS:
          localState.errorOptions = authPprError
          localState.errorDisplay = true
          break
        case ErrorCategories.ACCOUNT_SETTINGS:
          localState.errorOptions = loginError
          localState.errorDisplay = true
          break
        case ErrorCategories.DRAFT_DELETE:
          localState.errorOptions = draftDeleteError
          localState.errorDisplay = true
          break
        case ErrorCategories.DRAFT_LOAD:
          localState.errorOptions = registrationOpenDraftError
          localState.errorDisplay = true
          break
        case ErrorCategories.HISTORY_REGISTRATIONS:
          localState.errorOptions = historyRegError
          localState.errorDisplay = true
          break
        case ErrorCategories.HISTORY_SEARCHES:
          // handled inline
          break
        case ErrorCategories.PRODUCT_ACCESS:
          localState.errorOptions = authAssetsError
          localState.errorDisplay = true
          break
        case ErrorCategories.REGISTRATION_TRANSFER:
        case ErrorCategories.REGISTRATION_CREATE:
          handleErrorRegCreate(error)
          break
        case ErrorCategories.REGISTRATION_DELETE:
          localState.errorOptions = registrationDeleteError
          localState.errorDisplay = true
          break
        case ErrorCategories.REGISTRATION_LOAD:
          localState.errorOptions = registrationLoadError
          localState.errorDisplay = true
          router.push({ name: RouteNames.DASHBOARD })
          break
        case ErrorCategories.REGISTRATION_SAVE:
          localState.errorOptions = registrationSaveDraftError
          localState.errorDisplay = true
          break
        case ErrorCategories.REPORT_GENERATION:
          localState.errorOptions = openDocError
          localState.errorDisplay = true
          break
        case ErrorCategories.SEARCH:
          handleErrorSearch(error)
          break
        case ErrorCategories.SEARCH_COMPLETE:
          // handled in search comp
          break
        case ErrorCategories.SEARCH_UPDATE:
          // handled in search comp
          break
        default:
          console.error('Unhandled error: ', error)
      }
    }

    const handleErrorRegCreate = (error: ErrorIF) => {
      // prep for registration payment issues
      let filing = localState.registrationTypeUI
      const flowType = getRegistrationFlowType.value as unknown as RegistrationFlowType

      if (flowType !== RegistrationFlowType.NEW) {
        filing = flowType?.toLowerCase() || 'registration'
      }
      localState.payErrorOptions = { ...paymentErrorReg }
      if (localState.registrationTypeUI) {
        localState.payErrorOptions.text = localState.payErrorOptions.text.replace('filing_type', filing)
      }
      // errors with a 'type' are payment issues, other errors handles in 'default' logic
      switch (error.type) {
        case (
          ErrorCodes.BCOL_ACCOUNT_CLOSED ||
          ErrorCodes.BCOL_USER_REVOKED ||
          ErrorCodes.BCOL_ACCOUNT_REVOKED ||
          ErrorCodes.BCOL_UNAVAILABLE
        ):
          // bcol expected errors
          if ([RegistrationFlowType.NEW, RegistrationFlowType.AMENDMENT].includes(flowType)) {
            localState.payErrorOptions.text += '<br/><br/>' + error.detail +
              `<br/><br/>Your ${filing} will be saved as a draft and you can retry your payment ` +
              'once the issue has been resolved.'
          } else {
            localState.payErrorOptions.acceptText = 'Return to Dashboard'
            localState.payErrorOptions.text += '<br/><br/>' + error.detail +
              'You can retry your payment once the issue has been resolved.'
          }
          localState.payErrorDisplay = true
          break
        case ErrorCodes.ACCOUNT_IN_PAD_CONFIRMATION_PERIOD:
          // pad expected errors
          localState.payErrorOptions.text += '<br/><br/>' + error.detail +
            '<br/><br/>If this error continues after the waiting period has completed, please contact us.'
          localState.payErrorOptions.hasContactInfo = true
          localState.payErrorDisplay = true
          break
        default:
          if (error.type && error.type?.includes('BCOL') && error.detail) {
            // generic catch all bcol
            if ([RegistrationFlowType.NEW, RegistrationFlowType.AMENDMENT].includes(flowType)) {
              localState.payErrorOptions.text += '<br/><br/>' + error.detail +
                `<br/><br/>Your ${filing} will be saved as a draft and you can retry your payment ` +
                'once the issue has been resolved.'
            } else {
              localState.payErrorOptions.acceptText = 'Return to Dashboard'
              localState.payErrorOptions.text += '<br/><br/>' + error.detail +
                'You can retry your payment once the issue has been resolved.'
            }
            localState.payErrorDisplay = true
          } else if (error.statusCode === StatusCodes.PAYMENT_REQUIRED) {
            // generic catch all pay error
            const errorDetail = error.type ? error.detail : parsePayDetail(error.detail)
            localState.payErrorOptions.text = `The payment could not be completed at this time for the following
              reason:<br/><br/><b>${errorDetail}</b><br/><br/>If this issue persists, please contact us.`
            localState.payErrorOptions.hasContactInfo = true
            localState.payErrorDisplay = true
          } else {
            localState.errorOptions = registrationCompleteError
            localState.errorDisplay = true
          }
      }
    }

    const handleErrorSearch = (error: ErrorIF) => {
      switch (error.type) {
        case (
          ErrorCodes.BCOL_ACCOUNT_CLOSED ||
          ErrorCodes.BCOL_USER_REVOKED ||
          ErrorCodes.BCOL_ACCOUNT_REVOKED ||
          ErrorCodes.BCOL_UNAVAILABLE
        ):
          localState.payErrorOptions = { ...paymentErrorSearch }
          localState.payErrorOptions.text += '<br/><br/>' + error.detail
          localState.payErrorDisplay = true
          break
        case ErrorCodes.ACCOUNT_IN_PAD_CONFIRMATION_PERIOD:
          localState.payErrorOptions = { ...paymentErrorSearch }
          localState.payErrorOptions.text += '<br/><br/>' + error.detail +
            '<br/><br/>If this error continues after the waiting period has completed, please contact us.'
          localState.payErrorOptions.hasContactInfo = true
          localState.payErrorDisplay = true
          break
        default:
          if (error.type && error.type?.includes('BCOL') && error.detail) {
            // bcol generic
            localState.payErrorOptions = { ...paymentErrorSearch }
            localState.payErrorOptions.text += '<br/><br/>' + error.detail
            localState.payErrorDisplay = true
          } else if (error.statusCode === StatusCodes.PAYMENT_REQUIRED) {
            // generic pay error
            localState.payErrorOptions = { ...paymentErrorSearch }
            localState.payErrorOptions.text = '<b>The payment could not be completed at this time</b>' +
              '<br/><br/>If this issue persists, please contact us.'
            localState.payErrorOptions.hasContactInfo = true
            localState.payErrorDisplay = true
          } else {
            // generic search error
            localState.errorOptions = { ...searchResultsError }
            localState.errorDisplay = true
          }
      }
    }

    const proceedAfterError = (proceed: boolean): void => {
      localState.errorDisplay = false
      // Navigate to Registries dashboard in the event of a login or access error.
      if (localState.errorOptions === loginError || localState.errorOptions === authPprError ||
        localState.errorOptions === authAssetsError
      ) {
        navigate(localState.registryUrl)
      }
      // for now just refresh app
      if (!proceed) initApp()
    }

    const onProfileReady = async (val: boolean): Promise<void> => {
      if (val && !localState.loggedOut) {
        // start KC token service
        await startTokenService()

        // load account information
        loadAccountInformation()

        // initialize app
        await initApp()

        // set browser title
        setBrowserTitle()
      }
    }

    watch(() => route, (newVal: any) => {
      localState.currentPath = newVal.path
      localState.currentPathName = newVal.name as RouteNames
    }, { immediate: true, deep: true })

    /** Called when profile is ready -- we can now init app. */
    watch(() => localState.profileReady, async (val: boolean) => {
      await onProfileReady(val)
    })

    return {
      handleError,
      proceedAfterError,
      payErrorDialogHandler,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
// place app header on top of dialogs (and therefore still usable)
.app-header {
  z-index: 1000;
}

.env-info {
  font-size: 16px;
  text-align: center;
  color: #212529;
  background-color: #FCBA19;
}

.v-application .warning {
  background-color: #FCBA19 !important;
  color: #212529;
}

::v-deep .v-alert .v-alert__wrapper {
  padding: 8px 10px 10px 10px !important;
}
</style>
