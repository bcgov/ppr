<template>
  <div>
    <section id="mhr-unit-note-doc-id" class="mt-10">
      <h2>Document ID</h2>
      <p class="mt-2">
        Enter the 8-digit Document ID number.
      </p>
      // Add Document ID placeholder //
    </section>

    <section id="mhr-unit-note-remarks" class="mt-10">
      <h2>Remarks</h2>
      <p class="mt-2">
        Add remarks to provide further details on this {{ unitNote.typeDesc }}.
      </p>
      // Add Remarks placeholder //
    </section>

    <section id="mhr-unit-note-person-giving-notice" class="mt-10">
      <h2>Person Giving Notice</h2>
      <p class="mt-2">
        Enter the contact information for the person making the claim.
      </p>
      // Add Person Giving Notice placeholder //
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'
import { unitNotes as unitNotesResources } from '@/resources/mhr-transfers/unit-notes'
import { UnitNoteDocTypes } from '@/enums'

export default defineComponent({
  name: 'UnitNoteAdd',
  props: {
    docType: {
      type: String as () => UnitNoteDocTypes
    }
  },
  setup (props) {
    const localState = reactive({
      unitNote: unitNotesResources[props.docType]
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped></style>
