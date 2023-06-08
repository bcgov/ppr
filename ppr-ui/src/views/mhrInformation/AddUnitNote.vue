<template>
  <v-container class="view-container pa-0" fluid>

    <div class="view-container px-15 pt-0 pb-5">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="mhr-information-header" class="pt-3 soft-corners-top">
              <v-col cols="auto">
                <h1>
                  {{ unitNote.header }}
                </h1>
                <p class="mt-7">
                  Enter the information below to file a {{ unitNote.typeDesc }} on manufactured home registration number
                  {{ mhrNumber }}.
                </p>

                <section id="mhr-unit-note-doc-id" class="mt-10">
                  <h2>Document ID</h2>
                  <p class="mt-2">
                    Enter the 8-digit Document ID number.
                  </p>
                  // Add Document ID component //
                </section>

                <section id="mhr-unit-note-remarks" class="mt-10">
                  <h2>Remarks</h2>
                  <p class="mt-2">
                    Add remarks to provide further details on this {{ unitNote.typeDesc }}.
                  </p>
                  // Add Remarks //
                </section>

                <section id="mhr-unit-note-person-giving-notice" class="mt-10">
                  <h2>Person Giving Notice</h2>
                  <p class="mt-2">
                    Enter the contact information for the person making the claim.
                  </p>
                  // Add Person Giving Notice //
                </section>

              </v-col>
            </v-row>
          </v-col>

          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix class="sticky-container" relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <StickyContainer
                  :setShowButtons="true"
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
import { defineComponent, computed, reactive, toRefs } from 'vue-demi'
import { useRouter } from 'vue2-helpers/vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { unitNotes } from '@/resources/mhr-transfers/unit-notes'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { RouteNames } from '@/enums'
import { StickyContainer } from '@/components/common'

export default defineComponent({
  name: 'AddUnitNote',
  components: { StickyContainer },
  props: {
  },
  setup () {
    const router = useRouter()

    const {
      setUnsavedChanges
    } = useStore()

    const {
      getMhrUnitNoteType,
      getMhrInformation
    } = storeToRefs(useStore())

    const localState = reactive({
      isReviewMode: false,

      unitNote: unitNotes[getMhrUnitNoteType.value],
      mhrNumber: getMhrInformation.value.mhrNumber,

      // fee summary
      feeType: FeeSummaryTypes.MHR_UNIT_NOTE,
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      })
    })

    const goToReview = async (): Promise<void> => {
    }

    const goToDash = (): void => {
      // if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      // else {
      setUnsavedChanges(false)
      // setGlobalEditingMode(false)
      // setEmptyMhrTransfer(initMhrTransfer())
      // resetValidationState()

      router.push({
        name: RouteNames.DASHBOARD
      })
      // }
    }

    return {
      goToReview,
      goToDash,
      ...toRefs(localState)
    }
  }
})
</script>

<style scoped></style>
