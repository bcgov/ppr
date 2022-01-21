<template>
  <v-app class="app-container" id="app">
    <!-- Dialogs -->
    <error-dialog
      attach="#app"
      :display="errorDialog"
      :options="dialogOptions"
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
        :show-actions="true"
        :show-login-actions="true"
      />

    <div class="app-body">
      <main v-if="!isErrorDialog">
        <v-row
          v-if="!isProd"
          no-gutters
          style="height: 40px; background-color: #FCBA19;"
          align="center"
          justify="center"
        >
          <v-col class="env-info">
            This application is for test purposes only. Data contained here is TEST DATA - NOT FOR OFFICIAL USE.
          </v-col>
        </v-row>
        <breadcrumb :setCurrentPath="currentPath" :setCurrentPathName="currentPathName" v-if="haveData" />
        <tombstone :setCurrentPath="currentPath" v-if="haveData" />
        <v-container class="view-container pa-0 ma-0">
          <v-row no-gutters>
            <v-col cols="12">
              <router-view
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
import SbcAuthenticationOptionsDialog from 'sbc-common-components/src/components/SbcAuthenticationOptionsDialog.vue'

// local Components
import * as Dialogs from '@/components/dialogs'
import { Breadcrumb } from '@/components/common'
import { Tombstone } from '@/components/tombstone'
import * as Views from '@/views'
// local Mixins, utils, etc
import { AuthMixin } from '@/mixins'
import { fetchError, loginError, paymentErrorReg, saveSearchError } from '@/resources/dialogOptions'
import { getKeycloakRoles, getProductSubscription, getPPRUserSettings, updateLdUser, getSbcFromAuth } from '@/utils'
// local Enums, Constants, Interfaces
import {
  AccountProductCodes, AccountProductMemberships, AccountProductRoles, APIRegistrationTypes,
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
  private errorDialog = false
  private dialogOptions: DialogOptionsIF = loginError
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

  /** True if an error dialog is displayed. */
  private get isErrorDialog (): boolean {
    return this.errorDialog
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
        // add condition once we know what to look for
        if (false) { // eslint-disable-line no-constant-condition
          // cancel closing the page
          event.preventDefault()
          // pop up confirmation dialog
          // NB: custom text is not supported in all browsers
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

    // ensure user is authorized for this profile (kept this in just in case)
    try {
      await this.loadAuth()
    } catch (error) {
      console.log('Auth error =', error)
      this.haveData = true
      this.handleError({ statusCode: StatusCodes.UNAUTHORIZED })
      return
    }

    // load user info
    try {
      await this.loadUserInfo()
    } catch (error) {
      console.log('User info error =', error)
      this.haveData = true
      this.handleError({ statusCode: StatusCodes.NOT_FOUND })
      return
    }

    try {
      await this.loadAccountProductSubscriptions()
    } catch (error) {
      // may want to do something about this later, for now just log the error and let user continue
      console.log('Auth product subscription error =', error)
      return
    }

    // update Launch Darkly
    if (!this.isJestRunning) {
      try {
        await this.updateLaunchDarkly()
      } catch (error) {
        // just log the error -- no need to halt app
        console.log('Launch Darkly update error =', error)
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
    this.errorDialog = false
    this.payErrorDisplay = false
  }

  /** Fetches authorizations and verifies and stores roles. */
  private async loadAuth (): Promise<any> {
    // save roles from the keycloak token
    const authRoles = getKeycloakRoles()
    if (authRoles && authRoles.length > 0) {
      if (authRoles.includes('gov_account_user')) {
        // if staff make call to check for sbc
        const isSbc = await getSbcFromAuth()
        this.setRoleSbc(isSbc)
      }
      this.setAuthRoles(authRoles)
    } else {
      throw new Error('Invalid auth roles')
    }
  }

  /** Fetches current user info and stores it. */
  private async loadUserInfo (): Promise<any> {
    // auth api user info
    const response = await this.fetchCurrentUser()
    const userInfo: UserInfoIF = response?.data
    if (userInfo) {
      // ppr api user settings
      const settings: UserSettingsIF = await getPPRUserSettings()
      userInfo.settings = settings
      this.setUserInfo(userInfo)
      if (!settings || settings?.error) {
        // error popup -> user may still continue
        throw new Error('Invalid user settings')
      }
    } else {
      throw new Error('Invalid user info')
    }
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
    if (!this.loggedOut && this.$route?.path !== `/${RouteNames.SIGN_OUT}`) {
      // cases are for different payment errors, other errors caught at bottom
      let filing = this.registrationTypeUI
      if (this.getRegistrationFlowType !== RegistrationFlowType.NEW) {
        filing = this.getRegistrationFlowType?.toLowerCase() || 'registration'
      }
      this.payErrorOptions = { ...paymentErrorReg }
      if (this.registrationTypeUI) {
        this.payErrorOptions.text = this.payErrorOptions.text.replace('filing_type', filing)
      }
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
            // for other errors:
            const saveErrorCodes = [StatusCodes.INTERNAL_SERVER_ERROR, StatusCodes.BAD_REQUEST]
            if (saveErrorCodes.includes(error.statusCode)) {
              this.dialogOptions = saveSearchError
              this.errorDialog = true
            } else if (error.statusCode === StatusCodes.NOT_FOUND) {
              this.dialogOptions = fetchError
              this.errorDialog = true
            } else if (error.statusCode === StatusCodes.UNAUTHORIZED) {
              this.dialogOptions = loginError
              this.errorDialog = true
            } else {
              // temporary catch all (should be a more generic dialogue)
              this.dialogOptions = saveSearchError
              this.errorDialog = true
            }
          }
      }
    }
  }

  private proceedAfterError (proceed: boolean): void {
    this.errorDialog = false
    // still need to fill this out more
    // for now just refresh app
    if (proceed) this.initApp()
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

</style>
