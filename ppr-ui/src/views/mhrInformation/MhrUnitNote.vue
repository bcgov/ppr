<template>
  <v-container
    class="view-container pa-0 pb-10"
    fluid
  >
    <v-overlay
      v-model="loading"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="30"
        indeterminate
      />
    </v-overlay>

    <BaseDialog
      :closeAction="true"
      :setOptions="notCompleteDialog"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />

    <div class="pt-0 pb-20">
      <div class="container pa-0 pt-4">
        <v-row noGutters>
          <v-col cols="9">
            <div
              v-if="!isReviewMode"
              id="mhr-unit-note"
              class="pt-3"
              data-test-id="unit-note-add"
            >
              <h1>
                {{ unitNote.header }} {{ getCancelledUnitNoteHeader() }}
              </h1>

              <div
                v-if="isNoticeOfCaution"
                class="mt-7"
                data-test-id="cau-exp-note"
              >
                Note: This Notice of Caution will expire 3 months after the registration date.
              </div>

              <UnitNoteAdd
                :docType="unitNoteDocType"
                :validate="validate"
                @isValid="isUnitNoteValid = $event"
              />
            </div>

            <div
              v-else
              class="pt-3"
              data-test-id="unit-note-review"
            >
              <UnitNoteReview
                :validate="validate"
                @isValid="isUnitNoteReviewValid = $event"
              />
            </div>
          </v-col>

          <v-col
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :setShowButtons="true"
                :setBackBtn="showBackBtn"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="reviewConfirmText"
                :setRightOffset="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setErrMsg="feeSummaryErrorMsg"
                data-test-id="fee-summary"
                @cancel="showCancelDialog = true"
                @back="isReviewMode = false"
                @submit="goToReview()"
              />
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, computed, reactive, toRefs, onBeforeMount, onMounted, nextTick } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { StickyContainer } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { notCompleteDialog } from '@/resources/dialogOptions/cancelDialogs'
import { UnitNoteAdd, UnitNoteReview } from '@/components/unitNotes'
import { ErrorIF, RegTableNewItemI, UnitNoteRegistrationIF } from '@/interfaces'
import { useMhrUnitNote, useMhrValidations, useNavigation } from '@/composables'
import { scrollToFirstErrorComponent, scrollToTop } from '@/utils'
import { RouteNames, UnitNoteDocTypes } from '@/enums'

export default defineComponent({
  name: 'MhrUnitNote',
  components: {
    BaseDialog,
    StickyContainer,
    UnitNoteAdd,
    UnitNoteReview
  },
  props: {},
  emits: ['error'],
  setup (props, context) {
    const { goToDash, goToRoute } = useNavigation()

    const {
      setRegTableNewItem,
      setEmptyUnitNoteRegistration,
      setMhrUnitNoteRegistration
    } = useStore()

    const {
      getMhrUnitNoteType,
      getMhrUnitNoteRegistration,
      getMhrInformation,
      getMhrUnitNoteValidation
    } = storeToRefs(useStore())

    const {
      resetAllValidations
    } = useMhrValidations(toRefs(getMhrUnitNoteValidation.value))

    const {
      initEmptyUnitNote,
      isCancelUnitNote,
      buildApiDataAndSubmit,
      getCancelledUnitNoteHeader
    } = useMhrUnitNote()

    const localState = reactive({
      loading: false,
      isUnitNoteValid: false,
      isUnitNoteReviewValid: false,
      validate: false,
      isReviewMode: false,
      showCancelDialog: false,
      showBackBtn: computed((): string => localState.isReviewMode ? 'Back' : ''),
      isNoticeOfCaution: computed((): boolean => getMhrUnitNoteType.value === UnitNoteDocTypes.NOTICE_OF_CAUTION),

      unitNoteDocType: getMhrUnitNoteType.value,
      unitNote: UnitNotesInfo[getMhrUnitNoteType.value],
      mhrNumber: getMhrInformation.value.mhrNumber,

      isUnitNoteAddValid: computed((): boolean => {
        const { documentId, remarks, personGivingNotice } =
          getMhrUnitNoteValidation.value
        if(isCancelUnitNote.value) {
          return documentId && remarks
        }
        return documentId && remarks && personGivingNotice
      }),

      // fee summary
      feeType: FeeSummaryTypes.MHR_UNIT_NOTE,
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      }),
      feeSummaryErrorMsg: computed((): string => {
        const isValid = localState.isReviewMode ? localState.isUnitNoteReviewValid : localState.isUnitNoteValid
        return localState.validate && !isValid
          ? '< Please complete required information'
          : ''
      })
    })

    onBeforeMount(async () => {
      if (!getMhrUnitNoteType.value) {
        goToDash()
      }

      // initiate an empty Unit Note registration if the note is not Cancel Note
      if (!isCancelUnitNote.value && getMhrUnitNoteType.value !== UnitNoteDocTypes.NOTICE_OF_REDEMPTION) {
        // set empty Unit Note but keep the Unit Note Document Type
        const initialUnitNote: UnitNoteRegistrationIF = initEmptyUnitNote()
        initialUnitNote.note.documentType = getMhrUnitNoteType.value
        await setEmptyUnitNoteRegistration(initialUnitNote)
      }
      if (isCancelUnitNote.value) {
        setMhrUnitNoteRegistration({ key: 'attentionReference', value: '' })
      }
      // reset validation trigger
      localState.validate = false
    })

    onMounted(() => {
      scrollToTop()
    })

    const goToReview = async (): Promise<void> => {
      localState.validate = true // trigger validation for Unit Note component
      await nextTick()

      if (localState.isReviewMode) {
        if (!localState.isUnitNoteReviewValid) {
          scrollToFirstErrorComponent()
        } else {
          // register Unit Note
          localState.loading = true

          // build payload and submit
          const unitNoteRegistrationResp = await buildApiDataAndSubmit(getMhrUnitNoteRegistration.value)

          if (!unitNoteRegistrationResp.error) {
            // this will scroll & highlight a new row for Unit Note in Registration Table
            const newItem: RegTableNewItemI = {
              addedReg: unitNoteRegistrationResp.note.documentRegistrationNumber,
              addedRegParent: unitNoteRegistrationResp.mhrNumber,
              addedRegSummary: null,
              prevDraft: ''
            }

            setRegTableNewItem(newItem)
            goToDash()
          } else {
            emitError(unitNoteRegistrationResp?.error)
          }
          localState.loading = false
        }
      } else if (localState.isUnitNoteValid) {
        // go to Review if there are no errors on Unit Note Add screen
        localState.isReviewMode = true
        localState.validate = false
      }

      scrollToFirstErrorComponent()
    }

    const goToDashboard = (): void => {
      resetAllValidations()
      goToDash()
    }

    // Emit error to router view
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
    }

    const handleDialogResp = (val: boolean): void => {
      if (!val && localState.showCancelDialog) {
        goToRoute(RouteNames.MHR_INFORMATION)
      }
      localState.showCancelDialog = false
    }

    return {
      notCompleteDialog,
      goToReview,
      goToDashboard,
      handleDialogResp,
      getMhrUnitNoteValidation,
      getCancelledUnitNoteHeader,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
