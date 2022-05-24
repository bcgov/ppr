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
      @proceed="payErrorDialogHandler()"
    />

    <sbc-header
        class="sbc-header"
        :in-auth="false"
        :show-login-menu="false"
      />

    <div class="app-body">
      <main>
        <sbc-system-banner
          v-if="systemMessage != null"
          v-bind:show="systemMessage != null"
          v-bind:type="systemMessageType"
          v-bind:message="systemMessage"
          icon=" "
          align="center"
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
// External
import { Component, Watch, Mixins } from 'vue-property-decorator'
import { Route } from 'vue-router' // eslint-disable-line
import { Action, Getter } from 'vuex-class'
import { StatusCodes } from 'http-status-codes'

// BC Registry
import KeycloakService from 'sbc-common-components/src/services/keycloak.services'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcSystemBanner from 'sbc-common-components/src/components/SbcSystemBanner.vue'
import SbcAuthenticationOptionsDialog from 'sbc-common-components/src/components/SbcAuthenticationOptionsDialog.vue'

// local Components
import * as Dialogs from '@/components/dialogs'
import { Breadcrumb } from '@/components/common'
import { Tombstone } from '@/components/tombstone'
import * as Views from '@/views'
// local Mixins, utils, etc
import { AuthMixin } from '@/mixins'
import {
  authError, draftDeleteError, historyRegError, loginError, openDocError, paymentErrorReg,
  paymentErrorSearch, registrationCompleteError, registrationDeleteError, registrationLoadError,
  registrationOpenDraftError, registrationSaveDraftError, searchResultsError
} from '@/resources/dialogOptions'
import {
  getFees,
  getKeycloakRoles,
  getProductSubscription,
  getPPRUserSettings,
  getSbcFromAuth,
  navigate,
  updateLdUser
} from '@/utils'
// local Enums, Constants, Interfaces
import { FeeCodes } from '@/composables/fees/enums'
import {
  AccountProductCodes, AccountProductMemberships, AccountProductRoles, APIRegistrationTypes,
  ErrorCategories,
  ErrorCodes, RegistrationFlowType, RouteNames
} from '@/enums'
import {
  AccountProductSubscriptionIF, ActionBindingIF, DialogOptionsIF, // eslint-disable-line
  ErrorIF, RegistrationTypeIF, UserInfoIF, UserSettingsIF // eslint-disable-line
} from '@/interfaces'

@Component({
  components: {
    Breadcrumb,
    SbcHeader,
    SbcFooter,
    SbcAuthenticationOptionsDialog,
    SbcSystemBanner,
    Tombstone,
    ...Dialogs,
    ...Views
  }
})
export default class App extends Mixins(AuthMixin) {
  // Global getters
  @Getter getRegistrationFlowType: RegistrationFlowType
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getRegistrationOther: string
  @Getter getUserEmail!: string
  @Getter getUserFirstName!: string
  @Getter getUserLastName!: string
  @Getter getUserRoles!: string
  @Getter getUserUsername!: string
  @Getter hasUnsavedChanges: Boolean
  @Getter isPremiumAccount!: boolean
  @Getter isRoleStaff!: boolean
  @Getter isRoleStaffBcol!: boolean
  @Getter isRoleStaffReg!: boolean

  // Global setter
  @Action setAuthRoles: ActionBindingIF
  @Action setAccountProductSubscribtion!: ActionBindingIF
  @Action setAccountInformation!: ActionBindingIF
  @Action setKeycloakRoles!: ActionBindingIF
  @Action setRegistrationNumber!: ActionBindingIF
  @Action setUserInfo: ActionBindingIF
  @Action setRoleSbc: ActionBindingIF

  // Local Properties
  private currentPath = ''
  private currentPathName: RouteNames = null
  private errorDisplay = false
  private errorOptions: DialogOptionsIF = loginError
  private saveDraftExitToggle = false
  private payErrorDisplay = false
  private payErrorOptions: DialogOptionsIF = null

  // FUTURE: change profileReady/appReady/haveData to a state machine?

  /** Whether the user profile is ready (ie, auth is loaded) and we can init the app. */
  private profileReady: boolean = false

  /** Whether the app is ready and the views can now load their data. */
  private appReady: boolean = false

  /** Whether the views have loaded their data and the spinner can be hidden. */
  private haveData: boolean = false

  /** Whether the app is in the process of logging out or not */
  private loggedOut: boolean = false

  /** Whether the token refresh service is initialized. */
  private tokenService: boolean = false

  /** The registry URL. */
  private get registryUrl (): string {
    // if REGISTRY_URL does not exist this will return 'undefined'. Needs to be null or str
    const configRegistryUrl = sessionStorage.getItem('REGISTRY_URL')
    if (configRegistryUrl) return configRegistryUrl
    return null
  }

