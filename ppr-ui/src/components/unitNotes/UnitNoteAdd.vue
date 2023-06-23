<template>
  <div>
    <section id="mhr-unit-note-doc-id" class="mt-10">
      <DocumentId
        :documentId="unitNoteDocumentId"
        :setStoreProperty="setDocumentId"
        :validate="true"
        @isValid="handleComponentValid(MhrCompVal.DOC_ID_VALID, $event)"
      />
    </section>

    <section id="mhr-unit-note-remarks" class="mt-10">
      <Remarks
        :unitNoteRemarks="unitNoteRemarks"
        description="Remarks will be shown when a search result is produced for this manufactured home."
        :setStoreProperty="setRemarks"
        :validate="false"
        @isValid="handleComponentValid(MhrCompVal.REMARKS_VALID, $event)"
      />
    </section>

    <section id="mhr-unit-note-person-giving-notice" class="mt-10">
      <ContactInformation
        :contactInfo="unitNoteGivingNoticeParty"
        :content="{
          title: 'Person Giving Notice',
          description: 'Enter the contact information for the person making the claim',
          sideLabel: 'Person Giving Notice'
        }"
        :validate="false"
        :setStoreProperty="setGivingNoticeParty"
        @isValid="handleComponentValid(MhrCompVal.PERSON_GIVING_NOTICE_VALID, $event)"
      />
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { UnitNoteDocTypes } from '@/enums'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { PartyIF, UnitNoteIF } from '@/interfaces'
import { useMhrValidations } from '@/composables'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { DocumentId, Remarks, ContactInformation } from '../common'

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
  setup (props) {
    const {
      setMhrUnitNote
    } = useStore()

    const {
      getMhrUnitNote,
      getMhrUnitNoteValidation
    } = storeToRefs(useStore())

    const {
      setValidation // eslint-disable-line no-unused-vars
    } = useMhrValidations(toRefs(getMhrUnitNoteValidation.value))

    const localState = reactive({
      unitNoteInfo: UnitNotesInfo[props.docType],
      isUnitNoteValid: false,

      // Remarks
      unitNoteRemarks: (getMhrUnitNote.value as UnitNoteIF).remarks || '',

      // Document Id
      unitNoteDocumentId: (getMhrUnitNote.value as UnitNoteIF).documentId || '',

      // Person Giving Notice
      unitNoteGivingNoticeParty: (getMhrUnitNote.value as UnitNoteIF).givingNoticeParty || {}
    })

    const handleComponentValid = (component: MhrCompVal, isValid: boolean) => {
      setValidation(MhrSectVal.UNIT_NOTE_VALID, component, isValid)
    }

    const setDocumentId = (val) => {
      setMhrUnitNote({ key: 'documentId', value: val })
    }

    const setRemarks = (val) => {
      setMhrUnitNote({ key: 'remarks', value: val })
    }

    const setGivingNoticeParty = (val: PartyIF) => {
      setMhrUnitNote({ key: 'givingNoticeParty', value: val })
    }

    return {
      MhrCompVal,
      setDocumentId,
      setRemarks,
      setGivingNoticeParty,
      handleComponentValid,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped></style>
