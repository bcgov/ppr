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
                  :homeOwners="reviewOwners"
                  :currentHomeOwners="getMhrTransferCurrentHomeOwners"
                />
              </template>

              <!-- MHR Information Section -->
              <template v-else>
                <HomeOwners isMhrTransfer class="mt-n2" />
              </template>
            </section>

            <TransferDetails :validateTransferDetails="validateTransferDetails" />
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
                  @cancel="goToDash()"
                  @back="isReviewMode = false"
                  @save="onSave()"
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
import { ActionTypes, RouteNames } from '@/enums'
import {
  createMhrTransferDraft, deleteMhrDraft,
  fetchMhRegistration,
  getMhrTransferDraft,
  pacificDate,
  submitMhrTransfer,
  updateMhrDraft
} from '@/utils'
import { StickyContainer } from '@/components/common'
import { useHomeOwners, useMhrInformation } from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import TransferDetails from '@/components/mhrTransfers/TransferDetails.vue'
import { HomeOwners } from '@/views'
import { BaseDialog } from '@/components/dialogs'
import { unsavedChangesDialog } from '@/resources/dialogOptions'
import { cloneDeep } from 'lodash'

export default defineComponent({
  name: 'MhrInformation',
  components: {
    BaseDialog,
    HomeOwners,
    TransferDetails,
    HomeOwnersTable,
    StickyContainer
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    isMhrTransfer: {
      type: Boolean,
      default: true
    }
  },
  setup (props, context) {
    const {
      getMhrTransferHomeOwners, getMhrInformation, getMhrTransferCurrentHomeOwners, hasUnsavedChanges
    } = useGetters<any>([
      'getMhrTransferHomeOwners', 'getMhrInformation', 'getMhrTransferCurrentHomeOwners', 'hasUnsavedChanges'
    ])

    const {
      setMhrTransferHomeOwnerGroups, setMhrTransferCurrentHomeOwnerGroups, setUnsavedChanges
    } = useActions<any>([
      'setMhrTransferHomeOwnerGroups', 'setMhrTransferCurrentHomeOwnerGroups', 'setUnsavedChanges'
    ])

    const { setEmptyMhrTransfer } = useActions<any>(['setEmptyMhrTransfer'])

    const {
      isTransferDetailsValid,
      initMhrTransfer,
      buildApiData
    } = useMhrInformation()

    const {
      isGlobalEditingMode,
      setShowGroups
    } = useHomeOwners(props.isMhrTransfer)

    const localState = reactive({
      dataLoaded: false,
      loading: false,
      isReviewMode: false,
      validate: false,
      validateTransferDetails: false,
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
        return !isGlobalEditingMode.value && isTransferDetailsValid.value && true // Get Owner Count here > 1 etc
      }),
      transferErrorMsg: computed((): string => {
        return localState.validate && !localState.isValidTransfer ? '< Please make any required changes' : ''
      }),
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      }),
      reviewOwners: computed(() => {
        return getMhrTransferHomeOwners.value.filter(owner => owner.action !== ActionTypes.REMOVED)
      }),
      options: unsavedChangesDialog,
      showCancelDialog: false

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
      await setUnsavedChanges(false)
    })

    // Future state to parse all relevant MHR Information
    const parseMhrInformation = async (): Promise<void> => {
      await parseCurrentOwnerGroups()
    }

    const parseCurrentOwnerGroups = async (): Promise<void> => {
      const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)
      const currentOwnerGroups = data?.ownerGroups || [] // Safety check. Should always have ownerGroups

      // Store a snapshot of the existing OwnerGroups for baseline of current state
      await setMhrTransferCurrentHomeOwnerGroups(cloneDeep(data.ownerGroups))

      currentOwnerGroups.forEach((ownerGroup, index) => {
        ownerGroup.groupId = index + 1
      })
      setShowGroups(currentOwnerGroups.length > 1)

      // Set owners to store
      if (getMhrInformation.value.draftNumber) {
        // Retrieve owners from draft if it exists
        const { registration } = await getMhrTransferDraft(getMhrInformation.value.draftNumber)
        setShowGroups(registration.addOwnerGroups.length > 1)
        setMhrTransferHomeOwnerGroups([...registration.addOwnerGroups])
      } else {
        // Set current owners if there is no draft
        setMhrTransferHomeOwnerGroups(currentOwnerGroups)
      }
    }

    const goToReview = async (): Promise<void> => {
      localState.validate = true
      localState.validateTransferDetails = true
      if (localState.isReviewMode) {
        localState.loading = true
        const apiData = await buildApiData()
        const mhrTransferFiling = await submitMhrTransfer(apiData, getMhrInformation.value.mhrNumber)
        localState.loading = false
        await setUnsavedChanges(false)

        if (!mhrTransferFiling.error) {
          // Delete the draft on successful submission
          if (getMhrInformation.value.draftNumber) await deleteMhrDraft(getMhrInformation.value.draftNumber)
          goToDash()
        } else console.log(mhrTransferFiling?.error) // Handle Schema or Api errors here.
      }
      if (localState.isValidTransfer) {
        localState.isReviewMode = true
      }
    }

    const onSave = async (): Promise<void> => {
      localState.loading = true
      const apiData = await buildApiData(true)

      const mhrTransferDraft = getMhrInformation.value.draftNumber
        ? await updateMhrDraft(getMhrInformation.value.draftNumber, apiData)
        : await createMhrTransferDraft(apiData)
      localState.loading = false
      setUnsavedChanges(false)
      !mhrTransferDraft.error
        ? goToDash()
        : console.log(mhrTransferDraft?.error) // Handle Schema or Api errors here..
    }

    const goToDash = (): void => {
      if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      else {
        context.root.$router.push({
          name: RouteNames.DASHBOARD
        })
      }
    }

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) {
        setUnsavedChanges(false)
        goToDash()
      }
    }

    return {
      goToReview,
      onSave,
      goToDash,
      getMhrTransferHomeOwners,
      getMhrTransferCurrentHomeOwners,
      ...toRefs(localState),
      handleDialogResp
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