  private get systemMessage (): string {
    // if SYSTEM_MESSAGE does not exist this will return 'undefined'. Needs to be null or str
    const systemMessage = sessionStorage.getItem('SYSTEM_MESSAGE')
    if (systemMessage) return systemMessage
    return null
  }

  private get systemMessageType (): string {
    // if SYSTEM_MESSAGE_TYPE does not exist this will return 'undefined'. Needs to be null or str
    const systemMessageType = sessionStorage.getItem('SYSTEM_MESSAGE_TYPE')
    if (systemMessageType) return systemMessageType
    return null
  }

  /** True if Jest is running the code. */
  private get isJestRunning (): boolean {
    return (process.env.JEST_WORKER_ID !== undefined)
  }

  /** Whether user is authenticated. */
  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  /** The About text. */
  private get aboutText (): string {
    return process.env.ABOUT_TEXT
  }

  private get isProd (): boolean {
    var env = sessionStorage.getItem('POD_NAMESPACE')
    if (env != null && env.trim().length > 0) {
      return Boolean(env.toLowerCase().endsWith('prod'))
    }
    return Boolean(false)
  }

  private get registrationTypeUI (): string {
    if (this.getRegistrationType?.registrationTypeAPI === APIRegistrationTypes.OTHER) {
      return this.getRegistrationOther || ''
    }
    return this.getRegistrationType?.registrationTypeUI || ''
  }

