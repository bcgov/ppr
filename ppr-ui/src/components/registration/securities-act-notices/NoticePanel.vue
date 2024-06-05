<template>
  <v-expansion-panel
    class="notice-panel pb-4"
    :class="{ 'border-error-left' : isActivePanel && !isValidOrder }"
  >
    <!-- Remove Notice Dialog -->
    <BaseDialog
      id="removeNoticeDialog"
      setAttach="#securities-act-notices"
      :setDisplay="showRemoveNoticeDialog"
      :setOptions="confirmRemoveNoticeDialog"
      @proceed="removeNotice"
    />

    <!-- Default Notice Title Content -->
    <v-expansion-panel-title
      disableIconRotate
      :disabled="true"
      :hideActions="isSummary"
      :class="{ 'removed-item': notice.action === ActionTypes.REMOVED }"
    >
      <v-expand-transition>
        <v-row
          noGutters
          class="py-3"
        >
          <v-col
            cols="12"
            class="d-inline-flex"
          >
            <h3 class="notice-type-text">
              {{ saNoticeTypeMapping[notice.securitiesActNoticeType] }}
            </h3>
            <v-btn
              v-if="notice.securitiesActOrders?.length"
              class="hide-show-orders-btn ml-n2"
              variant="plain"
              color="primary"
              :ripple="false"
              :disabled="disableActions"
              @click="showOrders = !showOrders"
            >
              <span class="fs-14">
                <v-icon size="20">{{ showOrders ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
                {{ showOrders ? 'Hide Orders' : 'Show Orders' }} ({{ notice.securitiesActOrders?.length }})
              </span>
            </v-btn>
            <span>
              <InfoChip
                v-if="isAmendment"
                class="mt-3 ml-2 py-1"
                :action="notice.action"
              />
            </span>
          </v-col>
          <v-col cols="12">
            <p
              class="effective-date-text fs-14"
              :class="{'removed-item': notice.action === ActionTypes.REMOVED}"
            >
              Effective Date:
              {{ yyyyMmDdToPacificDate(notice.effectiveDateTime?.split('T')[0], true) || '(Not Entered)' }}
            </p>
          </v-col>
        </v-row>
      </v-expand-transition>

      <!-- Custom Panel Actions -->
      <template #actions>
        <span class="security-notice-header-action mt-n4">
          <v-btn
            v-if="isAmendment && (notice?.action === ActionTypes.EDITED || notice?.action === ActionTypes.REMOVED)"
            class="security-notice-undo-btn px-0"
            variant="plain"
            color="primary"
            :disabled="disableActions"
            :ripple="false"
            @click="handleEditNotice(getOriginalSecuritiesActNotices[noticeIndex], true)"
          >
            <span class="pr-4">
              <v-icon size="small">mdi-undo</v-icon>
              Undo
            </span>
            <v-divider
              v-if="notice.action !== ActionTypes.REMOVED"
              vertical
            />
          </v-btn>
          <v-btn
            v-else
            class="security-notice-btn px-0"
            variant="plain"
            color="primary"
            :disabled="disableActions"
            :ripple="false"
            @click="toggleNoticeForm('editNotice')"
          >
            <span class="pr-4">
              <v-icon size="small">mdi-pencil</v-icon>
              {{ (isAmendment && !notice.action) ? 'Amend' : 'Edit' }} Notice
            </span>
            <v-divider vertical />
          </v-btn>
          <v-menu
            v-if="notice?.action !== ActionTypes.REMOVED"
            location="bottom right"
            class="security-notice-menu"
          >
            <template #activator="{ props, isActive }">
              <v-btn
                id="security-notice-menu-btn"
                class="px-0"
                variant="plain"
                color="primary"
                v-bind="props"
                minWidth="10"
                width="45"
                :disabled="disableActions"
                :ripple="false"
              >
                <v-icon
                  class="menu-drop-down-icon"
                  color="primary"
                >
                  {{ isActive ? 'mdi-menu-up' : 'mdi-menu-down' }}
                </v-icon>
              </v-btn>
            </template>

            <!-- Drop down list -->
            <v-list>
              <v-list-item
                :data-test-id="`security-notice-add-co`"
                @click="toggleNoticeForm('addCourtOrder')"
              >
                <v-list-item-subtitle class="text-left">
                  <v-icon
                    color="primary"
                    size="1.125rem"
                  >mdi-plus</v-icon>
                  Add Court Order
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item
                :data-test-id="`security-notice-add-comm`"
                @click="toggleNoticeForm('addCommissionOrder')"
              >
                <v-list-item-subtitle class="text-left">
                  <v-icon
                    color="primary"
                    size="1.125rem"
                  >mdi-plus</v-icon>
                  Add Securities Commission Order
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item
                v-if="isAmendment && notice.action === ActionTypes.EDITED"
                :data-test-id="`security-notice-amend-drop-option`"
                @click="toggleNoticeForm('editNotice')"
              >
                <v-list-item-subtitle class="text-left">
                  <v-icon
                    color="primary"
                    size="1.125rem"
                  >mdi-pencil</v-icon>
                  Amend Notice
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item
                :data-test-id="`security-notice-remove`"
                @click="removeOrNotify"
              >
                <v-list-item-subtitle class="text-left">
                  <v-icon
                    color="primary"
                    size="1.125rem"
                  >mdi-delete</v-icon>
                  Remove Notice
                </v-list-item-subtitle>
              </v-list-item>

            </v-list>
          </v-menu>
        </span>
      </template>
    </v-expansion-panel-title>

    <!-- Add/Edit Notice/Order Content-->
    <v-expansion-panel-text>
      <v-divider class="ml-0 mt-n2 mb-4" />
      <AddEditNotice
        v-if="editNotice"
        class="px-0 mx-0"
        isEditing
        :notice="notice"
        :isAmendment="isAmendment"
        @cancel="togglePanel(true)"
        @done="handleEditNotice"
      />
      <!-- Add Court Order -->
      <AddEditCourtOrder
        v-else-if="addCourtOrder || (editOrder && notice.securitiesActOrders[editOrderIndex]?.courtOrder)"
        class="px-0 mx-0"
        :isEditing="!!notice.securitiesActOrders?.[editOrderIndex]"
        :courtOrderProp="notice.securitiesActOrders?.[editOrderIndex]"
        :isAmendment="isAmendment"
        @isValid="isValidOrder = $event"
        @cancel="togglePanel(true)"
        @done="handleAddEditOrder"
      />

      <!-- Add Commission Order -->
      <AddEditCommissionOrder
        v-else-if="addCommissionOrder || editOrder"
        class="px-0 mx-0"
        :isEditing="!!notice.securitiesActOrders?.[editOrderIndex]"
        :commissionOrderProp="notice.securitiesActOrders?.[editOrderIndex]"
        :isAmendment="isAmendment"
        @isValid="isValidOrder = $event"
        @cancel="togglePanel(true)"
        @done="handleAddEditOrder"
      />
    </v-expansion-panel-text>

    <!-- Order Review Content -->
    <v-expand-transition>
      <div
        v-if="showOrders && !isActivePanel"
      >
        <v-expansion-panel-title
          v-if="notice?.securitiesActOrders?.length"
          class="py-4 px-7 mt-n1"
          disabled
          hideActions
        >
          <!-- Order Review Components -->
          <div class="order-content">
            <CourtCommissionOrderReview
              v-for="(order, index) in notice.securitiesActOrders"
              :key="index"
              class="rounded-all"
              :order="order"
              :isAmendment="isAmendment"
              :hasRemovedOrders="notice.action === ActionTypes.REMOVED"
            >
              <template
                v-if="!isSummary && notice.action !== ActionTypes.REMOVED"
                #actions
              >
                <span class="float-right mr-n2">
                  <v-btn
                    v-if="isAmendment &&
                      (order?.action === ActionTypes.EDITED || order?.action === ActionTypes.REMOVED)"
                    class="security-order-undo-btn px-0"
                    variant="plain"
                    color="primary"
                    :disabled="disableActions"
                    :ripple="false"
                    @click="handleAddEditOrder(
                      getOriginalSecuritiesActNotices[noticeIndex].securitiesActOrders[index], index, true
                    )"
                  >
                    <span class="pr-4">
                      <v-icon size="small">mdi-undo</v-icon>
                      Undo
                    </span>
                    <v-divider
                      v-if="order?.action !== ActionTypes.REMOVED"
                      vertical
                    />
                  </v-btn>
                  <v-btn
                    v-else
                    class="security-order-menu-btn px-0"
                    variant="plain"
                    color="primary"
                    :disabled="disableActions"
                    :ripple="false"
                    @click="toggleNoticeForm('editOrder', index)"
                  >
                    <span class="pr-4">
                      <v-icon size="small">mdi-pencil</v-icon>
                      {{ (isAmendment && !order.action) ? 'Amend' : 'Edit' }} Order
                    </span>
                    <v-divider vertical />
                  </v-btn>
                  <v-menu
                    v-if="order?.action !== ActionTypes.REMOVED"
                    location="bottom right"
                    class="security-order-menu"
                  >
                    <template #activator="{ props, isActive }">
                      <v-btn
                        class="px-0"
                        variant="plain"
                        color="primary"
                        v-bind="props"
                        minWidth="10"
                        width="45"
                        :disabled="disableActions"
                        :ripple="false"
                      >
                        <v-icon
                          class="menu-drop-down-icon"
                          color="primary"
                        >
                          {{ isActive ? 'mdi-menu-up' : 'mdi-menu-down' }}
                        </v-icon>
                      </v-btn>
                    </template>

                    <!-- Drop down list -->
                    <v-list>
                      <v-list-item
                        v-if="isAmendment && order.action === ActionTypes.EDITED"
                        :data-test-id="'security-order-amend-drop'"
                        @click="toggleNoticeForm('editOrder', index)"
                      >
                        <v-list-item-subtitle class="text-left">
                          <v-icon
                            color="primary"
                            size="1.125rem"
                          >mdi-pencil</v-icon>
                          Amend Order
                        </v-list-item-subtitle>
                      </v-list-item>

                      <v-list-item
                        :data-test-id="'security-order-remove'"
                        @click="removeOrder(noticeIndex, index)"
                      >
                        <v-list-item-subtitle class="text-left">
                          <v-icon
                            color="primary"
                            size="1.125rem"
                          >mdi-delete</v-icon>
                          Remove Order
                        </v-list-item-subtitle>
                      </v-list-item>

                    </v-list>
                  </v-menu>
                </span>
              </template>
            </CourtCommissionOrderReview>
          </div>
        </v-expansion-panel-title>
      </div>
    </v-expand-transition>
  </v-expansion-panel>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { AddEditSaNoticeIF, CourtOrderIF } from '@/interfaces'
import { ActionTypes, saNoticeTypeMapping } from '@/enums'
import { yyyyMmDdToPacificDate } from '@/utils/date-helper'
import {
  AddEditCommissionOrder,
  AddEditCourtOrder,
  AddEditNotice,
  CourtCommissionOrderReview
} from '@/components/registration'
import { InfoChip } from '@/components/common'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { confirmRemoveNoticeDialog } from '@/resources/dialogOptions'
import { BaseDialog } from '@/components/dialogs'
import { cloneDeep, isEqual, omit } from 'lodash'

/** Composables **/
const { setSecuritiesActNotices, setSecuritiesActNoticeOrder } = useStore()
const { getSecuritiesActNotices, getOriginalSecuritiesActNotices } = storeToRefs(useStore())

/** Emits **/
const emits = defineEmits<{
  togglePanel: [value: number],
  activeOrderIndex: [value: number]
}>()

/** Props **/
const props = withDefaults(defineProps<{
  notice: AddEditSaNoticeIF,
  noticeIndex: number,
  isActivePanel: boolean,
  disableActions?: boolean,
  closeOrders?: boolean,
  isSummary?: boolean,
  isAmendment?: boolean
}>(), {
  notice: null,
  noticeIndex: null,
  isActivePanel: false,
  disableActions: false,
  closeOrders: false,
  isSummary: false,
  isAmendment: false
})

/** Local Properties **/
const editNotice = ref(false)
const addCourtOrder = ref(false)
const editOrder = ref(false)
const editOrderIndex = ref(-1)
const addCommissionOrder = ref(false)
const isValidOrder = ref(true)
const showRemoveNoticeDialog = ref(false)
const showOrders = ref(props.isSummary)

/** Open and close respective notice and order forms **/
const toggleNoticeForm = async (formRef: string, index: number = -1) => {
  // Reset form refs
  resetFormDefaults()

  switch (formRef) {
    case 'editNotice':
      await nextTick()
      editNotice.value = true
      break
    case 'addCourtOrder':
      await nextTick()
      addCourtOrder.value = true
      break
    case 'addCommissionOrder':
      addCommissionOrder.value = true
      break
    case 'editOrder':
      // Set Order index
      editOrderIndex.value = index
      await nextTick()
      editOrder.value = true
      break
  }
  togglePanel()
}

/** Remove Notice and Order handlers **/
const removeNotice = (proceed: boolean) => {
  if (proceed) {
    // Mark pre-existing notices for removal
    if (props.isAmendment && getSecuritiesActNotices.value[props.noticeIndex].action !== ActionTypes.ADDED) {
      getSecuritiesActNotices.value[props.noticeIndex] = {
        ...cloneDeep(getOriginalSecuritiesActNotices.value[props.noticeIndex]),
        securitiesActOrders: cloneDeep(getOriginalSecuritiesActNotices.value[props.noticeIndex]?.securitiesActOrders),
        action: ActionTypes.REMOVED
      }
      setSecuritiesActNotices([...getSecuritiesActNotices.value])
      showRemoveNoticeDialog.value = false
    } else {
      // Remove New or Added Notices
      getSecuritiesActNotices.value.splice(props.noticeIndex, 1)
      setSecuritiesActNotices([...getSecuritiesActNotices.value])
      showRemoveNoticeDialog.value = false
    }
  } else showRemoveNoticeDialog.value = false
}

/** Prompt Removal Dialog or call remove when no orders **/
const removeOrNotify = () => {
  if (getSecuritiesActNotices.value[props.noticeIndex].securitiesActOrders?.length > 0) {
    showRemoveNoticeDialog.value = true
  } else removeNotice(true)
}

/** Mark for removal or remove designated order from parent notice **/
const removeOrder = (noticeIndex: number, orderIndex: number) => {
  const orders = getSecuritiesActNotices.value[noticeIndex].securitiesActOrders

  // Mark pre-existing notices for removal
  if (props.isAmendment && orders[orderIndex].action !== ActionTypes.ADDED) {
    const order = {
      ...orders[orderIndex],
      action: ActionTypes.REMOVED
    }
    setSecuritiesActNoticeOrder(noticeIndex, orderIndex, order)

    // Set Parent Notice Action
    getSecuritiesActNotices.value[noticeIndex].action = ActionTypes.EDITED
  } else {
    // Remove New/Added Orders
    orders.splice(orderIndex, 1)
    setAndCloseNotice(true)
  }
}

/** Handle notice form edits **/
const handleEditNotice = (notice: AddEditSaNoticeIF, isUndo = false): void => {
  // Set add edit notices
  const editNotice = !notice.effectiveDateTime ? omit(notice, 'effectiveDateTime') : notice
  getSecuritiesActNotices.value[props.noticeIndex] = cloneDeep(editNotice)
  setAndCloseNotice(isUndo)
}

const handleAddEditOrder = (order: CourtOrderIF, orderIndex: number = null, isUndo = false): void => {
  // The Notice of which the orders belong too
  const parentNotice = getSecuritiesActNotices.value[props.noticeIndex]

  // Handle Undo
  if (isUndo) {
    setSecuritiesActNoticeOrder(props.noticeIndex, orderIndex, omit(order, 'action'))
  } else if (editOrderIndex.value > -1) {
    const isAmendedOrder = !isEqual(parentNotice.securitiesActOrders[editOrderIndex.value], order)

    // Edit Order
    parentNotice.securitiesActOrders[editOrderIndex.value] = {
      ...order,
      ...(props.isAmendment && order.action !== ActionTypes.ADDED && isAmendedOrder && {
        action: ActionTypes.EDITED
      })
    }
  } else {
    // Define securities act orders array if absent (ie amendment notices with no initial orders)
    if (!parentNotice.securitiesActOrders) parentNotice.securitiesActOrders = []

    // Set add Court Order
    parentNotice.securitiesActOrders.push({
      ...order,
      ...(props.isAmendment && {
        action: ActionTypes.ADDED
      })
    })
  }
  setAndCloseNotice(isUndo)
  showOrders.value = true
}

/** Reset local form state **/
const resetFormDefaults = () => {
  // Reset form refs
  showOrders.value = false
  editOrderIndex.value = -1
  editNotice.value = false
  editOrder.value = false
  addCourtOrder.value = false
  addCommissionOrder.value = false
  isValidOrder.value = true
}

/** Toggle open and close panel expansion **/
const togglePanel = (isCancel: boolean = false) => {
  if (isCancel) resetFormDefaults()
  emits('togglePanel', props.noticeIndex)
}

/** Set Notices to Store and close active panels **/
const setAndCloseNotice = (isUndo = false): void => {
  // Amendments: Determine the action for each notice - mark as edited if it has changes,
  // retain added/removed notices, otherwise omit the action property.
  const notices = props.isAmendment
    ? getSecuritiesActNotices.value.map((notice, index) => {
      const originalNotice = getOriginalSecuritiesActNotices.value[index]
      const isAdded = notice.action === ActionTypes.ADDED
      const isRemoved = notice.action === ActionTypes.REMOVED
      const isEdited = !isAdded && !isEqual(omit(notice, 'action'), omit(originalNotice, 'action'))

      if (isEdited) {
        return { ...notice, action: ActionTypes.EDITED }
      }
      return (isAdded || isRemoved) ? { ...notice } : omit(notice, 'action')
    })
    : getSecuritiesActNotices.value

  setSecuritiesActNotices([...notices])
  // Close expanded panel
  resetFormDefaults()
  if (!isUndo) togglePanel()
}

/** Watchers **/
watch([() => props.disableActions, () => props.closeOrders], ([disableActions, closeOrders]) => {
  if ((disableActions || closeOrders) && !props.isSummary) showOrders.value = false
})
watch(() => showOrders.value, (val: boolean) => {
  if (val) {
    emits('activeOrderIndex', props.noticeIndex)
    setTimeout(() => {
      document.getElementsByClassName('notice-panel')[props.noticeIndex]?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      })
    }, 200)
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
h3 {
  line-height: 2.45rem;
}
.removed-item {
  h3, p {
    opacity: .5
  }
}
.notice-content-row {
  background-color: #F2F6FB;
}
.order-content {
  width: 100%
}
.hide-show-orders-btn {
  line-height: 1.25rem
}
#court-commission-order-review:not(:first-child) {
  margin-top: 16px;
}
:deep(.v-expansion-panel-title) {
  cursor: default;
}
</style>
