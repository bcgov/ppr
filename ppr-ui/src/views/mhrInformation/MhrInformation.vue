<template>
  <v-container class="view-container pa-0" fluid>

    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="mhr-information-header" class="pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>Manufactured Home Information</h1>
                <p class="mt-7">
                  This is the current information for this registration as of
                  <span class="font-weight-bold">{{ asOfDateTime }}</span>.
                </p>
              </v-col>
            </v-row>

            <section v-if="dataLoaded" class="py-4">
              <header class="review-header mt-1">
                <v-icon class="ml-1" color="darkBlue">mdi-home</v-icon>
                <label class="font-weight-bold pl-2">Home Owners</label>
              </header>

              <!-- MHR Information Review Section -->
              <template v-if="isReviewMode">
                <HomeOwnersTable
                  class="px-7"
                  isMhrTransfer
                  isReadonlyTable
                  :homeOwners="getMhrTransferHomeOwners"
                />
              </template>

              <!-- MHR Information Section -->
              <template v-else>
                <HomeOwners isMhrTransfer class="mt-n2" />
              </template>
            </section>

          </v-col>
          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <sticky-container
                  :setShowButtons="true"
                  :setBackBtn="showBackBtn"
                  :setCancelBtn="'Cancel'"
                  :setSaveBtn="'Save and Resume Later'"
                  :setSubmitBtn="reviewConfirmText"
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  :setErrMsg="transferErrorMsg"
                  @cancel="cancel()"
                  @back="isReviewMode = false"
                  @submit="goToReview()"
                />
              </affix>
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { RouteNames } from '@/enums'
import { fetchMhRegistration, pacificDate, submitMhrTransfer } from '@/utils'
import { StickyContainer } from '@/components/common'
import { useHomeOwners, useMhrInformation } from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { HomeOwners } from '@/views'
import { BaseDialog } from '@/components/dialogs'
import { unsavedChangesDialog } from '@/resources/dialogOptions'

export default defineComponent({
  name: 'MhrInformation',
  components: {
    BaseDialog,
    HomeOwners,
    HomeOwnersTable,
    StickyContainer
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const {
      getMhrTransferHomeOwners, getMhrInformation, hasUnsavedChanges
    } = useGetters<any>([
      'getMhrTransferHomeOwners', 'getMhrInformation', 'hasUnsavedChanges'
    ])

    const {
      setMhrTransferHomeOwnerGroups, setMhrTransferCurrentHomeOwnerGroups,setUnsavedChanges
    } = useActions<any>([
      'setMhrTransferHomeOwnerGroups', 'setMhrTransferCurrentHomeOwnerGroups','setUnSavedChanges'
    ])

    const { setEmptyMhrTransfer } = useActions<any>(['setEmptyMhrTransfer'])

    const {
      initMhrTransfer,
      buildApiData
    } = useMhrInformation()

    const {
      isGlobalEditingMode
    } = useHomeOwners()

    const options = unsavedChangesDialog
    var showCancelDialog = false

    const localState = reactive({
      dataLoaded: false,
      loading: false,
      isReviewMode: false,
      validate: false,
      feeType: FeeSummaryTypes.MHR_TRANSFER, // FUTURE STATE: To be dynamic, dependent on what changes have been made
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
      asOfDateTime: computed((): string => {
        return `${pacificDate(new Date())}`
      }),
      showBackBtn: computed((): string => {
        return localState.isReviewMode ? 'Back' : ''
      }),
      isValidTransfer: computed((): boolean => {
        return !isGlobalEditingMode.value && true // Get Owner Count here > 1 etc
      }),
      transferErrorMsg: computed((): string => {
        return localState.validate && !localState.isValidTransfer ? '< Please make any required changes' : ''
      }),
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      }),
      options,
      showCancelDialog
    })

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !localState.isAuthenticated) {
        goToDash()
        return
      }
      // page is ready to view
      context.emit('emitHaveData', true)

      localState.loading = true
      setEmptyMhrTransfer(initMhrTransfer())
      // Set baseline MHR Information to state
      await parseMhrInformation()
      localState.loading = false

      localState.dataLoaded = true
    })

    const parseMhrInformation = async (): Promise<void> => {
      // Future state to parse all relevant MHR Information
      const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)
      const currentOwnerGroups = data?.ownerGroups || [] // Safety check. Should always have ownerGroups
      setMhrTransferHomeOwnerGroups(currentOwnerGroups)

      // Store a snapshot of the existing OwnerGroups for baseline of current state
      setMhrTransferCurrentHomeOwnerGroups(currentOwnerGroups)
    }

    const cancel = async (): Promise<void> => {
      if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      else goToDash()
    }

    const goToReview = async (): Promise<void> => {
      localState.validate = true
      if (localState.isReviewMode) {
        localState.loading = true
        const mhrTransferFiling = await submitMhrTransfer(buildApiData(), getMhrInformation.value.mhrNumber)
        localState.loading = false

        !mhrTransferFiling.error
          ? goToDash()
          : console.log(mhrTransferFiling?.error) // Handle Schema or Api errors here..
      }
      if (localState.isValidTransfer) {
        localState.isReviewMode = true
      }
    }

    const goToDash = (): void => {
      context.root.$router.push({
        name: RouteNames.DASHBOARD
      })
    }

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) goToDash()
    }
    return {
      goToReview,
      goToDash,
      getMhrTransferHomeOwners,
      ...toRefs(localState),
      handleDialogResp,
      cancel
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