  /**
   * Called when component is created.
   * NB: User may not be authed yet.
   */
  private created (): void {
    if (this.$route?.query?.logout) {
      this.loggedOut = true
      sessionStorage.removeItem(SessionStorageKeys.KeyCloakToken)
      this.$router.push(`${window.location.origin}`)
    } else {
      this.loggedOut = false
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
        const routeName = this.$router.currentRoute.name as RouteNames
        if (changeRoutes.includes(routeName) || (newAmendRoutes.includes(routeName) && this.hasUnsavedChanges)) {
          // browser popup
          event.preventDefault()
          // NB: custom text is no longer supported in any major browsers due to security reasons.
          // 'event.returnValue' is treated as a flag
          event.returnValue = 'You have unsaved changes. Are you sure you want to leave?'
        }
      }

      // if we are already authenticated then go right to init
      // (since we won't get the event from Signin component)
      if (this.isAuthenticated) this.onProfileReady(true)
    }
  }

  private payErrorDialogHandler () {
    this.payErrorDisplay = false
    if ([RegistrationFlowType.NEW, RegistrationFlowType.AMENDMENT].includes(this.getRegistrationFlowType)) {
      this.saveDraftExitToggle = !this.saveDraftExitToggle
    } else {
      this.setRegistrationNumber(null)
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
  }

  @Watch('$route', { immediate: true, deep: true })
  onUrlChange (newVal: Route) {
    this.currentPath = newVal.path
    this.currentPathName = newVal.name as RouteNames
  }

  /** Called when profile is ready -- we can now init app. */
  @Watch('profileReady')
  private async onProfileReady (val: boolean): Promise<void> {
    //
    // do the one-time things here
    //
    if (val && !this.loggedOut) {
      // start KC token service
      await this.startTokenService()

      // load account information
      this.loadAccountInformation()

      // initialize app
      await this.initApp()
    }
  }

  /** Initializes application. Also called for retry. */
  private async initApp (): Promise<void> {
    //
    // do the repeatable things here
    //

    // reset errors in case of retry
    this.resetFlags()

    // ensure user is authorized for this profile
    const authResp = await this.loadAuth()
    if (authResp.statusCode !== StatusCodes.OK) {
      console.error(authResp.message)
      this.handleError(authResp)
      // show stopper so return
      return
    }

    // load user info
    const userInfoResp = await this.loadUserInfo()
    if (userInfoResp.statusCode !== StatusCodes.OK) {
      console.error(userInfoResp.message)
      this.handleError(userInfoResp)
      // show stopper so return
      return
    }

    try {
      await this.loadAccountProductSubscriptions()
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
    if (!this.isJestRunning) {
      try {
        await this.updateLaunchDarkly()
      } catch (error) {
        // just log the error -- no need to halt app
        console.error('Launch Darkly update error = ', error)
      }
    }

    // finally, let router views know they can load their data
    this.appReady = true
  }

  /** Starts token service that refreshes KC token periodically. */
  private async startTokenService (): Promise<void> {
    // only initialize once
    // don't start during Jest tests as it messes up the test JWT
    if (this.tokenService || this.isJestRunning) return

    try {
      console.info('Starting token refresh service...')
      await KeycloakService.initializeToken()
      this.tokenService = true
    } catch (e) {
      // this happens when the refresh token has expired
      // 1. clear flags and keycloak data
      this.tokenService = false
      this.profileReady = false
      sessionStorage.removeItem(SessionStorageKeys.KeyCloakToken)
      sessionStorage.removeItem(SessionStorageKeys.KeyCloakRefreshToken)
      sessionStorage.removeItem(SessionStorageKeys.KeyCloakIdToken)
      sessionStorage.removeItem(SessionStorageKeys.CurrentAccount)
      // 2. reload app to get new tokens
      location.reload()
    }
  }

  /** Resets all error flags/states. */
  private resetFlags (): void {
    this.appReady = false
    this.haveData = false
    this.errorDisplay = false
    this.payErrorDisplay = false
  }

  /** Fetches authorizations and verifies and stores roles. */
  private async loadAuth (): Promise<ErrorIF> {
    // save roles from the keycloak token
    let message = ''
    let statusCode = StatusCodes.OK
    try {
      const authRoles = getKeycloakRoles()
      if (authRoles && authRoles.length > 0) {
        if (authRoles.includes('gov_account_user')) {
          // if staff make call to check for sbc
          const isSbc = await getSbcFromAuth()
          this.setRoleSbc(isSbc)
          isSbc && authRoles.push('sbc')
        }
        if (!authRoles.includes('ppr') && !authRoles.includes('mhr')) {
          throw new Error('No access to Assets')
        }
        this.setAuthRoles(authRoles)
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
  private async loadUserInfo (): Promise<ErrorIF> {
    // auth api user info
    const response = await this.fetchCurrentUser()
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
      } else if (!this.isRoleStaff) {
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
      this.setUserInfo(userInfo)
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

  /** Gets account information (e.g. Premium account) and stores it. */
  private loadAccountInformation (): void {
    const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
    if (currentAccount) {
      const accountInfo = JSON.parse(currentAccount)
      this.setAccountInformation(accountInfo)
    }
  }

  /** Gets product subscription autorizations (for now just RPPR) and stores it. */
  private async loadAccountProductSubscriptions (): Promise<any> {
    let rpprSubscription = {} as AccountProductSubscriptionIF
    if (this.isRoleStaff) {
      rpprSubscription = {
        [AccountProductCodes.RPPR]: {
          membership: AccountProductMemberships.MEMBER,
          roles: [AccountProductRoles.PAY, AccountProductRoles.SEARCH]
        }
      }
      if (this.isRoleStaffBcol || this.isRoleStaffReg) {
        rpprSubscription.RPPR.roles.push(AccountProductRoles.EDIT)
      }
    } else rpprSubscription = await getProductSubscription(AccountProductCodes.RPPR)
    this.setAccountProductSubscribtion(rpprSubscription)
  }

  /** Updates Launch Darkly with user info. */
  private async updateLaunchDarkly (): Promise<any> {
    // since username is unique, use it as the user key
    const key: string = this.getUserUsername
    const email: string = this.getUserEmail
    const firstName: string = this.getUserFirstName
    const lastName: string = this.getUserLastName
    // remove leading { and trailing } and tokenize string
    const custom: any = { roles: this.getUserRoles }

    await updateLdUser(key, email, firstName, lastName, custom)
  }

  private handleError (error: ErrorIF): void {
    switch (error.category) {
      case ErrorCategories.ACCOUNT_ACCESS:
        this.errorOptions = authError
        this.errorDisplay = true
        break
      case ErrorCategories.ACCOUNT_SETTINGS:
        this.errorOptions = loginError
        this.errorDisplay = true
        break
      case ErrorCategories.DRAFT_DELETE:
        this.errorOptions = draftDeleteError
        this.errorDisplay = true
        break
      case ErrorCategories.DRAFT_LOAD:
        this.errorOptions = registrationOpenDraftError
        this.errorDisplay = true
        break
      case ErrorCategories.HISTORY_REGISTRATIONS:
        this.errorOptions = historyRegError
        this.errorDisplay = true
        break
      case ErrorCategories.HISTORY_SEARCHES:
        // handled inline
        break
      case ErrorCategories.REGISTRATION_CREATE:
        this.handleErrorRegCreate(error)
        break
      case ErrorCategories.REGISTRATION_DELETE:
        this.errorOptions = registrationDeleteError
        this.errorDisplay = true
        break
      case ErrorCategories.REGISTRATION_LOAD:
        this.errorOptions = registrationLoadError
        this.errorDisplay = true
        this.$router.push({ name: RouteNames.DASHBOARD })
        break
      case ErrorCategories.REGISTRATION_SAVE:
        this.errorOptions = registrationSaveDraftError
        this.errorDisplay = true
        break
      case ErrorCategories.REPORT_GENERATION:
        this.errorOptions = openDocError
        this.errorDisplay = true
        break
      case ErrorCategories.SEARCH:
        this.handleErrorSearch(error)
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

  private handleErrorRegCreate (error: ErrorIF) {
    // prep for registration payment issues
    let filing = this.registrationTypeUI
    if (this.getRegistrationFlowType !== RegistrationFlowType.NEW) {
      filing = this.getRegistrationFlowType?.toLowerCase() || 'registration'
    }
    this.payErrorOptions = { ...paymentErrorReg }
    if (this.registrationTypeUI) {
      this.payErrorOptions.text = this.payErrorOptions.text.replace('filing_type', filing)
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
        if ([RegistrationFlowType.NEW, RegistrationFlowType.AMENDMENT].includes(this.getRegistrationFlowType)) {
          this.payErrorOptions.text += '<br/><br/>' + error.detail +
            `<br/><br/>Your ${filing} will be saved as a draft and you can retry your payment ` +
            'once the issue has been resolved.'
        } else {
          this.payErrorOptions.acceptText = 'Return to Dashboard'
          this.payErrorOptions.text += '<br/><br/>' + error.detail +
            'You can retry your payment once the issue has been resolved.'
        }
        this.payErrorDisplay = true
        break
      case ErrorCodes.ACCOUNT_IN_PAD_CONFIRMATION_PERIOD:
        // pad expected errors
        this.payErrorOptions.text += '<br/><br/>' + error.detail +
          '<br/><br/>If this error continues after the waiting period has completed, please contact us.'
        this.payErrorOptions.hasContactInfo = true
        this.payErrorDisplay = true
        break
      default:
        if (error.type && error.type?.includes('BCOL') && error.detail) {
          // generic catch all bcol
          if ([RegistrationFlowType.NEW, RegistrationFlowType.AMENDMENT].includes(this.getRegistrationFlowType)) {
            this.payErrorOptions.text += '<br/><br/>' + error.detail +
              `<br/><br/>Your ${filing} will be saved as a draft and you can retry your payment ` +
              'once the issue has been resolved.'
          } else {
            this.payErrorOptions.acceptText = 'Return to Dashboard'
            this.payErrorOptions.text += '<br/><br/>' + error.detail +
              'You can retry your payment once the issue has been resolved.'
          }
          this.payErrorDisplay = true
        } else if (error.statusCode === StatusCodes.PAYMENT_REQUIRED) {
          // generic cath all pay error
          this.payErrorOptions.text = '<b>The payment could not be completed at this time</b>' +
            '<br/><br/>If this issue persists, please contact us.'
          this.payErrorOptions.hasContactInfo = true
          this.payErrorDisplay = true
        } else {
          this.errorOptions = registrationCompleteError
          this.errorDisplay = true
        }
    }
  }

  private handleErrorSearch (error: ErrorIF) {
    switch (error.type) {
      case (
        ErrorCodes.BCOL_ACCOUNT_CLOSED ||
        ErrorCodes.BCOL_USER_REVOKED ||
        ErrorCodes.BCOL_ACCOUNT_REVOKED ||
        ErrorCodes.BCOL_UNAVAILABLE
      ):
        this.payErrorOptions = { ...paymentErrorSearch }
        this.payErrorOptions.text += '<br/><br/>' + error.detail
        this.payErrorDisplay = true
        break
      case ErrorCodes.ACCOUNT_IN_PAD_CONFIRMATION_PERIOD:
        this.payErrorOptions = { ...paymentErrorSearch }
        this.payErrorOptions.text += '<br/><br/>' + error.detail +
          '<br/><br/>If this error continues after the waiting period has completed, please contact us.'
        this.payErrorOptions.hasContactInfo = true
        this.payErrorDisplay = true
        break
      default:
        if (error.type && error.type?.includes('BCOL') && error.detail) {
          // bcol generic
          this.payErrorOptions = { ...paymentErrorSearch }
          this.payErrorOptions.text += '<br/><br/>' + error.detail
          this.payErrorDisplay = true
        } else if (error.statusCode === StatusCodes.PAYMENT_REQUIRED) {
          // generic pay error
          this.payErrorOptions = { ...paymentErrorSearch }
          this.payErrorOptions.text = '<b>The payment could not be completed at this time</b>' +
            '<br/><br/>If this issue persists, please contact us.'
          this.payErrorOptions.hasContactInfo = true
          this.payErrorDisplay = true
        } else {
          // generic search error
          this.errorOptions = { ...searchResultsError }
          this.errorDisplay = true
        }
    }
  }

  private proceedAfterError (proceed: boolean): void {
    this.errorDisplay = false
    // still need to fill this out more
    if (this.errorOptions === loginError || this.errorOptions === authError) {
      navigate(this.registryUrl)
    }
    // for now just refresh app
    if (!proceed) this.initApp()
  }
}
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
