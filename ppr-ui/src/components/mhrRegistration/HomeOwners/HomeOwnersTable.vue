<template>
  <v-card
    id="home-owner-table-card"
    flat
    rounded
    role="region"
    :class="{ 'border-error-left': showTableError && !hideTableErrors }"
  >
    <v-table
      id="mhr-home-owners-table"
      class="home-owners-table"
      item-key="groupId"
      role="presentation"
      :class="{ 'review-mode': isReadonlyTable }"
      :group-by="showGroups ? 'groupId' : null"
    >
      <thead class="simple">
        <tr>
          <th
            v-for="header in homeOwnersTableHeaders"
            :key="header.value"
            :class="header.class"
            :aria-label="header.text || header.value"
            :aria-hidden="header.value === 'actions'"
          >
            {{ header.text }}
          </th>
        </tr>
      </thead>
      <tbody v-if="homeOwners.length > 0">
        <tr
          v-for="(group, groupIndex) in homeOwnerGroups"
          :key="`${group}: ${groupIndex}`"
        >
          <td
            class="pa-0"
            colspan="4"
          >
            <!-- Start of Home Owner Group -->
            <div
              v-if="
                groupIndex === 0 &&
                  (isMhrTransfer || isMhrCorrection) &&
                  !hasActualOwners(group.owners) &&
                  group.owners.length > 0 &&
                  hasRemovedAllHomeOwnerGroups() &&
                  !isTransferToExecutorProbateWill &&
                  !isTransferToExecutorUnder25Will &&
                  !isTransferToAdminNoWill
              "
            >
              <div
                v-if="!isTransferToSurvivingJointTenant"
                class="pa-6 fs-14 text-center no-owners-head-row"
                data-test-id="no-data-msg"
              >
                No owners added yet.
              </div>
              <div
                v-else
                class="error-text pa-6 fs-14 text-center"
              >
                Must contain at least one owner.
              </div>
              <v-divider class="mx-0" />
            </div>

            <div
              v-if="(forceShowGroups === undefined ? showGroups : forceShowGroups) &&
                !(disableGroupHeader(group.groupId) && (hideRemovedOwners || isReadonlyTable))"
              :colspan="4"
              class="py-3 group-header-slot"
              :class="{
                'spacer-header': disableGroupHeader(group.groupId),
                'border-error-left': isInvalidOwnerGroup(group.groupId)
              }"
            >
              <TableGroupHeader
                :group-id="group.groupId"
                :group-number="getGroupNumberById(group.groupId)"
                :owners="hasActualOwners(group.owners) ? group.owners : []"
                :owner-groups="homeOwnerGroups"
                :show-edit-actions="showEditActions && enableTransferOwnerGroupActions()"
                :disable-group-header="disableGroupHeader(group.groupId)"
                :is-mhr-transfer="isMhrTransfer"
              />
            </div>
            <!-- End of Table Group Header -->

            <div
              v-for="(item, index) in group.owners"
              :key="`${item}: ${index}`"
              class="owner-row"
            >
              <!-- Transfer scenario: Display error for groups that 'removed' all owners
               but they still exist in the table -->
              <div v-if="isGroupWithNoOwners(item.groupId, index) || isTransferGroupInvalid(group.groupId, index)">
                <div
                  class="py-1 bottom-border"
                  :class="{ 'border-error-left': isInvalidOwnerGroup(group.groupId) }"
                  data-test-id="invalid-group-msg"
                >
                  <div
                    class="error-text my-6 text-center"
                    :data-test-id="`no-owners-msg-group-${homeOwners.indexOf(item)}`"
                  >
                    <HomeOwnersGroupError :group-id="group.groupId" />
                  </div>
                </div>
              </div>

              <tr
                v-else-if="!isMhrTransfer && !isMhrCorrection &&
                  index === 0 && hasMixedOwnersInGroup(item.groupId) && !isReadonlyTable"
                class="d-block"
              >
                <!-- Mixed owners error for Registrations -->
                <HomeOwnersMixedRolesError
                  :group-id="item.groupId"
                  :show-border-error="isInvalidOwnerGroup(item.groupId)"
                />
              </tr>

              <template v-if="isCurrentlyEditing(homeOwners.indexOf(item))">
                <div
                  class="pa-0"
                  :colspan="homeOwnersTableHeaders.length"
                >
                  <v-expand-transition>
                    <AddEditHomeOwner
                      :edit-home-owner="item"
                      :is-home-owner-person="!item.organizationName"
                      :is-mhr-transfer="isMhrTransfer"
                      :show-table-error="validateTransfer && (isAddingMode || isEditingMode)"
                      :disable-owner-removal="isDisabledForSJTChanges(item) || isDisabledForWillChanges(item)"
                      @cancel="currentlyEditingHomeOwnerId = -1"
                      @remove="removeOwnerHandler(item)"
                    />
                  </v-expand-transition>
                </div>
              </template>

              <div
                v-else-if="item.ownerId"
                :key="`owner-row-key-${homeOwners.indexOf(item)}`"
                class="owner-row owner-info"
                :class="{
                  'border-error-left': isInvalidOwnerGroup(item.groupId),
                  'no-bottom-border': (isRemovedHomeOwner(item) &&
                    (showDeathCertificate() || showSupportingDocuments()) &&
                    isReadonlyTable)
                }"
                :data-test-id="`owner-info-${item.ownerId}`"
              >
                <!-- Start of Name -->
                <td
                  class="owner-name pr-6"
                  :class="[
                    {
                      'no-bottom-border': hideRowBottomBorder(item),
                    },
                    homeOwnersTableHeaders[0].class
                  ]"
                >
                  <div :class="{ 'removed-owner': isRemovedHomeOwner(item) }">
                    <span
                      v-if="item.individualName"
                      class="owner-icon-name"
                      aria-label="Person"
                    >
                      <v-icon
                        class="mr-2"
                        :class="{ 'person-executor-icon': item.partyType !== HomeOwnerPartyTypes.OWNER_IND }"
                      >
                        {{ getHomeOwnerIcon(item.partyType) }}
                      </v-icon>
                      <span class="font-weight-bold">
                        {{ item.individualName.first }}
                        {{ item.individualName.middle }}
                        {{ item.individualName.last }}
                      </span>
                    </span>
                    <span
                      v-else
                      class="owner-icon-name"
                      aria-label="Business"
                    >
                      <v-icon
                        class="mr-2"
                        :class="{ 'business-executor-icon': item.partyType !== HomeOwnerPartyTypes.OWNER_BUS }"
                      >
                        {{ getHomeOwnerIcon(item.partyType, true) }}
                      </v-icon>
                      <div class="font-weight-bold">
                        {{ item.organizationName }}
                      </div>
                    </span>

                    <div
                      v-if="item.partyType === HomeOwnerPartyTypes.OWNER_IND ||
                        item.partyType === HomeOwnerPartyTypes.OWNER_BUS"
                      class="font-light suffix"
                    >
                      {{ item.suffix }}
                    </div>
                    <div
                      v-else
                      class="font-light description"
                    >
                      {{ item.description }}
                    </div>
                  </div>

                  <!-- Hide Chips for Review Mode -->
                  <template v-if="(isMhrCorrection || isMhrTransfer) && (!isReadonlyTable || showChips)">
                    <InfoChip
                      class="ml-8 mt-2"
                      :action="mapInfoChipAction(item)"
                    />
                  </template>
                </td>
                <!-- End of Name -->

                <td :class="[{ 'no-bottom-border': hideRowBottomBorder(item) }, homeOwnersTableHeaders[1].class]">
                  <base-address
                    :schema="addressSchema"
                    :value="item.address"
                    :class="{ 'removed-owner': isRemovedHomeOwner(item) }"
                  />
                </td>
                <!-- End of Address -->

                <td :class="[{ 'no-bottom-border': hideRowBottomBorder(item) }, homeOwnersTableHeaders[2].class]">
                  <div :class="{ 'removed-owner': isRemovedHomeOwner(item) }">
                    {{ toDisplayPhone(item.phoneNumber) }}
                    <span v-if="item.phoneExtension"> Ext {{ item.phoneExtension }} </span>
                  </div>
                </td>
                <!-- End of Phone -->

                <td
                  v-if="showEditActions"
                  class="row-actions text-right"
                  :class="[{ 'no-bottom-border': hideRowBottomBorder(item) }, homeOwnersTableHeaders[3].class]"
                >
                  <!-- New Owner Actions -->
                  <div
                    v-if="(isMhrCorrection && isAddedHomeOwner(item)) ||
                      ((!isMhrTransfer && !isMhrCorrection) || isAddedHomeOwner(item)) && enableHomeOwnerChanges()"
                    class="mr-n4"
                  >
                    <v-btn
                      variant="plain"
                      color="primary"
                      class="mr-n4"
                      :ripple="false"
                      :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                      data-test-id="table-edit-btn"
                      @click="openForEditing(homeOwners.indexOf(item))"
                    >
                      <v-icon size="small">
                        mdi-pencil
                      </v-icon>
                      <span>Edit</span>
                      <v-divider
                        class="ma-0 pl-3"
                        vertical
                      />
                    </v-btn>
                    <!-- Actions drop down menu -->
                    <v-menu location="bottom right">
                      <template #activator="{ props }">
                        <v-btn
                          variant="plain"
                          color="primary"
                          class="menu-drop-down-btn px-0 mr-n4"
                          :disabled="isAddingMode || isGlobalEditingMode"
                          v-bind="props"
                        >
                          <v-icon>mdi-menu-down</v-icon>
                        </v-btn>
                      </template>

                      <!-- More actions drop down list -->
                      <v-list class="actions-dropdown actions__more-actions">
                        <v-list-item
                          class="my-n2"
                          @click="remove(item)"
                        >
                          <v-list-item-subtitle class="pa-0">
                            <v-icon
                              size="small"
                              style="margin-bottom: 3px"
                            >
                              mdi-delete
                            </v-icon>
                            <span class="ml-1 remove-btn-text">Remove Owner</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>
                  <!-- End of Owner Actions -->

                  <!-- Owner Corrections -->
                  <div
                    v-else-if="isMhrCorrection"
                    class="mr-n5"
                  >
                    <v-btn
                      v-if="!item?.action"
                      variant="plain"
                      color="primary"
                      class="mr-n4"
                      :ripple="false"
                      :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                      data-test-id="table-edit-btn"
                      @click="openForEditing(homeOwners.indexOf(item))"
                    >
                      <v-icon size="small">
                        mdi-pencil
                      </v-icon>
                      <span>{{ correctAmendLabel }}</span>
                      <v-divider
                        class="ma-0 pl-3"
                        vertical
                      />
                    </v-btn>
                    <v-btn
                      v-if="showCorrectUndoOptions(item)"
                      variant="plain"
                      color="primary"
                      :class="{'mr-3' : isRemovedHomeOwner(item) }"
                      :ripple="false"
                      :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                      data-test-id="table-undo-btn"
                      @click="undo(item)"
                    >
                      <v-icon size="small">
                        mdi-undo
                      </v-icon>
                      <span>Undo</span>
                      <v-divider
                        v-if="!isRemovedHomeOwner(item)"
                        class="ma-0 pl-3 mr-n5"
                        vertical
                      />
                    </v-btn>
                    <!-- Actions drop down menu -->
                    <v-menu
                      v-if="!isRemovedHomeOwner(item)"
                      location="bottom right"
                      class="mr-n4"
                    >
                      <template #activator="{ props }">
                        <v-btn
                          variant="plain"
                          color="primary"
                          class="menu-drop-down-btn"
                          :disabled="isAddingMode || isGlobalEditingMode"
                          v-bind="props"
                        >
                          <v-icon>mdi-menu-down</v-icon>
                        </v-btn>
                      </template>

                      <!-- More actions drop down list -->
                      <v-list class="actions-dropdown actions__more-actions">
                        <v-list-item
                          v-if="isCorrectedOwner(item)"
                          class="my-n2"
                          @click="openForEditing(homeOwners.indexOf(item))"
                        >
                          <v-list-item-subtitle class="pa-0">
                            <v-icon
                              size="small"
                              style="margin-bottom: 3px"
                            >
                              mdi-pencil
                            </v-icon>
                            <span class="ml-1 remove-btn-text">{{ correctAmendLabel }}</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                        <v-list-item
                          class="my-n2"
                          @click="markForRemoval(item)"
                        >
                          <v-list-item-subtitle class="pa-0">
                            <v-icon
                              size="small"
                              style="margin-bottom: 3px"
                            >
                              mdi-delete
                            </v-icon>
                            <span class="ml-1 remove-btn-text">Delete Owner</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>

                  <!-- Existing Owner Actions -->
                  <template v-else-if="enableTransferOwnerActions(item)">
                    <v-btn
                      v-if="!isRemovedHomeOwner(item) &&
                        !isChangedOwner(item) &&
                        !(!isPartyTypeNotEAT(item) && isTransferToSurvivingJointTenant) &&
                        !isDisabledForSJTChanges(item) &&
                        !isDisabledForWillChanges(item)"
                      variant="plain"
                      color="primary"
                      class="mr-n4"
                      :ripple="false"
                      :disabled="
                        isAddingMode ||
                          isEditingMode ||
                          isGlobalEditingMode"
                      data-test-id="table-delete-btn"
                      @click="markForRemoval(item)"
                    >
                      <v-icon size="small">
                        mdi-delete
                      </v-icon>
                      <span>Delete Owner</span>
                      <v-divider
                        v-if="enableTransferOwnerMenuActions(item)"
                        class="ma-0 pl-3"
                        vertical
                      />
                    </v-btn>

                    <template v-if="isRemovedHomeOwner(item) || isChangedOwner(item)">
                      <v-btn
                        variant="plain"
                        color="primary"
                        class="mx-0 px-0"
                        :ripple="false"
                        :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                        data-test-id="table-undo-btn"
                        @click="undo(item)"
                      >
                        <v-icon size="small">
                          mdi-undo
                        </v-icon>
                        <span>Undo</span>
                        <v-divider
                          v-if="enableTransferOwnerMenuActions(item) && !isRemovedHomeOwner(item)"
                          class="ma-0 pl-3"
                          vertical
                        />
                      </v-btn>

                      <v-menu
                        v-if="isChangedOwner(item) && (isDisabledForSJTChanges(item) || isDisabledForWillChanges(item))"
                        location="bottom right"
                      >
                        <template #activator="{ props }">
                          <v-btn
                            variant="plain"
                            color="primary"
                            class="menu-drop-down-btn mr-n4"
                            :disabled="isAddingMode || isGlobalEditingMode || isDisabledForSJTChanges(item)"
                            v-bind="props"
                          >
                            <v-icon>mdi-menu-down</v-icon>
                          </v-btn>
                        </template>

                        <!-- More actions drop down list -->
                        <v-list class="actions-dropdown actions__more-actions">
                          <!-- Menu Edit Option -->
                          <v-list-item
                            class="my-n2"
                            @click="openForEditing(homeOwners.indexOf(item))"
                          >
                            <v-list-item-subtitle class="pa-0">
                              <v-icon
                                size="small"
                                class="mb-1"
                              >
                                mdi-pencil
                              </v-icon>
                              <span class="ml-1 remove-btn-text">Change Details</span>
                            </v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </template>

                    <!-- Change Details when other actions are disabled -->
                    <v-btn
                      v-else-if="isDisabledForSJTChanges(item) || isDisabledForWillChanges(item)"
                      variant="plain"
                      color="primary"
                      class="mx-0 px-0"
                      :ripple="false"
                      data-test-id="owner-change-details-btn"
                      @click="openForEditing(homeOwners.indexOf(item))"
                    >
                      <v-icon size="small">
                        mdi-pencil
                      </v-icon>
                      <span>Change Details</span>
                    </v-btn>

                    <!-- Menu actions drop down menu -->
                    <template
                      v-if="enableTransferOwnerMenuActions(item) &&
                        !isRemovedHomeOwner(item) &&
                        !(!isPartyTypeNotEAT(item) && isTransferToSurvivingJointTenant) &&
                        !isDisabledForSJTChanges(item) &&
                        !isDisabledForWillChanges(item)"
                    >
                      <v-menu location="bottom right">
                        <template #activator="{ props }">
                          <v-btn
                            variant="plain"
                            color="primary"
                            class="menu-drop-down-btn mr-n4"
                            :disabled="isAddingMode || isGlobalEditingMode || isDisabledForSJTChanges(item)"
                            v-bind="props"
                          >
                            <v-icon>mdi-menu-down</v-icon>
                          </v-btn>
                        </template>

                        <!-- More actions drop down list -->
                        <v-list class="actions-dropdown actions__more-actions">
                          <!-- Menu Edit Option -->
                          <v-list-item
                            class="my-n2"
                            @click="openForEditing(homeOwners.indexOf(item))"
                          >
                            <v-list-item-subtitle class="pa-0">
                              <v-icon
                                size="small"
                                class="mb-1"
                              >
                                mdi-pencil
                              </v-icon>
                              <span class="ml-1 remove-btn-text">Change Details</span>
                            </v-list-item-subtitle>
                          </v-list-item>

                          <!-- Menu Delete Option -->
                          <v-list-item
                            v-if="isChangedOwner(item)"
                            class="my-n2"
                            @click="removeChangeOwnerHandler(item)"
                          >
                            <v-list-item-subtitle class="pa-0">
                              <v-icon
                                size="small"
                                class="mb-1"
                              >
                                mdi-delete
                              </v-icon>
                              <span class="ml-1 remove-btn-text">Delete Owner</span>
                            </v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </template>
                  </template>
                  <template v-else-if="!!getMhrTransferType?.transferType">
                    <template v-if="isRemovedHomeOwner(item) || isChangedOwner(item)">
                      <v-btn
                        variant="plain"
                        color="primary"
                        class="mx-0 px-0"
                        :ripple="false"
                        :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                        data-test-id="table-undo-btn"
                        @click="undo(item)"
                      >
                        <v-icon size="small">
                          mdi-undo
                        </v-icon>
                        <span>Undo</span>
                        <v-divider
                          v-if="enableTransferOwnerMenuActions(item) && !isRemovedHomeOwner(item)"
                          class="ma-0 pl-3"
                          vertical
                        />
                      </v-btn>

                      <v-menu
                        v-if="isChangedOwner(item)"
                        location="bottom right"
                      >
                        <template #activator="{ props }">
                          <v-btn
                            variant="plain"
                            color="primary"
                            class="menu-drop-down-btn mr-n4"
                            :disabled="isAddingMode || isGlobalEditingMode"
                            v-bind="props"
                          >
                            <v-icon>mdi-menu-down</v-icon>
                          </v-btn>
                        </template>

                        <!-- More actions drop down list -->
                        <v-list class="actions-dropdown actions__more-actions">
                          <!-- Menu Edit Option -->
                          <v-list-item
                            class="my-n2"
                            @click="openForEditing(homeOwners.indexOf(item))"
                          >
                            <v-list-item-subtitle class="pa-0">
                              <v-icon
                                size="small"
                                class="mb-1"
                              >
                                mdi-pencil
                              </v-icon>
                              <span class="ml-1 remove-btn-text">Change Details</span>
                            </v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </template>
                    <!-- Change Details when other actions are disabled -->
                    <v-btn
                      v-else
                      variant="plain"
                      color="primary"
                      class="mx-0 px-0"
                      :ripple="false"
                      data-test-id="owner-change-details-btn"
                      @click="openForEditing(homeOwners.indexOf(item))"
                    >
                      <v-icon size="small">
                        mdi-pencil
                      </v-icon>
                      <span>Change Details</span>
                    </v-btn>
                  </template>
                </td>
              </div>

              <!-- For MHR scenarios where users can entirely remove added owners -->
              <tr v-else-if="!hideRemovedOwners && !showGroups">
                <div
                  class="my-6 text-center"
                  data-test-id="no-owners-mgs"
                >
                  No owners added yet.
                </div>
              </tr>
              <tr
                v-if="isRemovedHomeOwner(item) && showDeathCertificate() && !isReadonlyTable"
                class="death-certificate-row"
              >
                <td
                  :colspan="homeOwnersTableHeaders.length"
                  class="pt-0 px-8"
                  :class="{ 'border-error-left': isInvalidOwnerGroup(item.groupId) }"
                >
                  <v-expand-transition class="ml-4">
                    <BusinessRemovalForm
                      v-if="item.partyType === HomeOwnerPartyTypes.OWNER_BUS"
                      :historical-owner="item"
                      :validate="validateTransfer"
                    />
                    <DeathCertificate
                      v-else
                      :deceased-owner="item"
                      :validate="validateTransfer"
                    />
                  </v-expand-transition>
                </td>
              </tr>
              <tr
                v-else-if="isRemovedHomeOwner(item) &&
                  (showDeathCertificate() || showSupportingDocuments()) &&
                  isReadonlyTable"
                class="owner-info"
              >
                <td
                  v-if="(item.deathCorpNumber || item.deathDateTime) &&
                    item.partyType === HomeOwnerPartyTypes.OWNER_BUS"
                  :colspan="homeOwnersTableHeaders.length"
                  class="deceased-review-info pt-0 mt-1 mb-2"
                >
                  <v-row
                    no-gutters
                    class="ml-8"
                  >
                    <v-col cols="12">
                      <p class="generic-label mt-2">
                        <span class="fs-14">Incorporation or Registration Number:</span>
                        <span class="font-light mx-1">{{ item.deathCorpNumber }}</span>
                      </p>
                      <p class="generic-label">
                        <span class="fs-14">Date of Dissolution or Cancellation:</span>
                        <span class="font-light mx-1">{{ yyyyMmDdToPacificDate(item.deathDateTime, true) }}</span>
                      </p>
                    </v-col>
                  </v-row>
                </td>
                <td
                  v-if="item.supportingDocument || showDeathCertificate()"
                  :colspan="homeOwnersTableHeaders.length"
                  class="deceased-review-info pt-0 mt-1 mb-2"
                >
                  <v-row
                    no-gutters
                    class="ml-8"
                  >
                    <v-col cols="12">
                      <div
                        v-if="item.supportingDocument === SupportingDocumentsOptions.AFFIDAVIT"
                        data-test-id="affidavit-review-note"
                      >
                        <div class="generic-label-14">
                          Affidavit of Executor with Death Certificate
                        </div>
                        <div>
                          Note: Ensure you have the original signed Affidavit of Executor form and a court certified
                          true copy of the will.
                        </div>
                        <p class="generic-label mt-2">
                          <span class="fs-14">Death Certificate Registration Number:</span>
                          <span class="font-light mx-1">{{ item.deathCertificateNumber }}</span>
                        </p>
                        <p class="generic-label">
                          <span class="fs-14">Date of Death:</span>
                          <span class="font-light mx-1">{{ yyyyMmDdToPacificDate(item.deathDateTime, true) }}</span>
                        </p>
                      </div>
                      <div
                        v-if="item.supportingDocument === SupportingDocumentsOptions.DEATH_CERT ||
                          showDeathCertificate()"
                        data-test-id="death-cert-review-note"
                      >
                        <p
                          v-if="item.deathCertificateNumber"
                          class="generic-label"
                        >
                          <span class="fs-14">Death Certificate Registration Number:</span>
                          <span class="font-light mx-1">{{ item.deathCertificateNumber }}</span>
                        </p>
                        <p
                          v-else
                          class="generic-label"
                        >
                          <span class="fs-14">Incorporation or Registration Number:</span>
                          <span class="font-light mx-1">{{ item.deathCorpNumber }}</span>
                        </p>
                        <p class="generic-label">
                          <span class="fs-14">
                            Date of {{ item.deathCorpNumber ? 'Dissolution or Cancellation' : 'Death' }}:
                          </span>
                          <span class="font-light mx-1">{{ yyyyMmDdToPacificDate(item.deathDateTime, true) }}</span>
                        </p>
                      </div>
                      <div
                        v-else-if="item.supportingDocument === SupportingDocumentsOptions.PROBATE_GRANT"
                        data-test-id="grant-review-note"
                      >
                        <div class="generic-label-14">
                          Grant of Probate with Will
                        </div>
                        <div>
                          Note: Ensure you have a court certified true copy of the Grant of Probate with the will
                          attached.
                        </div>
                      </div>
                      <div
                        v-else-if="item.supportingDocument === SupportingDocumentsOptions.ADMIN_GRANT"
                      >
                        <div class="generic-label-14">
                          Grant of Administration
                        </div>
                        <div>
                          Note: Ensure you have the original court certified true copy of Grant of
                          Administration and Affidavit of Administration with list of Assets and Liabilities.
                        </div>
                      </div>
                    </v-col>
                  </v-row>
                </td>
              </tr>

              <tr
                v-else-if="isRemovedHomeOwner(item) &&
                  showSupportingDocuments() &&
                  !isReadonlyTable &&
                  isPartyTypeNotEAT(item)"
                class="d-block"
              >
                <td
                  :colspan="homeOwnersTableHeaders.length"
                  class="px-14 d-block"
                  :class="{ 'border-error-left': isInvalidOwnerGroup(group.groupId) }"
                >
                  <BusinessRemovalForm
                    v-if="item.partyType === HomeOwnerPartyTypes.OWNER_BUS"
                    :historical-owner="item"
                    :validate="validateTransfer"
                  />
                  <v-expand-transition v-else>
                    <SupportingDocuments
                      :key="item.ownerId"
                      :deleted-owner="item"
                      :validate="validateTransfer"
                      :is-second-option-disabled="TransToExec.hasOnlyOneOwnerInGroup(item.groupId)"
                      :is-second-option-error="TransToExec.isAllGroupOwnersWithDeathCerts(item.groupId)"
                      :has-death-cert-for-first-option="isTransferToExecutorUnder25Will"
                      @handle-doc-option-one-selected="TransToExec.resetGrantOfProbate(group.groupId, item.ownerId)"
                    >
                      <template #deathCert>
                        <DeathCertificate
                          :deceased-owner="item"
                          :validate="validateTransfer"
                          :is-disabled="isGlobalEditingMode"
                        />
                      </template>
                    </SupportingDocuments>
                  </v-expand-transition>
                </td>
              </tr>
            </div>
            <div
              v-if="group.owners.length === 0"
              class="error-text my-6 text-center"
              data-test-id="no-owners-err-msg"
            >
              Group must contain at least one owner.
            </div>
          </td>
        </tr>
      </tbody>

      <!-- No Data -->
      <tbody v-else>
        <tr>
          <td
            :colspan="homeOwnersTableHeaders.length"
            class="pa-7 text-center"
            data-test-id="no-data-msg"
          >
            No owners added yet.
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-card>
  <BaseDialog
    :set-options="mhrDeceasedOwnerChanges"
    :set-display="showOwnerChangesDialog"
    @proceed="handleOwnerChangesDialogResp($event)"
  />
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { homeOwnersTableHeaders, homeOwnersTableHeadersReview } from '@/resources/tableHeaders'
import {
  useHomeOwners,
  useMhrCorrections,
  useMhrInfoValidation,
  useMhrValidations,
  useTransferOwners
} from '@/composables'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { toDisplayPhone } from '@/utils'
import { AddEditHomeOwner } from '@/components/mhrRegistration/HomeOwners'
import HomeOwnersMixedRolesError from './HomeOwnersMixedRolesError.vue'
import {
  BusinessRemovalForm,
  DeathCertificate,
  HomeOwnersGroupError,
  SupportingDocuments
} from '@/components/mhrTransfers'
import TableGroupHeader from '@/components/mhrRegistration/HomeOwners/TableGroupHeader.vue'
import { mhrDeceasedOwnerChanges } from '@/resources/dialogOptions'
import { yyyyMmDdToPacificDate } from '@/utils/date-helper'
import { InfoChip } from '@/components/common'
import type { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { ActionTypes, HomeOwnerPartyTypes, HomeTenancyTypes, SupportingDocumentsOptions } from '@/enums'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'HomeOwnersTable',
  components: {
    BaseAddress,
    BusinessRemovalForm,
    AddEditHomeOwner,
    TableGroupHeader,
    SupportingDocuments,
    DeathCertificate,
    InfoChip,
    HomeOwnersGroupError,
    HomeOwnersMixedRolesError
  },
  props: {
    homeOwnerGroups: {
      type: Array as () => MhrRegistrationHomeOwnerGroupIF[],
      default: () => []
    },
    isAdding: {
      type: Boolean,
      default: false
    },
    isReadonlyTable: { type: Boolean, default: false },
    isMhrTransfer: { type: Boolean, default: false },
    hideRemovedOwners: { type: Boolean, default: false },
    showChips: { type: Boolean, default: false },
    validateTransfer: { type: Boolean, default: false },
    hideTableErrors: { type: Boolean, default: false },
    forceShowGroups: { type: Boolean, default: undefined } // used in Mhr Re-Registration flow for Previous Owners
  },
  emits: ['isValidTransferOwners', 'handleUndo'],
  setup (props, context) {
    const addressSchema = PartyAddressSchema
    const { setUnsavedChanges } = useStore()
    const {
      getMhrTransferType,
      getMhrRegistrationValidationModel,
      getMhrInfoValidation,
      hasUnsavedChanges,
      getMhrRegistrationHomeOwnerGroups,
      getMhrTransferHomeOwnerGroups
    } = storeToRefs(useStore())
    const { isMhrCorrection, correctAmendLabel } = useMhrCorrections()
    const {
      showGroups,
      removeOwner,
      deleteGroup,
      isGlobalEditingMode,
      setGlobalEditingMode,
      hasMinimumGroups,
      editHomeOwner,
      getGroupById,
      undoGroupChanges,
      getGroupNumberById,
      getHomeTenancyType,
      hasMixedOwnersInAGroup,
      hasMixedOwnersInGroup,
      hasRemovedAllHomeOwners,
      hasRemovedAllHomeOwnerGroups,
      getTotalOwnershipAllocationStatus,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups
    } = useHomeOwners(props.isMhrTransfer, isMhrCorrection.value)
    const {
      enableHomeOwnerChanges,
      enableTransferOwnerActions,
      enableTransferOwnerGroupActions,
      enableTransferOwnerMenuActions,
      showDeathCertificate,
      showSupportingDocuments,
      isDisabledForSoGChanges,
      isDisabledForSJTChanges,
      isDisabledForWillChanges,
      isCurrentOwner,
      getCurrentOwnerStateById,
      isTransferDueToSaleOrGift,
      isTransferToSurvivingJointTenant,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      isTransferWithoutBillOfSale,
      groupHasRemovedAllCurrentOwners,
      moveCurrentOwnersToPreviousOwners,
      hasMinOneExecOrAdminInGroup,
      hasAllOwnersRemoved,
      hasOnlyOneGroupOfOwners,
      TransSaleOrGift,
      TransToExec,
      TransToAdmin,
      TransWithoutBillOfSale,
      TransJointTenants
    } = useTransferOwners(!props.isMhrTransfer)

    const { getValidation, MhrSectVal, MhrCompVal } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { isValidDeceasedOwnerGroup } = useMhrInfoValidation(getMhrInfoValidation.value)

    const localState = reactive({
      currentlyEditingHomeOwnerId: -1,
      reviewed: false,
      showOwnerChangesDialog: false,
      ownerToDecease: null as MhrRegistrationHomeOwnerIF,
      isEditingMode: computed((): boolean => localState.currentlyEditingHomeOwnerId >= 0),
      isAddingMode: computed((): boolean => props.isAdding),
      showTableError: computed((): boolean => {
        // For certain Transfers, we only need to check for global changes and do not show table error in other cases
        if (isTransferToExecutorProbateWill.value ||
          isTransferToExecutorUnder25Will.value ||
          isTransferDueToSaleOrGift.value ||
          isTransferToAdminNoWill.value ||
          isTransferToSurvivingJointTenant.value) {
          return props.validateTransfer &&
            ((props.isMhrTransfer && !hasUnsavedChanges.value) ||
              !localState.isValidAllocation ||
              (!showGroups.value && hasAllOwnersRemoved() && !hasOnlyOneGroupOfOwners()))
        }

        return ((props.validateTransfer || (!props.isMhrTransfer && localState.reviewedOwners)) &&
          (
            localState.homeOwners.length === 0 ||
            !hasMinimumGroups() ||
            (props.isMhrTransfer && !hasUnsavedChanges.value) ||
            !localState.isValidAllocation ||
            localState.hasGroupsWithNoOwners ||
            (hasMixedOwnersInAGroup() && !showGroups.value)
          )
        )
      }),
      homeOwners: computed(() =>
        props.homeOwnerGroups
          // need to have groupId to display Group Header for groups with no Owners
          .flatMap(group => (group.owners.length > 0 ? group.owners : { groupId: group.groupId }))
      ),
      reviewedOwners: computed((): boolean =>
        getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS)
      ),
      showEditActions: computed((): boolean => !props.isReadonlyTable),
      homeOwnersTableHeaders: props.isReadonlyTable ? homeOwnersTableHeadersReview : homeOwnersTableHeaders,
      addedOwnerCount: computed((): number => {
        return getTransferOrRegistrationHomeOwners().filter(owner => owner.action === ActionTypes.ADDED).length
      }),
      addedGroupCount: computed((): number => {
        return getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action === ActionTypes.ADDED).length
      }),
      hasGroupsWithNoOwners: computed((): boolean => {
        const groups = getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action !== ActionTypes.REMOVED)
        return groups.some(group => group.owners.filter(owner => owner.action !== ActionTypes.REMOVED).length === 0)
      }),
      isValidAllocation: computed((): boolean => {
        return !showGroups.value || !getTotalOwnershipAllocationStatus.value.hasTotalAllocationError ||
          [HomeTenancyTypes.SOLE, HomeTenancyTypes.JOINT].includes(getHomeTenancyType())
      })
    })

    const showCorrectUndoOptions = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return [ActionTypes.REMOVED, ActionTypes.CORRECTED, ActionTypes.EDITED].includes(item?.action)
    }

    const isInvalidRegistrationOwnerGroup = (groupId: number) =>
      hasMixedOwnersInGroup(groupId) && localState.reviewedOwners &&
      !localState.showTableError && !props.isReadonlyTable

    const isInvalidTransferOwnerGroup = (groupId: number, hasExecOrAdminInGroup: boolean) => {
      if (props.validateTransfer &&
        (!hasUnsavedChanges.value || hasMinOneExecOrAdminInGroup(groupId)) &&
        TransToExec.hasAllCurrentOwnersRemoved(groupId)
      ) return false

      const hasRemovedOwners = TransToExec.hasSomeOwnersRemoved(groupId)
      // groups that are not edited are valid
      if (!hasRemovedOwners && !hasExecOrAdminInGroup) return false

      const hasRemovedAllOwners = TransToExec.hasAllCurrentOwnersRemoved(groupId)
      const hasValidDocs = TransToExec.hasOwnersWithValidSupportDocs(groupId)
      const hasOwnersWithoutDeathCert = !TransToExec.isAllGroupOwnersWithDeathCerts(groupId)

      return !(hasRemovedAllOwners && hasValidDocs && hasOwnersWithoutDeathCert && hasExecOrAdminInGroup)
    }

    // check if Owner Group that has deceased Owners is valid
    const isInvalidOwnerGroup = (groupId: number): boolean => {
      if (!props.isMhrTransfer) return isInvalidRegistrationOwnerGroup(groupId)

      // do not show group error is there is a table error for invalid ownership allocation
      if (!props.validateTransfer || !localState.isValidAllocation) return false

      // check if group is not valid due to mixed owners or all removed owners
      if (isTransferDueToSaleOrGift.value &&
        (
          TransSaleOrGift.hasMixedOwnersInGroup(groupId) ||
          TransSaleOrGift.hasPartlyRemovedEATOwners(groupId) ||
          (TransSaleOrGift.hasAllCurrentOwnersRemoved(groupId) && !TransSaleOrGift.hasAddedOwners(groupId)) ||
          !getMhrTransferHomeOwnerGroups.value?.some(group => hasActualOwners(group.owners))
        )) return true

      if ((isTransferToExecutorProbateWill.value ||
        isTransferToExecutorUnder25Will.value ||
        isTransferToAdminNoWill.value)) {
        const hasExecOrAdminInGroup = isTransferToAdminNoWill.value
          ? TransToAdmin.hasAddedAdministratorsInGroup(groupId)
          : TransToExec.hasAddedExecutorsInGroup(groupId)

        return isInvalidTransferOwnerGroup(groupId, hasExecOrAdminInGroup)
      }

      return !isValidDeceasedOwnerGroup(groupId) && !localState.showTableError
    }

    const remove = (item): void => {
      localState.currentlyEditingHomeOwnerId = -1
      setUnsavedChanges(true)
      removeOwner(item)
    }

    const markForRemoval = (item: MhrRegistrationHomeOwnerIF): void => {
      localState.currentlyEditingHomeOwnerId = -1
      editHomeOwner(
        { ...item, action: ActionTypes.REMOVED },
        item.groupId
      )

      const group: MhrRegistrationHomeOwnerGroupIF = getGroupById(item.groupId)
      const isEmptyGroup = group.owners.every(owner => owner.action === ActionTypes.REMOVED)

      // mark empty groups as removed to show the 'No owners added yet' error
      if (isEmptyGroup && !showGroups.value) {
        group.action = ActionTypes.REMOVED
      }

      // When base ownership is SO/JT and all current owners have been removed: Move them to a previous owners group.
      if (groupHasRemovedAllCurrentOwners(getGroupById(item.groupId)) && showGroups.value) {
        moveCurrentOwnersToPreviousOwners(getGroupById(item.groupId))
      }
    }

    const undo = async (item: MhrRegistrationHomeOwnerIF): Promise<void> => {
       editHomeOwner(
        { ...getCurrentOwnerStateById(item.ownerId), action: null },
        item.groupId
      )
      const isRemovedGroup = getGroupById(item.groupId).action === ActionTypes.REMOVED
      isRemovedGroup && undoGroupChanges(item.groupId)
      context.emit('handleUndo', item)
    }

    const openForEditing = (index: number) => {
      localState.currentlyEditingHomeOwnerId = index
    }

    const isCurrentlyEditing = (index: number): boolean => {
      return index === localState.currentlyEditingHomeOwnerId
    }

    const mapInfoChipAction = (item: MhrRegistrationHomeOwnerIF): string => {
      return item.action === ActionTypes.REMOVED &&
      isPartyTypeNotEAT(item) &&
      (showDeathCertificate() ||
        isTransferToExecutorProbateWill.value ||
        isTransferToExecutorUnder25Will.value ||
        isTransferToAdminNoWill.value)
        ? item.partyType === HomeOwnerPartyTypes.OWNER_BUS ? 'HISTORICAL' : 'DECEASED'
        : item.action
    }

    // To render Group table header the owners array must not be empty
    // check for at least one owner with an id
    // This util function will help to show Owners: 0 in the table header
    const hasActualOwners = (owners: MhrRegistrationHomeOwnerIF[]): boolean => {
      const activeOwners = owners.filter(owner => owner.action !== ActionTypes.REMOVED)
      return activeOwners.length > 0 && activeOwners.some(owner => owner.ownerId !== undefined)
    }

    const isAddedHomeOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return item.action === ActionTypes.ADDED
    }

    const isAddedHomeOwnerGroup = (groupId: number): boolean => {
      return getGroupById(groupId)?.action === ActionTypes.ADDED
    }

    const isChangedOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return item.action === ActionTypes.CHANGED
    }

    const isRemovedHomeOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return item.action === ActionTypes.REMOVED
    }

    const isCorrectedOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return [ActionTypes.CORRECTED, ActionTypes.EDITED].includes(item.action)
    }

    const isPartyTypeNotEAT = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return ![HomeOwnerPartyTypes.EXECUTOR, HomeOwnerPartyTypes.ADMINISTRATOR, HomeOwnerPartyTypes.TRUSTEE]
        .includes(item.partyType)
    }

    const hasNoGroupInterest = (groupId: number): boolean => {
      const group = getGroupById(groupId)
      return !group.interestNumerator && !group.interestDenominator
    }

    const disableGroupHeader = (groupId: number): boolean => {
      const currentOwners = localState.homeOwners.filter(owner => owner.action !== ActionTypes.ADDED)

      return hasRemovedAllHomeOwners(currentOwners) &&
        isAddedHomeOwnerGroup(groupId) &&
        hasNoGroupInterest(groupId) &&
        localState.addedGroupCount <= 1
    }

    const isGroupWithNoOwners = (groupId: number, index: number): boolean => {
      const group = getGroupById(groupId)

      const hasNoOwners =
        group?.action !== ActionTypes.REMOVED &&
        group?.interestNumerator &&
        group?.interestDenominator &&
        group?.owners.filter(owner => owner.action !== ActionTypes.REMOVED).length === 0

      return hasNoOwners && index === 0
    }

    // validate group for different Transfers types
    const isTransferGroupInvalid = (groupId: number, index) => {
      if (index !== 0 || !hasUnsavedChanges.value) return false
      if (isTransferToExecutorProbateWill.value ||
        isTransferToExecutorUnder25Will.value ||
        isTransferToAdminNoWill.value) {
        const hasAddedRoleInGroup = isTransferToAdminNoWill.value
          ? TransToAdmin.hasAddedAdministratorsInGroup(groupId)
          : TransToExec.hasAddedExecutorsInGroup(groupId)

        return (
          (TransToExec.hasSomeOwnersRemoved(groupId) || hasAddedRoleInGroup) &&
          !(hasAddedRoleInGroup &&
            !TransSaleOrGift.hasMixedOwnersInGroup(groupId) &&
            TransToExec.hasAllCurrentOwnersRemoved(groupId) &&
            !TransToExec.isAllGroupOwnersWithDeathCerts(groupId))
        )
      }

      if (isTransferDueToSaleOrGift.value) {
        return TransSaleOrGift.hasMixedOwnersInGroup(groupId) || TransSaleOrGift.hasPartlyRemovedEATOwners(groupId)
      }

      if (isTransferWithoutBillOfSale.value && !TransWithoutBillOfSale.hasAllCurrentOwnersRemoved(groupId)) {
        // check only for mixed owners, removed Exec, Admin, Trustees should not trigger the error
        return TransSaleOrGift.hasMixedOwnersInGroup(groupId)
      }
    }

    const removeOwnerHandler = (owner: MhrRegistrationHomeOwnerIF): void => {
      isCurrentOwner(owner)
        ? isChangedOwner(owner) ? removeChangeOwnerHandler(owner) : markForRemoval(owner)
        : remove(owner)
    }

    const removeChangeOwnerHandler = (owner: MhrRegistrationHomeOwnerIF): void => {
      localState.ownerToDecease = { ...getCurrentOwnerStateById(owner.ownerId), groupId: owner.groupId }
      localState.showOwnerChangesDialog = true
    }

    const handleOwnerChangesDialogResp = async (val: boolean): Promise<void> => {
      if (!val) {
        localState.showOwnerChangesDialog = false
        return
      }

      await markForRemoval(localState.ownerToDecease)
      localState.showOwnerChangesDialog = false
      localState.ownerToDecease = null
    }

    // Hide bottom border for the owner's row that requires additional input (Death Certificate etc.)
    const hideRowBottomBorder = (rowItem: MhrRegistrationHomeOwnerIF): boolean => {
      return isRemovedHomeOwner(rowItem) &&
        isPartyTypeNotEAT(rowItem) && // show the bottom border line for Execs, Admins and Trustees
        (showDeathCertificate() || showSupportingDocuments())
    }

    const getHomeOwnerIcon = (partyType: HomeOwnerPartyTypes, isBusiness = false): string => {
      const uniqueRoleIcon = isBusiness
        ? 'custom:ExecutorBusinessIcon'
        : 'custom:ExecutorPersonIcon'
      const ownerIcon = isBusiness
        ? 'mdi-domain'
        : 'mdi-account'

      switch (partyType) {
        case HomeOwnerPartyTypes.EXECUTOR:
        case HomeOwnerPartyTypes.ADMINISTRATOR:
        case HomeOwnerPartyTypes.TRUSTEE:
          return uniqueRoleIcon
        case HomeOwnerPartyTypes.OWNER_IND:
        case HomeOwnerPartyTypes.OWNER_BUS:
          return ownerIcon
      }
    }

    watch(() => localState.currentlyEditingHomeOwnerId, () => {
      setGlobalEditingMode(localState.isEditingMode)
    })

    // When a change is made to homeOwners, check if any actions have changed, if so set flag
    watch(() => localState.homeOwners, (val) => {
      setUnsavedChanges(val.some(owner => !!owner.action || !owner.ownerId))

      context.emit('isValidTransferOwners',
        hasMinimumGroups() &&
        localState.isValidAllocation &&
        !localState.hasGroupsWithNoOwners &&
        (isTransferDueToSaleOrGift.value ? TransSaleOrGift.isValidTransfer.value : true) &&
        (isTransferToSurvivingJointTenant.value ? TransJointTenants.isValidTransfer.value : true) &&
        ((isTransferToExecutorProbateWill.value || isTransferToExecutorUnder25Will.value)
          ? TransToExec.isValidTransfer.value
          : true) &&
        (isTransferToAdminNoWill.value ? TransToAdmin.isValidTransfer.value : true)
      )
    }, { immediate: true, deep: true })

    watch(
      () => enableTransferOwnerGroupActions(),
      () => {
        localState.currentlyEditingHomeOwnerId = -1
      }
    )

    return {
      getMhrRegistrationHomeOwnerGroups,
      ActionTypes,
      addressSchema,
      toDisplayPhone,
      openForEditing,
      isCurrentlyEditing,
      showGroups,
      hasActualOwners,
      remove,
      deleteGroup,
      isGlobalEditingMode,
      hasMinimumGroups,
      isAddedHomeOwner,
      isChangedOwner,
      isCorrectedOwner,
      isRemovedHomeOwner,
      markForRemoval,
      undo,
      mapInfoChipAction,
      hasMixedOwnersInGroup,
      hasRemovedAllHomeOwners,
      hasRemovedAllHomeOwnerGroups,
      isAddedHomeOwnerGroup,
      disableGroupHeader,
      isGroupWithNoOwners,
      getGroupNumberById,
      getMhrTransferHomeOwnerGroups,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups,
      enableHomeOwnerChanges,
      enableTransferOwnerActions,
      enableTransferOwnerGroupActions,
      enableTransferOwnerMenuActions,
      showDeathCertificate,
      showSupportingDocuments,
      isDisabledForSoGChanges,
      isDisabledForSJTChanges,
      isDisabledForWillChanges,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      isTransferToSurvivingJointTenant,
      isCurrentOwner,
      mhrDeceasedOwnerChanges,
      removeOwnerHandler,
      removeChangeOwnerHandler,
      handleOwnerChangesDialogResp,
      hideRowBottomBorder,
      yyyyMmDdToPacificDate,
      isInvalidOwnerGroup,
      HomeOwnerPartyTypes,
      SupportingDocumentsOptions,
      HomeOwnersGroupError,
      TransSaleOrGift,
      TransToExec,
      TransToAdmin,
      getMhrInfoValidation,
      isTransferGroupInvalid,
      getHomeOwnerIcon,
      isPartyTypeNotEAT,
      showCorrectUndoOptions,
      isMhrCorrection,
      correctAmendLabel,
      getMhrTransferType,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;

.home-owners-table {
  .person-executor-icon {
    margin-top: -3px !important;
    height: 22px !important;
    width: 22px !important;
  }

  .business-executor-icon {
    margin-top: -8px !important;
    margin-left: -4px !important;
    height: 29px !important;
    width: 28px !important;
  }

  .spacer-header {
    border-color: $gray1 !important;
    background-color: $gray1 !important;
  }

  .no-bottom-border {
    border-bottom: none !important;
  }

  .death-certificate-row {
    display: grid;
  }

  .group-header-slot,
  tr.v-row-group__header,
  tbody tr.v-row-group__header:hover {
    background-color: $app-lt-blue;
  }

  .no-owners-head-row {
    color: $gray7;
  }

  .owner-name,
  .owner-name i {
    color: $gray9 !important;
  }

  .owner-name .suffix-error {
    color: $error;
  }

  .removed-owner {
    opacity: 0.4;
  }

  table {

    min-width: 50rem;

    thead.simple {

      th:not(:first-child) {
        padding-left: 0
      }
    }

    tbody > tr > td > div > tr > td,
    tbody > tr > td,
    .owner-info {
      padding: 20px 0;
      border-radius: 0 !important;
    }

    .owner-row,
    .bottom-border {
      border-bottom: thin solid rgba(0, 0, 0, 0.12);
    }

    td:first-child, th:first-child {
      padding-left: 22px;
    }

    tbody > tr.v-row-group__header,
    tbody > tr.v-row-group__header:hover {
      background: $app-lt-blue !important;
    }

    .no-owners-error {
      text-align: center;
      color: $error;
    }

    .owner-info {
      width: 100%;
      display: inline-flex;
      align-items: baseline;

      td {
        white-space: normal;
        vertical-align: top;
      }
    }
    .deceased-review-info {
      width: 100%;
    }
  }

  .owner-icon-name {
    display: flex;
    align-items: flex-start;
    overflow-wrap: anywhere;

    div {
      word-break: break-word;
    }

    i {
      margin-top: -3px;
    }
  }

  .v-data-table thead,
  .v-data-table-header th {
    padding: 0 16px;
  }

  .font-light {
    color: $gray7;
    font-size: 14px;
    line-height: 22px;
    margin-left: 32px;
    font-weight: normal;
  }

  .theme--light.v-btn.v-btn--disabled {
    color: #1669bb !important;
    opacity: 0.4 !important;
  }

  .row-actions {
    padding-right: 30px;
    display: inline-flex;
    justify-content: flex-end;
  }
}

.home-owners-table:not(.review-mode) .group-header-slot {
  padding-left: 20px;
  padding-right: 12px;
}

.v-menu__content {
  cursor: pointer;
}

:deep(.review-mode) {
  table {
    th:first-child,
    td:first-child {
      padding-left: 0 !important;
    }
  }

  tbody > tr.v-row-group__header {
    margin-left: 20px !important;
    padding-left: 20px !important;
  }
}
</style>
