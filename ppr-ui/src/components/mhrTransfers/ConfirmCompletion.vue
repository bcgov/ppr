<template>
  <div id="transfer-confirm">
    <h2><span>{{ sectionNumber }}</span>. Confirm</h2>
    <p class="mt-2">
      The following information must be completed and confirmed before submitting this registration.
    </p>
    <v-card
      flat
      rounded
      id="confirm-completion-card"
      class="mt-8 pt-5 pa-8 pr-6 pb-7"
      :class="{ 'border-error-left': showErrorComponent }"
      data-test-id="confirm-completion-card"
    >
      <v-form ref="confirmCompletionForm">
        <v-row>
          <v-col cols="3">
            <label class="generic-label" for="declared-value" :class="{ 'error-text': showErrorComponent }">
              Confirm Completion
            </label>
          </v-col>
          <v-col cols="9" class="confirm-completion-req">
            <ol>
              <li v-if="!isTransferDueToDeath" class="pl-3 pb-3 mb-7">
                <p><strong>Bill of sale</strong> has been signed by either all owners or by someone with the authority
                  to act on behalf of the registered owners and witnessed by an independent third party. If this is a
                  transfer to a beneficiary, you must have written consent from all beneficiaries that are not being
                  added as an owner.</p>
                <p class="confirm-completion-note">
                  <span>Note: </span> If the bill of sale has been signed by someone acting on behalf of the registered
                  owners, the person submitting this transfer is a lawyer or notary, and the power by which the
                  signatory was authorized was power of attorney, representation agreement, committee, receiver, or writ
                  of seizure and sale.
                </p>
              </li>
              <li v-else-if="isTransferDueToDeath" class="pl-3 pb-3 mb-7">
                <p><strong>Original or
                  <v-tooltip
                    top
                    content-class="top-tooltip pa-5"
                    transition="fade-transition"
                    data-test-id="organization-tooltip"
                    allow-overflow
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <span
                        v-bind="attrs"
                        v-on="on"
                      ><u> certified copy</u></span>
                    </template>
                    Vital Statistics and associated Funeral Homes issue original death certificates on secure, banknote
                    paper. Certified copies are obtained by presenting those original certificate(s) to a lawyer,
                    notary or other commissioner for taking affidavits and having them confirm that it is a true copy
                    of the original. A statement of death or a cremation certificate from a funeral director is not
                    acceptable.
                  </v-tooltip>
                  of Death Certificate</strong> that has been issued by Vital Statistics and has been recieved for each
                  joint tenant owner being removed due to death. I confirm that it was
                  <v-tooltip
                    top
                    content-class="top-tooltip pa-5"
                    transition="fade-transition"
                    data-test-id="organization-tooltip"
                    allow-overflow
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <span
                        v-bind="attrs"
                        v-on="on"
                      ><u> issued from Canada or the United States</u></span>
                    </template>
                    If the death certificate was issued outside of Canada or the US, the transfer will have to be sent
                    to the Manufactured Home Registry
                  </v-tooltip>
                  , and the name on the death certificate matches the name displayed above exactly.
                  </p>
              </li>
              <li v-if="isRoleStaff" class="pl-3 pb-3 mb-7">
                <p><strong>Transfer or Change Ownership form</strong> has been recieved and retained.</p>
              </li>
              <li v-if="isTransferToExecutorProbateWill" class="pl-3 pb-3 mb-7">
                <p><strong>Court certified true copy of the Probate with the will.</strong></p>
              </li>
              <li v-if="!isTransferDueToDeath" class="pl-3 pb-3 mb-7">
                <p><strong>Search of the Corporate Register</strong> has been completed if one or more of the current or
                future owners is an incorporated company, society or cooperative association.</p>
                <p class="confirm-completion-note">
                  <span>Note: </span> For current registered owners the incorporated business must have been active on
                  the Corporate Register at the time the bill of sale was signed. Future owners must be in active status
                  at the time of registration.
                </p>
              </li>
              <li class="pl-3 pb-3 mb-0">
                <p><strong>Personal Property Registry lien search</strong> has been completed and there are no liens
                on the home that stop the transfer.</p>
                <p class="confirm-completion-note">
                  <span>Note: </span> Liens that stop the transfer include Family Maintenance Enforcement Act, Family
                  Relations Act, BC Second Mortgage, Land Tax Deferment Act.
                </p>
              </li>
            </ol>
            <v-checkbox
              class="pa-7 ma-0 confirm-checkbox"
              :hide-details="true"
              id="checkbox-certified"
              v-model="confirmCompletion"
              data-test-id="confirm-completion-checkbox"
            >
              <template v-slot:label>
                <span data-test-id="confirm-checkbox-label" :class="{ 'invalid-color': showErrorComponent }">
                  I, <strong>{{ legalName }}</strong
                  >, confirm that all of the requirements listed above have been completed.
                </span>
              </template>
            </v-checkbox>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { ApiTransferTypes } from '@/enums'
import { useTransferOwners } from '@/composables'

export default defineComponent({
  name: 'ConfirmCompletion',

  props: {
    sectionNumber: {
      type: Number,
      default: 2
    },
    legalName: {
      type: String,
      required: true
    },
    setShowErrors: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirmCompletion'],
  setup (props, { emit }) {
    const {
      getMhrTransferType,
      isRoleStaff
    } = useGetters<any>([
      'getMhrTransferType',
      'isRoleStaff'
    ])

    const { isTransferDueToDeath, isTransferToExecutorProbateWill } = useTransferOwners()

    const localState = reactive({
      showErrorComponent: computed((): boolean => {
        return (props.setShowErrors && !localState.confirmCompletion)
      }),
      confirmCompletion: false,
      transferType: getMhrTransferType.value?.transferType
    })

    watch(
      () => localState.confirmCompletion,
      (val: boolean) => {
        emit('confirmCompletion', val)
      }
    )

    return {
      isRoleStaff,
      ApiTransferTypes,
      isTransferDueToDeath,
      isTransferToExecutorProbateWill,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#transfer-confirm {
  p {
    color: $gray7;
  }
  .confirm-completion-req {
    ol {
      padding-left: 50px;
    }
    ol li:not(:last-child) {
      border-bottom: 1px solid $gray3;
      ::marker {
        font-weight: bold;
      }
    }
  }
  .confirm-completion-note {
    margin-top: 20px;
    font-size: 14px;
    line-height: 22px;
    color: $gray7;
    span {
      font-weight: bold;
    }
  }

  u {
    border-bottom: 1px dotted #000;
    text-decoration: none;
  }

  .confirm-checkbox::v-deep {
    background-color: $gray1;
    font-size: 16px;
    line-height: 24px;
    vertical-align: top;

    .v-input__control .v-input__slot {
      align-items: flex-start;
    }
  }
}
</style>
