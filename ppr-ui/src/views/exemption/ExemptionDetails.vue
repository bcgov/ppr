<template>
  <section
    id="exemption-details"
    aria-label="exemption-details"
  >
    <LienAlert v-if="hasLien" />

    <v-row
      noGutters
      class="soft-corners-top"
    >
      <v-col
        class="role"
        cols="auto"
        aria-label="exemption-help-content"
      >
        <p class="mt-9">
          This is the current information for this registration as of
          <span class="font-weight-bold">{{ asOfDateTime }}</span>.
        </p>

        <CautionBox
          class="mt-9"
          :setMsg="`The homeowner and home location information in the ${exemptionLabel.toLowerCase()} form and the
            manufactured home registry must align. If the current MHR registration information is
           inaccurate, the register must be updated prior to proceeding with this application for a ${exemptionLabel}.`"
        />

        <SimpleHelpToggle
          toggleButtonTitle="Help with Home Verification"
          :defaultHideText="false"
          class="my-6"
        >
          <template #content>
            <NonResExemptionSimpleHelp v-if="isNonResExemption" />
            <ExemptionSimpleHelp v-else />
          </template>
        </SimpleHelpToggle>
      </v-col>
    </v-row>

    <div :class="{ 'increment-sections' : isRoleStaffReg }">
      <section
        v-if="isRoleStaffReg"
        id="document-id-section"
        class="mt-7"
      >
        <DocumentId
          :content="docIdContent"
          :documentId="getMhrExemption.documentId"
          :validate="showErrors || localValidate"
          @setStoreProperty="handleDocumentIdUpdate"
          @isValid="updateValidation('documentId', $event)"
        />
      </section>

      <section
        id="home-details-section"
        :class="isRoleStaffReg ? 'mt-7' : 'mt-4'"
      >
        <h2>Home Details</h2>
        <p class="mb-n4">
          Verify the home details.
        </p>
        <YourHomeReview
          isExemption
          isTransferReview
        />
        <HomeLocationReview isTransferReview />
        <HomeOwnersReview isMhrTransfer />
      </section>

      <section
        v-if="isNonResExemption"
        id="remarks-section"
        class="mt-7"
      >
        <h2>Declaration</h2>
        <p>
          Select the date and reason this manufactured home was no longer in use. This information will appear in the
          Exemption Order upon filing.
        </p>

        <FormCard
          class="mt-5"
          label="Declaration Details"
          :showErrors="showDeclarationErrors"
        >
          <template #formSlot>
            <ExemptionDeclaration
              :validate="showDeclarationErrors"
              @updateOption="setMhrExemptionNote({ key: 'nonResidentialOption', value: $event })"
              @updateReason="setMhrExemptionNote({ key: 'nonResidentialReason', value: $event })"
              @updateOther="setMhrExemptionNote({ key: 'nonResidentialOther', value: $event })"
              @updateDate="setMhrExemptionNote({ key: 'expiryDateTime', value: $event })"
              @updateValid="updateValidation('declarationDetails', $event)"
            />
          </template>
        </FormCard>
      </section>

      <section
        v-if="isRoleStaffReg"
        id="remarks-section"
        class="mt-7"
      >
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
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { pacificDate } from '@/utils'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { docIdContent, exRemarksContent } from '@/resources'
import { ExemptionDeclaration, ExemptionSimpleHelp, NonResExemptionSimpleHelp } from '@/components/exemptions'
import { CautionBox, DocumentId, Remarks, SimpleHelpToggle, LienAlert } from '@/components/common'
import { HomeLocationReview, HomeOwnersReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { useExemptions, useNavigation } from '@/composables'
import { RouteNames } from '@/enums'
import FormCard from '@/components/common/FormCard.vue'

export default defineComponent({
  name: 'ExemptionDetails',
  components: {
    ExemptionDeclaration,
    FormCard,
    CautionBox,
    DocumentId,
    HomeOwnersReview,
    HomeLocationReview,
    SimpleHelpToggle,
    Remarks,
    YourHomeReview,
    LienAlert,
    ExemptionSimpleHelp,
    NonResExemptionSimpleHelp
  },
  props: { showErrors: { type: Boolean, default: false } },
  setup (props) {
    const { route } = useNavigation()
    const { exemptionLabel, isNonResExemption, updateValidation } = useExemptions()
    const { setValidation, setMhrExemptionNote, setMhrExemptionValue } = useStore()
    const { getMhrExemption, getMhrExemptionValidation, isRoleStaffReg, hasLien } = storeToRefs(useStore())

    const localState = reactive({
      localValidate: false,
      asOfDateTime: computed((): string => {
        return `${pacificDate(new Date())}`
      }),
      showDeclarationErrors: computed((): boolean => {
        return (props.showErrors || localState.localValidate) && !getMhrExemptionValidation.value?.declarationDetails
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
      exemptionLabel,
      getMhrExemption,
      docIdContent,
      exRemarksContent,
      isRoleStaffReg,
      setValidation,
      setMhrExemptionNote,
      handleRemarksUpdate,
      handleDocumentIdUpdate,
      updateValidation,
      hasLien,
      isNonResExemption,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
