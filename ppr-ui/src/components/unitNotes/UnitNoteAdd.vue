<template>
  <div>
    <section id="mhr-unit-note-doc-id" class="mt-10">
      <DocumentId
        :documentId="unitNoteDocumentId"
        :sectionNumber="1"
        :content="{
          title: 'Document ID',
          description: 'Enter the 8-digit Document ID number.',
          sideLabel: 'Document ID'
        }"
        :validate="validate"
        @setStoreProperty="handleStoreUpdate('documentId', $event)"
        @isValid="handleComponentValid(MhrCompVal.DOC_ID_VALID, $event)"
      />
    </section>

    <section id="mhr-unit-note-remarks" class="mt-10">
      <Remarks
        :unitNoteRemarks="unitNoteRemarks"
        :additionalRemarks="additionalRemarks"
        :showAdditionalRemarksCheckbox="isNoticeOfTaxSale"
        :sectionNumber="2"
        :content="remarksContent"
        :isRequired="isRemarksRequired"
        :validate="validate"
        @setStoreProperty="handleStoreUpdate($event.key, $event.value)"
        @isValid="handleComponentValid(MhrCompVal.REMARKS_VALID, $event)"
      />
    </section>

    <section id="mhr-unit-note-person-giving-notice" class="mt-10">
      <ContactInformation
        :contactInfo="unitNoteGivingNoticeParty"
        :sectionNumber="3"
        :content="contactInfoContent"
        :validate="validate"
        :isHidden="hasNoPersonGivingNotice"
        @setStoreProperty="handleStoreUpdate('givingNoticeParty', $event)"
        @isValid="handleComponentValid(MhrCompVal.PERSON_GIVING_NOTICE_VALID, $event)"
        enableCombinedNameValidation
        hidePartySearch
        hideDeliveryAddress
      >
        <template #preForm v-if="isPersonGivingNoticeOptional()">
          <v-checkbox
              id="no-person-giving-notice-checkbox"
              class="mb-8"
              :label="hasNoPersonGivingNoticeText"
              v-model="hasNoPersonGivingNotice"
              hide-details
          />
        </template>
      </ContactInformation>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { UnitNoteDocTypes } from '@/enums'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { ContactInformationContentIF, UnitNoteIF } from '@/interfaces'
import { useMhrUnitNote, useMhrValidations } from '@/composables'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { DocumentId, Remarks, ContactInformation } from '@/components/common'
import {
  personGivingNoticeContent, collectorInformationContent, remarksContent,
  hasNoPersonGivingNoticeText
} from '@/resources'

export default defineComponent({
  name: 'UnitNoteAdd',
  components: {
    DocumentId,
    Remarks,
    ContactInformation
  },
  props: {
    validate: {
      type: Boolean,
      default: false
    },
    docType: {
      type: String as () => UnitNoteDocTypes,
      default: UnitNoteDocTypes.NOTICE_OF_CAUTION
    }
  },
  emits: ['isValid'],
  setup (props, { emit }) {
    const {
      setMhrUnitNoteProp
    } = useStore()

    const {
      getMhrUnitNote,
      getMhrUnitNoteValidation
    } = storeToRefs(useStore())

    const {
      getValidation,
      setValidation
    } = useMhrValidations(toRefs(getMhrUnitNoteValidation.value))

    const {
      isPersonGivingNoticeOptional,
      isCancelUnitNote
    } = useMhrUnitNote()

    const localState = reactive({
      unitNoteInfo: UnitNotesInfo[props.docType],
      isUnitNoteValid: computed((): boolean =>
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.DOC_ID_VALID) &&
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.REMARKS_VALID) &&
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.PERSON_GIVING_NOTICE_VALID)
      ),
      contactInfoContent: computed((): ContactInformationContentIF =>
        [UnitNoteDocTypes.NOTICE_OF_TAX_SALE, UnitNoteDocTypes.NOTICE_OF_REDEMPTION].includes(props.docType)
          ? collectorInformationContent
          : personGivingNoticeContent
      ),
      isNoticeOfTaxSale: computed((): boolean => props.docType === UnitNoteDocTypes.NOTICE_OF_TAX_SALE),
      hasNoPersonGivingNotice: (getMhrUnitNote.value as UnitNoteIF).hasNoPersonGivingNotice || false,

      // Remarks
      unitNoteRemarks: (getMhrUnitNote.value as UnitNoteIF).remarks || '',
      additionalRemarks: (getMhrUnitNote.value as UnitNoteIF).additionalRemarks,
      remarksContent: computed(() => {
        // update the side label for Cancel Note only
        if (isCancelUnitNote.value) {
          remarksContent.sideLabel = remarksContent.sideLabelCancelNote
        }
        return remarksContent
      }),
      isRemarksRequired: computed((): boolean => props.docType === UnitNoteDocTypes.PUBLIC_NOTE),

      // Document Id
      unitNoteDocumentId: computed(() => (getMhrUnitNote.value as UnitNoteIF).documentId || ''),

      // Person Giving Notice
      unitNoteGivingNoticeParty: (getMhrUnitNote.value as UnitNoteIF).givingNoticeParty || {}
    })

    const handleComponentValid = (component: MhrCompVal, isValid: boolean) => {
      setValidation(MhrSectVal.UNIT_NOTE_VALID, component, isValid)
    }

    const handleStoreUpdate = (key: string, val) => {
      setMhrUnitNoteProp({ key, value: val })
    }

    watch(() => localState.hasNoPersonGivingNotice, (val) => {
      setValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.PERSON_GIVING_NOTICE_VALID, val)
      handleStoreUpdate('hasNoPersonGivingNotice', val)
    })

    watch(() => [localState.isUnitNoteValid, props.validate], () => {
      emit('isValid', localState.isUnitNoteValid)
    })

    return {
      personGivingNoticeContent,
      MhrCompVal,
      handleStoreUpdate,
      handleComponentValid,
      isPersonGivingNoticeOptional,
      hasNoPersonGivingNoticeText,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped></style>
