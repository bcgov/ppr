<template>
  <div id="supporting-documents" class="pb-3">
    <p>
      Select the supporting document you have for this owner:
    </p>
    <v-radio-group
      id="supporting-docs-options"
      v-model="deletedOwner.supportingDocument"
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
        :ripple="false"
        data-test-id="supporting-doc-option-one"
      />
      <v-radio
        id="supporting-doc-option-two"
        :label="docOptions.optionTwo.text"
        active-class="selected-radio"
        :value="docOptions.optionTwo.value"
        :disabled="isSecondOptionDisabled"
        :ripple="false"
        data-test-id="supporting-doc-option-two"
      />
    </v-radio-group>
    <div v-if="deletedOwner.supportingDocument === docOptions.optionOne.value"
      class="supporting-doc-one">
      <p>
        <strong>Note:</strong> {{ docOptions.optionOne.note }}
      </p>
    </div>
    <div v-if="deletedOwner.supportingDocument === docOptions.optionTwo.value"
      class="supporting-doc-two">
      <slot name="deathCert"></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { useHomeOwners, useTransferOwners } from '@/composables'
import { ApiTransferTypes, SupportingDocumentsOptions } from '@/enums/transferTypes'
import { MhrRegistrationHomeOwnerIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'
import { DeathCertificate } from '.'
import { transferSupportingDocuments } from '@/resources/'

export default defineComponent({
  name: 'SupportingDocument',
  props: {
    deletedOwner: {
      type: Object as () => MhrRegistrationHomeOwnerIF,
      default: null
    },
    // Used to disable Death Cert when group has only one owner
    isSecondOptionDisabled: {
      type: Boolean
    }
  },
  components: { DeathCertificate },
  setup (props) {
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
        ...props.deletedOwner,
        hasDeathCertificate: props.deletedOwner.supportingDocument === SupportingDocumentsOptions.DEATH_CERT
      },
      props.deletedOwner.groupId
      )
      setUnsavedChanges(true)
    }

    const localState = reactive({
      // Get relevant supporting documents options based on transfer type from the Resources
      docOptions: transferSupportingDocuments[getMhrTransferType.value.transferType]
    })

    // When there is one owner in the group, pre-select first radio option
    if (props.isSecondOptionDisabled) {
      props.deletedOwner.supportingDocument = localState.docOptions.optionOne.value
      updateDeletedOwner()
    }

    watch(() => props.deletedOwner.supportingDocument, () => {
      updateDeletedOwner()
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
      opacity: 40%;
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
