<template>
  <div id="transfer-confirm">
    <h3 class="fs-18">
      {{ `${sectionNumber ? sectionNumber + '.' : ''} Confirm` }}
    </h3>
    <p class="mt-1">
      The following information must be completed and confirmed before submitting this registration.
    </p>
    <v-card
      id="confirm-completion-card"
      flat
      rounded
      class="mt-8 pt-10 pa-8 pr-6 pb-7"
      :class="{ 'border-error-left': showErrorComponent }"
      data-test-id="confirm-completion-card"
    >
      <v-form ref="confirmCompletionForm">
        <v-row>
          <v-col cols="3">
            <h4
              class="fs-16 lh-22"
              :class="{ 'error-text': showErrorComponent }"
            >
              Confirm Completion
            </h4>
          </v-col>
          <v-col
            cols="9"
            class="confirm-completion-req pl-0 pr-4"
          >
            <slot name="contentSlot">
              <ol>
                <li
                  v-if="isTransferBillOfSale"
                  class="pl-3 pt-0"
                  data-test-id="bill-of-sale-sale-or-gift"
                >
                  <p><strong>Bill of sale</strong>, if applicable, meets the following requirements:</p>
                  <ul>
                    <li>
                      It has been signed by either a) the registered owner(s) (individually or by a duly authorized
                      representative of an organization), or b) person(s) with the authority to act on behalf of the
                      registered owner(s).<br><br>
                    </li>
                    <li>
                      If all owners of the home are selling their interest, all owners have signed the bill of sale.
                      If a group of owners is selling their interest, all owners within that group have signed the
                      Bill of Sale.<br><br>
                    </li>
                    <li>
                      All signatures have been witnessed by an independent third party, and the name and occupation
                      of each witness has been recorded.<br><br>
                    </li>
                    <li>
                      If this is a transfer to a beneficiary, you must have evidence of written consent from all
                      other beneficiaries that are not being added as a registered owner.
                    </li>
                  </ul>
                  <p
                    v-if="isRoleStaff"
                    class="confirm-completion-note"
                  >
                    <strong>Note:</strong> If the Bill of Sale has been signed by a person acting on behalf of a
                    registered owner, the person submitting this transfer must provide evidence of the authority
                    by which the signatory was authorized. Such authorization must be granted by one of the
                    following: power of attorney, representation agreement, committee, receiver, or writ of
                    seizure and sale.
                  </p>
                  <p
                    v-else
                    class="confirm-completion-note"
                  >
                    <strong>Note:</strong> If the Bill of Sale has been signed by a person acting on behalf of a
                    registered owner, the qualified supplier submitting this transfer must be a lawyer or notary.
                    Unless you are a lawyer or notary, you are not authorized to continue. The lawyer or notary
                    must confirm the authority by which the signatory was authorized. Such authorization must be
                    granted by one of the following: power of attorney, representation agreement, committee,
                    receiver, or writ of seizure and sale.
                  </p>
                </li>
                <li
                  v-else-if="!isTransferDueToDeath && !isTransferWithoutBillOfSale"
                  class="pl-3 pt-0"
                  data-test-id="bill-of-sale-section"
                >
                  <p>
                    <strong>Bill of sale</strong> has been signed by either all owners or by someone with the authority
                    to act on behalf of the registered owners and witnessed by an independent third party. If this is a
                    transfer to a beneficiary, you must have written consent from all beneficiaries that are not being
                    added as an owner.
                  </p>
                  <p class="confirm-completion-note">
                    <strong>Note:</strong> If the bill of sale has been signed by someone acting on behalf of the
                    registered owners, the person submitting this transfer is a lawyer or notary, and the power by which
                    the signatory was authorized was power of attorney, representation agreement, committee, receiver,
                    or writ of seizure and sale.
                  </p>
                </li>
                <li
                  v-else-if="isTransferDueToDeath"
                  class="pl-3 pt-0"
                  data-test-id="death-certificate-section"
                >
                  <p>
                    <strong>Original or
                      <v-tooltip
                        location="top"
                        content-class="top-tooltip pa-5"
                        transition="fade-transition"
                        data-test-id="organization-tooltip"
                      >
                        <template #activator="{ props }">
                          <span
                            v-bind="props"
                          ><u> certified copy</u></span>
                        </template>
                        Vital Statistics and associated Funeral Homes issue original death certificates on secure,
                        banknote paper. Certified copies are obtained by presenting those original certificate(s) to a
                        lawyer, notary or other commissioner for taking affidavits and having them confirm that it is a
                        true copy of the original. A statement of death or a cremation certificate from a funeral
                        director is not acceptable.
                      </v-tooltip>
                      of Death Certificate</strong> that has been issued by Vital Statistics and has been received for
                    each joint tenant owner being removed due to death. I confirm that it was
                    <v-tooltip
                      location="top"
                      content-class="top-tooltip pa-5"
                      transition="fade-transition"
                      data-test-id="organization-tooltip"
                    >
                      <template #activator="{ props }">
                        <span
                          v-bind="props"
                        ><u> issued from Canada or the United States</u></span>
                      </template>
                      If the death certificate was issued outside of Canada or the US, the transfer will have to be sent
                      to the Manufactured Home Registry.
                    </v-tooltip>, and the name on the death certificate matches the name displayed above exactly.
                  </p>
                </li>
                <li
                  v-if="isRoleStaff"
                  class="pl-3"
                  :class="{ 'pt-0' : isTransferWithoutBillOfSale }"
                  data-test-id="change-ownership-section"
                >
                  <p><strong>Transfer or Change Ownership form</strong> has been received and retained.</p>
                </li>
                <li
                  v-if="isRoleQualifiedSupplier && isTransferDueToSaleOrGift"
                  class="pl-3"
                  data-test-id="change-ownership-qs"
                >
                  <p><strong>Transfer or Change Ownership form</strong> has been received and retained.</p>
                </li>
                <li
                  v-if="isRoleStaff && (isTransferBillOfSale || isTransferWithoutBillOfSale)"
                  class="pl-3"
                  data-test-id="certified-copy-section"
                >
                  <p>
                    <strong>Certified copy of trust deed or trust agreement</strong> has been received and
                    retained if this is a transfer to trustee of a trust.
                  </p>
                </li>
                <li
                  v-if="isTransferToExecutorProbateWill"
                  class="pl-3"
                  data-test-id="probate-will-section"
                >
                  <p>
                    <strong>Court certified true copy of the Grant of Probate with the will attached </strong>
                    has been received and retained.
                  </p>
                </li>
                <li
                  v-if="isTransferToAdminNoWill"
                  class="pl-3"
                >
                  <p>
                    <strong>Court certified true copy of the Grant of Administration</strong> has been received and
                    retained.
                  </p>
                </li>
                <li
                  v-if="isTransferToAdminNoWill"
                  class="pl-3"
                >
                  <p>
                    <strong>Affidavit of Administration with List of Assets and Liabilities</strong> has been received
                    and retained.
                  </p>
                </li>
                <li
                  v-if="isTransferToExecutorUnder25Will"
                  class="pl-3"
                >
                  <p><strong>Certified true copy of the will</strong> has been received and retained.</p>
                </li>
                <li
                  v-if="isTransferToExecutorUnder25Will || isTransferToExecutorProbateWill"
                  class="pl-3"
                >
                  <p><strong>Original signed Affidavit of Executor form</strong> has been received and retained.</p>
                </li>
                <li
                  v-if="isRoleStaff && (isTransferBillOfSale || isTransferWithoutBillOfSale)"
                  class="pl-3"
                  data-test-id="trans-no-bill-sale"
                >
                  <p>
                    <strong>Additional supporting documents</strong> required for this transfer type, if applicable,
                    have been received and retained.
                  </p>
                </li>
                <li
                  v-if="isTransferDueToSaleOrGift || isTransferWithoutBillOfSale"
                  class="pl-3"
                  data-test-id="confirm-search-sale-or-gift"
                >
                  <p>
                    <strong>Search of the Corporate Register</strong> has been completed if one or more of the
                    current or future registered owners is an incorporated organization including a corporation,
                    society or cooperative association.
                  </p>
                  <p class="confirm-completion-note">
                    <strong>Note: </strong> For current registered owners, the incorporated organization must have
                    been active (good legal standing) on the Corporate Register at the time the bill of sale was
                    signed. Future registered owners must be active (good legal standing) at the time of this
                    registration.
                  </p>
                </li>
                <li
                  v-else-if="!isTransferDueToDeath"
                  class="pl-3"
                  data-test-id="confirm-search-section"
                >
                  <p>
                    <strong>Search of the Corporate Register</strong> has been completed if one or more of the
                    current or future registered owners is an incorporated organization including a corporation,
                    society or cooperative association.
                  </p>
                  <p class="confirm-completion-note">
                    <strong>Note:</strong> For current registered owners the incorporated business must have been
                    active on the Corporate Register at the time the bill of sale was signed. Future owners must
                    be in active status at the time of registration.
                  </p>
                </li>
                <li
                  v-if="(isTransferBillOfSale || isTransferWithoutBillOfSale) && isRoleStaff ||
                    isTransferToSurvivingJointTenant"
                  class="pl-3"
                  data-test-id="ppr-lien-sale-or-gift"
                >
                  <p>
                    <strong>Personal Property Registry lien search</strong> has been completed and there are no liens
                    that block the transfer. PPR registrations that block the transfer include the following:
                  </p>
                  <ul>
                    <li>
                      Marriage/Separation Agreement Affecting Manufactured Home
                    </li>
                    <li>
                      Land Tax Deferment Lien on a Manufactured Home
                    </li>
                    <li>
                      Maintenance Lien
                    </li>
                    <li>
                      Manufactured Home Notice
                    </li>
                    <li>
                      Possession under s.30 of the Sale of Goods Act
                    </li>
                  </ul>
                </li>
                <li
                  v-else-if="(isTransferDueToSaleOrGift && isRoleQualifiedSupplier) || isTransferDueToDeath"
                  class="pl-3"
                  data-test-id="ppr-lien-section-blockers"
                >
                  <p>
                    <strong>Personal Property Registry lien search</strong> has been completed and there are no liens
                    that block the transfer. PPR registrations that block the transfer include the following:
                  </p>
                  <ul>
                    <li>
                      Marriage/Separation Agreement Affecting Manufactured Home
                    </li>
                    <li>
                      Land Tax Deferment Lien on a Manufactured Home
                    </li>
                    <li>
                      Maintenance Lien
                    </li>
                    <li>
                      Manufactured Home Notice
                    </li>
                    <li>
                      Possession under s.30 of the Sale of Goods Act
                    </li>
                  </ul>
                </li>
                <li
                  v-else
                  class="pl-3 pb-0"
                  data-test-id="ppr-lien-section"
                >
                  <p>
                    <strong>Personal Property Registry lien search</strong> has been completed and there are no liens
                    on the home that stop the transfer.
                  </p>
                  <p class="confirm-completion-note">
                    <span>Note: </span> Liens that stop the transfer include Family Maintenance Enforcement Act, Family
                    Relations Act, BC Second Mortgage, Land Tax Deferment Act.
                  </p>
                </li>
                <li
                  v-if="isTransferDueToSaleOrGift && isRoleQualifiedSupplier"
                  class="pl-3 pb-0 mb-0"
                  data-test-id="file-store-section"
                >
                  <p>
                    <strong>All filed documents will be stored for 7 years.</strong> If requested, a copy or certified
                    copy of filed documents (such as the Bill of Sale, or other signed forms), will be provided within
                    7 business days, at the fee level set by the Registrar.
                  </p>
                </li>
              </ol>
            </slot>
          </v-col>
        </v-row>
        <v-row
          no-gutters
          class="mt-3"
        >
          <v-col cols="3">
            <v-spacer />
          </v-col>
          <v-col
            cols="9"
            class="ml-n4"
          >
            <v-checkbox
              id="checkbox-confirmed"
              v-model="confirmCompletion"
              class="pb-7 pt-5 px-4 my-0 confirm-checkbox"
              hide-details
              data-test-id="confirm-completion-checkbox"
              :ripple="false"
            >
              <template #label>
                <span
                  data-test-id="confirm-checkbox-label"
                  :class="{ 'error-text': showErrorComponent }"
                >
                  <span v-if="isAmendTransportPermit">I, <strong>{{ legalName }}</strong>,
                    confirm that I am duly authorized to submit this Transport Permit and I
                    understand the conditions and have complied with the requirements listed above.
                  </span>
                  <span v-else-if="isTransportPermit || isCancelChangeLocationActive">
                    I, <strong>{{ legalName }}</strong>,
                    confirm that I am duly authorized to submit this registration and I
                    understand the conditions and have complied with the requirements listed above.
                  </span>
                  <span v-else>I, <strong>{{ legalName }}</strong>,
                    confirm that all of the requirements listed above have been completed.
                  </span>
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
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { ApiTransferTypes } from '@/enums'
import { useTransferOwners, useTransportPermits } from '@/composables'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'ConfirmCompletion',
  props: {
    sectionNumber: {
      type: Number,
      default: null
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
      isRoleStaff,
      isRoleQualifiedSupplier
    } = storeToRefs(useStore())

    const {
      isTransferDueToDeath,
      isTransferWithoutBillOfSale,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      isTransferBillOfSale,
      isTransferDueToSaleOrGift,
      isTransferToSurvivingJointTenant
    } = useTransferOwners()

    const {
      isChangeLocationActive,
      isChangeLocationEnabled,
      isAmendLocationActive,
      isCancelChangeLocationActive
    } = useTransportPermits()

    const localState = reactive({
      showErrorComponent: computed((): boolean => {
        return (props.setShowErrors && !localState.confirmCompletion)
      }),
      isAmendTransportPermit: computed((): boolean =>
        isChangeLocationEnabled.value && isChangeLocationActive.value && isAmendLocationActive.value),
      isTransportPermit: computed((): boolean =>
        isChangeLocationEnabled.value && isChangeLocationActive.value),
      confirmCompletion: false,
    })

    watch(
      () => localState.confirmCompletion,
      (val: boolean) => {
        emit('confirmCompletion', val)
      }
    )

    return {
      isRoleStaff,
      isRoleQualifiedSupplier,
      ApiTransferTypes,
      isTransferDueToDeath,
      isTransferWithoutBillOfSale,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      isTransferBillOfSale,
      isTransferDueToSaleOrGift,
      isTransferToSurvivingJointTenant,
      isCancelChangeLocationActive,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
#transfer-confirm {
  p {
    color: $gray7;
  }

  .confirm-completion-req, :slotted(*) {
    ol {
      padding-left: 27px !important;
    }
    ol:not([type="a"])>li:not(:last-child) {
      border-bottom: 1px solid $gray3;

      ::marker {
        font-weight: normal;
      }
    }
    ol>li {
      padding: 25px 0;
      padding-left: unset;
    }
    ol>li::marker {
      font-weight: normal;
    }
    ul {
      margin-bottom: 16px;
      padding-top: 15px;
      margin-left: 20px;
      list-style-position: outside;

      li {
        padding-left: 10px;
        border-bottom: none !important;
      }
    }
    li {
      padding-left: 15px;
      border: 0;
    }
    .font-normal ol li ::marker {
      font-weight: normal;
    }
    .underline {
      border-bottom: 1px dotted $gray7;
      text-decoration: none;
    }
  }
  .confirm-completion-note {
    margin-top: 20px;
    font-size: 14px;
    line-height: 22px;
  }

  u {
    border-bottom: 1px dotted #000;
    text-decoration: none;
  }

  :deep(.confirm-checkbox) {
    background-color: $gray1;
    font-size: 16px;
    line-height: 24px;
    vertical-align: top;

    .v-selection-control {
      align-items: baseline;
    }
    .v-selection-control__wrapper {
      top: 3px;
    }
    .v-input__control .v-input__slot {
      align-items: flex-start;
    }
  }
}
</style>
