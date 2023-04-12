<template>
  <div id="supporting-documents" class="pb-3">
    <p class="fs-16" :class="{ 'error-text': showDocumentsSelectionError }">
      Select the supporting document you have for this owner:
    </p>
    <v-radio-group
      id="supporting-docs-options"
      v-model="deletedOwnerState.supportingDocument"
      class="supporting-docs-options"
      row
      :disabled="isGlobalEditingMode"
      hide-details="true"
    >
      <v-radio
        id="supporting-doc-option-one"
        :label="docOptions.optionOne.text"
        active-class="selected-radio"
        :value="docOptions.optionOne.value"
        data-test-id="supporting-doc-option-one"
      />
      <v-radio
        id="supporting-doc-option-two"
        :label="docOptions.optionTwo.text"
        active-class="selected-radio"
        :class="{ 'invalid-selection': isSecondOptionError }"
        :value="docOptions.optionTwo.value"
        :disabled="isSecondOptionDisabled"
        :color="isSecondOptionError ? 'error' : 'primary'"
        data-test-id="supporting-doc-option-two"
      />
    </v-radio-group>
    <div v-if="deletedOwnerState.supportingDocument === docOptions.optionOne.value"
      class="supporting-doc-one">
      <p class="fs-16">
        <strong>Note:</strong> {{ docOptions.optionOne.note }}
      </p>
    </div>
    <div v-if="deletedOwnerState.supportingDocument === docOptions.optionTwo.value"
      class="supporting-doc-two">
      <slot name="deathCert"></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { useHomeOwners, useTransferOwners } from '@/composables'
import { ApiTransferTypes, SupportingDocumentsOptions } from '@/enums/transferTypes'
import { MhrRegistrationHomeOwnerIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { defineComponent, reactive, toRefs, watch, computed } from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'
import { transferSupportingDocuments } from '@/resources/'

export default defineComponent({
  name: 'SupportingDocument',
  emits: ['handleDocOptionOneSelected'],
  props: {
    deletedOwner: {
      type: Object as () => MhrRegistrationHomeOwnerIF,
      required: true
    },
    // validate the supporting document selection
    validate: {
      type: Boolean,
      default: false
    },
    // Used to disable Death Cert when group has only one owner
    isSecondOptionDisabled: {
      type: Boolean,
      default: false
    },
    // Used to show error for Death Cert radio button
    isSecondOptionError: {
      type: Boolean,
      default: false
    }
  },
  components: { },
  setup (props, { emit }) {
    const { editHomeOwner, isGlobalEditingMode } = useHomeOwners(true)
    const { getMhrTransferType } = useTransferOwners()

    const {
      setUnsavedChanges
    } = useActions([
      'setUnsavedChanges'
    ])

    // Update deleted Owner based on supporting document selection
    // Only death certificate is captured in the api
    const updateDeletedOwner = (): void => {
      editHomeOwner({
        ...localState.deletedOwnerState,
        hasDeathCertificate: localState.deletedOwnerState.supportingDocument === SupportingDocumentsOptions.DEATH_CERT
      },
      localState.deletedOwnerState.groupId
      )
      setUnsavedChanges(true)
    }

    const localState = reactive({
      deletedOwnerState: computed(() => props.deletedOwner),
      showDocumentsSelectionError: computed(() => {
        return props.validate && !localState.deletedOwnerState.supportingDocument
      }),
      // Get relevant supporting documents options based on transfer type from the Resources
      docOptions: transferSupportingDocuments[getMhrTransferType.value.transferType]
    })

    // When there is one owner in the group, pre-select first radio option
    if (props.isSecondOptionDisabled) {
      localState.deletedOwnerState.supportingDocument = localState.docOptions.optionOne.value
      updateDeletedOwner()
    }

    watch(() => localState.deletedOwnerState.supportingDocument, () => {
      updateDeletedOwner()
      // Only one Grant of Probate document can be selected for the group
      if (localState.deletedOwnerState.supportingDocument === SupportingDocumentsOptions.PROBATE_GRANT) {
        emit('handleDocOptionOneSelected')
      }
    })

    return {
      SupportingDocumentsOptions,
      transferSupportingDocuments,
      ApiTransferTypes,
      isGlobalEditingMode,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.supporting-docs-options {
    display: flex;

    .v-radio {
      flex: 1;
      background-color: rgba(0, 0, 0, 0.06);
      height: 60px;
      padding-left: 24px;
      margin-right: 20px;
    }

    .v-radio:last-of-type {
      margin-right: 0;
    }

    .v-radio--is-disabled {
      opacity: 0.4;
    }

    .invalid-selection {
      border: 1px solid $error;
      background-color: white;
      .error--text {
        color: $error;
      }
    }

    .selected-radio {
      border: 1px solid $app-blue;
    }

  }

  .supporting-doc-one,
  .supporting-doc-two {
    border-top: 1px solid $gray3;
    margin-top: 35px;
    padding-top: 35px;
  }

  .supporting-doc-two {
    padding-top: 22px;
    .death-certificate {
      margin-bottom: 0;
    }
  }
</style>
