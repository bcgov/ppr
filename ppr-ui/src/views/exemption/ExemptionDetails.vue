<template>
  <section id="exemption-details" aria-label="exemption-details">

    <LienAlert v-if="hasLien" />

    <v-row no-gutters class="soft-corners-top">
      <v-col class="role" cols="auto" aria-label="exemption-help-content">
        <p class="mt-9">
          This is the current information for this registration as of
          <span class="font-weight-bold">{{ asOfDateTime }}</span>.
        </p>

        <CautionBox
          class="mt-9"
          setMsg="The homeowner and home location information in the residential exemption form, the manufactured home
          registry, and the land title must align. If the current MHR registration information is inaccurate, the
          register must be updated prior to proceeding with this application for Residential Exemption."
        />

        <SimpleHelpToggle
          toggleButtonTitle="Help with Home Verification"
          :defaultHideText="false"
          class="my-6"
        >
          <template #content>
            <article class="px-8 py-2">
              <h3 class="text-center">Need Help Verifying Manufactured Home and Owner Details?</h3>
              <p class="pt-3">The homeowner and location information in each of the following must align on:</p>
              <p class="mt-7 mb-0">(a) this application for Residential Exemption;</p>
              <p class="mb-0">(b) the current Manufactured Home Registry (MHR) registration; and,</p>
              <p>(c) the current land title as recorded in the British Columbia land title and survey system
                (<a href="https://ltsa.ca/">ltsa.ca</a>)(LTSA).</p>
              <p class="mt-7">The home location and homeowner(s) named in the Manufactured Home Registry match the home
                location and current ownership of the home on the Residential Exemption form.</p>
              <p class="mt-7 mb-0">You must have one of the following that shows the name and home location and at least
                one of the homeowners as also being an owner of the land where the home is located:</p>
              <p class="mb-0">- a Land Title Search, dated within 30 days of today or</p>
              <p>- evidence of a pending freehold transfer.</p>
              <p class="mt-7">Any differences must be resolved before you proceed. If the current MHR registration
                information is inaccurate, the register must be updated prior to proceeding with this application for
                Residential Exemption.</p>
            </article>
          </template>
        </SimpleHelpToggle>
      </v-col>
    </v-row>

    <div :class="{ 'increment-sections' : isRoleStaffReg }">
      <section v-if="isRoleStaffReg" id="document-id-section" class="mt-7">
        <DocumentId
          :content="exDocIdContent"
          :documentId="getMhrExemption.documentId"
          :validate="showErrors || localValidate"
          @setStoreProperty="handleDocumentIdUpdate"
          @isValid="updateValidation('documentId', $event)"
        />
      </section>

      <section id="home-details-section" :class="isRoleStaffReg ? 'mt-7' : 'mt-4'">
        <h2>Home Details</h2>
        <p class="mb-n4">Verify the home details.</p>
        <YourHomeReview isExemption isTransferReview />
        <HomeLocationReview isTransferReview />
        <HomeOwnersReview isMhrTransfer />
      </section>

      <section v-if="isRoleStaffReg" id="remarks-section" class="mt-7">
        <Remarks
          :content="exRemarksContent"
          :unitNoteRemarks="getMhrExemption.note.remarks"
          :validate="showErrors || localValidate"
          @setStoreProperty="handleRemarksUpdate"
          @isValid="updateValidation('remarks', $event)"
        />
      </section>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue-demi'
import { pacificDate } from '@/utils'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { exDocIdContent, exRemarksContent } from '@/resources'
import { CautionBox, DocumentId, Remarks, SimpleHelpToggle, LienAlert } from '@/components/common'
import { HomeLocationReview, HomeOwnersReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { useExemptions, useNavigation } from '@/composables'
import { RouteNames } from '@/enums'

export default defineComponent({
  name: 'ExemptionDetails',
  components: {
    CautionBox,
    DocumentId,
    HomeOwnersReview,
    HomeLocationReview,
    SimpleHelpToggle,
    Remarks,
    YourHomeReview,
    LienAlert
  },
  props: { showErrors: { type: Boolean, default: false } },
  setup () {
    const { route } = useNavigation()
    const { updateValidation } = useExemptions()
    const { setValidation, setMhrExemptionNote, setMhrExemptionValue } = useStore()
    const { getMhrExemption, isRoleStaffReg, hasLien } = storeToRefs(useStore())

    const localState = reactive({
      localValidate: false,
      asOfDateTime: computed((): string => {
        return `${pacificDate(new Date())}`
      })
    })

    const handleDocumentIdUpdate = (docId: string): void => {
      return setMhrExemptionValue({ key: 'documentId', value: docId })
    }
    const handleRemarksUpdate = (remarks: { key: string, value: string }): void => {
      setMhrExemptionNote(remarks)
    }

    watch(() => route.name, async () => {
      if (route.name === RouteNames.EXEMPTION_REVIEW) localState.localValidate = true
    })

    return {
      getMhrExemption,
      exDocIdContent,
      exRemarksContent,
      isRoleStaffReg,
      setValidation,
      setMhrExemptionNote,
      handleRemarksUpdate,
      handleDocumentIdUpdate,
      updateValidation,
      hasLien,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
