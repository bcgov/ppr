<template>
  <v-expansion-panel
    class="notice-panel pb-4"
    :class="{ 'border-error-left' : isActivePanel && ((addCourtOrder || editCourtOrder) && !isValidCourtOrder) }"
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
      v-if="!(isActivePanel && editNotice)"
      disableIconRotate
      :disabled="true"
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
                <v-icon size="20">{{ showOrders ? 'mdi-chevron-down' : 'mdi-chevron-up' }}</v-icon>
                {{ showOrders ? 'Show Orders' : 'Hide Orders' }} ({{ notice.securitiesActOrders?.length }})
              </span>
            </v-btn>
          </v-col>
          <v-col cols="12">
            <p class="effective-date-text fs-14">
              Effective Date: {{ yyyyMmDdToPacificDate(notice.effectiveDate, true) || '(Not Entered)' }}
            </p>
          </v-col>
        </v-row>
      </v-expand-transition>

      <!-- Custom Panel Actions -->
      <template #actions>
        <span class="security-notice-header-action mt-n4">
          <v-btn
            class="security-notice-btn px-0"
            variant="plain"
            color="primary"
            :disabled="disableActions"
            :ripple="false"
            @click="toggleNoticeForm('editNotice')"
          >
            <span class="pr-4">
              <v-icon size="small">mdi-pencil</v-icon>
              Edit Notice
            </span>
            <v-divider vertical />
          </v-btn>
          <v-menu
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
      <AddEditNotice
        v-if="editNotice"
        class="px-0 mx-0"
        isEditing
        :notice="notice"
        @cancel="togglePanel(true)"
        @done="handleEditNotice"
      />

      <!-- Add Court Order -->
      <template v-else-if="addCourtOrder">
        <v-divider class="ml-0 mt-n2 mb-4" />
        <AddEditCourtOrder
          class="px-0 mx-0"
          @isValid="isValidCourtOrder = $event"
          @cancel="togglePanel(true)"
          @done="handleAddEditCourtOrder"
        />
      </template>

      <template v-else-if="addCommissionOrder">
        <v-divider class="ml-0 mt-n2 mb-4" />
        <!-- Add Commission Order -->
        <AddEditCommissionOrder
          @click="toggleNoticeForm('addCommissionOrder')"
        />
      </template>
    </v-expansion-panel-text>

    <!-- Order Review Content -->
    <template v-if="showOrders">
      <v-expansion-panel-title
        v-for="(order, index) in notice.securitiesActOrders"
        :key="index"
        class="py-4 px-7 mt-n1"
        disabled
        hideActions
      >
        <div class="order-content">
          <!-- Inline Court Order Edit -->
          <template v-if="editOrderIndex === index">
            <AddEditCourtOrder
              class="px-0 mx-0"
              isEditing
              :courtOrderProp="notice.securitiesActOrders[editOrderIndex]"
              @isValid="isValidCourtOrder = $event"
              @cancel="togglePanel(true)"
              @done="handleAddEditCourtOrder"
            />
          </template>

          <!-- Order Review Components -->
          <CourtCommissionOrderReview
            v-else-if="editOrderIndex !== index"
            class="rounded-all"
            :order="order"
          >
            <template #actions>
              <span class="float-right mr-n2">
                <v-btn
                  class="security-order-menu-btn px-0"
                  variant="plain"
                  color="primary"
                  :disabled="disableActions"
                  :ripple="false"
                  @click="toggleNoticeForm('editOrder', index)"
                >
                  <span class="pr-4">
                    <v-icon size="small">mdi-pencil</v-icon>
                    Edit Order
                  </span>
                  <v-divider vertical />
                </v-btn>
                <v-menu
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
    </template>
  </v-expansion-panel>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { AddEditSaNoticeIF, CourtOrderIF } from '@/interfaces'
import { saNoticeTypeMapping } from '@/enums'
import { yyyyMmDdToPacificDate } from '@/utils/date-helper'
import {
  AddEditNotice,
  AddEditCourtOrder,
  AddEditCommissionOrder,
  CourtCommissionOrderReview
} from '@/components/registration'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { confirmRemoveNoticeDialog } from '@/resources/dialogOptions'
import { BaseDialog } from '@/components/dialogs'

/** Composables **/
const { setSecuritiesActNotices } = useStore()
const { getSecuritiesActNotices } = storeToRefs(useStore())

/** Emits **/
const emits = defineEmits<{
  togglePanel: [value: number]
}>()

/** Props **/
const props = withDefaults(defineProps<{
  notice: AddEditSaNoticeIF,
  noticeIndex: number,
  isActivePanel: boolean,
  disableActions?: boolean
}>(), {
  notice: null,
  noticeIndex: null,
  isActivePanel: false,
  disableActions: false
})

/** Local Properties **/
const editNotice = ref(false)
const addCourtOrder = ref(false)
const editCourtOrder = ref(false)
const editOrderIndex = ref(-1)
const addCommissionOrder = ref(false)
const isValidCourtOrder = ref(true)
const isValidCommissionOrder = ref(true)
const showRemoveNoticeDialog = ref(false)
const showOrders = ref(true)

/** Local Functions **/
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
      editCourtOrder.value = true
      break
  }
  togglePanel()
}
/** Remove Notice and Order handlers **/
const removeNotice = (proceed: boolean) => {
  if (proceed) {
    getSecuritiesActNotices.value.splice(props.noticeIndex, 1)
    setSecuritiesActNotices([...getSecuritiesActNotices.value])
    showRemoveNoticeDialog.value = false
  } else showRemoveNoticeDialog.value = false
}
const removeOrNotify = () => {
  if (getSecuritiesActNotices.value[props.noticeIndex].securitiesActOrders.length > 0) {
    showRemoveNoticeDialog.value = true
  } else removeNotice(true)
}
const removeOrder = (noticeIndex: number, orderIndex: number) => {
    getSecuritiesActNotices.value[noticeIndex].securitiesActOrders.splice(orderIndex, 1)
    setSecuritiesActNotices([...getSecuritiesActNotices.value])
}
const resetFormDefaults = () => {
  // Reset form refs
  editOrderIndex.value = -1
  editNotice.value = false
  addCourtOrder.value = false
  editCourtOrder.value = false
  addCommissionOrder.value = false
  isValidCourtOrder.value = true
  isValidCommissionOrder.value = true
}

/** Toggle open and close panel expansion **/
const togglePanel = (isCancel: boolean = false) => {
  if (isCancel) resetFormDefaults()
  emits('togglePanel', props.noticeIndex)
}

/** Handle notice form edits **/
const handleEditNotice = (notice: AddEditSaNoticeIF): void => {
  // Set add edit notices
  getSecuritiesActNotices.value[props.noticeIndex] = notice
  setAndCloseNotice()
}
const handleAddEditCourtOrder = (courtOrder: CourtOrderIF): void => {
  // Update when editing
  if (editOrderIndex.value > -1) {
    // Edit Order
    getSecuritiesActNotices.value[props.noticeIndex].securitiesActOrders[editOrderIndex.value] = courtOrder
  } else {
    // Set add Court Order
    getSecuritiesActNotices.value[props.noticeIndex].securitiesActOrders.unshift(courtOrder)
  }
  setAndCloseNotice()
}
const setAndCloseNotice = (): void => {
  setSecuritiesActNotices([...getSecuritiesActNotices.value])

  // Close expanded panel
  resetFormDefaults()
  togglePanel()
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
h3 {
  line-height: 2.45rem;
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
:deep(.v-expansion-panel-title) {
  cursor: default;
}
</style>
