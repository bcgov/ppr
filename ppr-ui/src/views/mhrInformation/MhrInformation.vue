<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>

    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>

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

            <section>
              <header class="review-header mt-1">
                <v-icon class="ml-1" color="darkBlue">mdi-home</v-icon>
                <label class="font-weight-bold pl-2">Home Owners</label>
              </header>

              <!-- MHR Information Review Section -->
              <template v-if="isReviewMode">
                <HomeOwnersTable
                  :isReadOnlyTable="true"
                  :homeOwners="getMhrRegistrationHomeOwners"
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
                  :setSubmitBtn="'Review and Confirm'"
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  :setErrMsg="transferErrorMsg"
                  @cancel="goToDash()"
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
import { pacificDate } from '@/utils'
import { StickyContainer } from '@/components/common'
import { useHomeOwners, useMhrInformation } from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { HomeOwners } from '@/views'

export default defineComponent({
  name: 'MhrInformation',
  components: {
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
      // getMhrInformation to be used future State to Access Full Registration information
      // eslint-disable-next-line no-unused-vars
      getMhrInformation, getMhrRegistrationHomeOwners
    } = useGetters<any>([
      'getMhrInformation', 'getMhrRegistrationHomeOwners'
    ])

    const { setEmptyMhrTransfer } = useActions<any>(['setEmptyMhrTransfer'])

    const {
      initMhrTransfer
    } = useMhrInformation()

    const {
      isGlobalEditingMode
    } = useHomeOwners()

    const localState = reactive({
      dataLoaded: false,
      submitting: false,
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
      })
    })

    onMounted((): void => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !localState.isAuthenticated) {
        goToDash()
        return
      }

      // page is ready to view
      setEmptyMhrTransfer(initMhrTransfer())
      context.emit('emitHaveData', true)
      localState.dataLoaded = true
    })

    const goToReview = (): void => {
      localState.validate = true
      if (localState.isValidTransfer) {
        localState.isReviewMode = true
      }
    }

    const goToDash = (): void => {
      context.root.$router.push({
        name: RouteNames.DASHBOARD
      })
    }

    return {
      goToReview,
      goToDash,
      getMhrRegistrationHomeOwners, // Future: To be a getter from Transfer State
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
