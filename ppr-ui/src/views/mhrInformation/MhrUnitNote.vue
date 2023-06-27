<template>
  <v-container class="view-container pa-0" fluid>

    <BaseDialog
      :setOptions="cancelOptions"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />

    <div class="view-container px-15 pt-0 pb-5">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <div v-if="!isReviewMode" id="mhr-unit-note" class="pt-3" data-test-id="unit-note-add">
              <h1>
                {{ unitNote.header }}
              </h1>
              <p class="mt-7">
                Enter the information below to file a {{ unitNote.header }} on manufactured home registration number
                {{ mhrNumber }}.
              </p>

              <UnitNoteAdd
                :docType='unitNoteDocType'
                :validate="validate"
                @isValid="isUnitNoteValid = $event"
              />
            </div>

            <div v-else class="pt-3" data-test-id="unit-note-review">
              <h1>
               Review and Confirm
              </h1>
              <p class="mt-7">
                Review your changes and complete the additional information before registering.
              </p>

              <UnitNoteReview />
            </div>
          </v-col>

          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix class="sticky-container" relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <StickyContainer
                  :setShowButtons="true"
                  :setBackBtn="showBackBtn"
                  :setCancelBtn="'Cancel'"
                  :setSubmitBtn="reviewConfirmText"
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  @cancel="goToDash()"
                  @back="isReviewMode = false"
                  @submit="goToReview()"
                  data-test-id="fee-summary"
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
import { defineComponent, computed, reactive, toRefs, onMounted, nextTick } from 'vue-demi'
import { useRouter } from 'vue2-helpers/vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { StickyContainer } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { unsavedChangesDialog } from '@/resources/dialogOptions/cancelDialogs'
import { UnitNoteAdd, UnitNoteReview } from '@/components/unitNotes'

export default defineComponent({
  name: 'MhrUnitNote',
  components: {
    BaseDialog,
    StickyContainer,
    UnitNoteAdd,
    UnitNoteReview
  },
  props: {
  },
  setup () {
    const router = useRouter()

    const {
      setUnsavedChanges
    } = useStore()

    const {
      hasUnsavedChanges,
      getMhrUnitNoteType,
      getMhrInformation
    } = storeToRefs(useStore())

    const localState = reactive({
      isUnitNoteValid: false,
      validate: false,
      isReviewMode: false,
      cancelOptions: unsavedChangesDialog,
      showCancelDialog: false,
      showBackBtn: computed((): string => localState.isReviewMode ? 'Back' : ''),

      unitNoteDocType: getMhrUnitNoteType.value,
      unitNote: UnitNotesInfo[getMhrUnitNoteType.value],
      mhrNumber: getMhrInformation.value.mhrNumber,

      // fee summary
      feeType: FeeSummaryTypes.MHR_UNIT_NOTE,
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      })
    })

    onMounted(async () => {
      if (!getMhrUnitNoteType.value) {
        await router.push({ name: RouteNames.DASHBOARD })
      }
    })

    const goToReview = async (): Promise<void> => {
      localState.validate = true // validate Unit Note components
      await nextTick()
      if (localState.isUnitNoteValid) localState.isReviewMode = true
    }

    const goToDash = (): void => {
      if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      else {
        setUnsavedChanges(false)
        // resetValidationState()

        router.push({
          name: RouteNames.DASHBOARD
        })
      }
    }

    const handleDialogResp = (val: boolean): void => {
      if (!val) {
        setUnsavedChanges(false)
        if (localState.showCancelDialog) {
          goToDash()
        }
      }
      localState.showCancelDialog = false
    }

    return {
      goToReview,
      goToDash,
      handleDialogResp,
      ...toRefs(localState)
    }
  }
})
</script>

<style scoped></style>
