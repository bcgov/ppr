<template>
  <v-expansion-panel
    class="notice-panel pb-4"
    :class="{ 'border-error-left' : isActivePanel && (addCourtOrder && !isValidCourtOrder) }"
  >
    <v-expansion-panel-title
      disableIconRotate
      :disabled="true"
    >
      <v-row
        noGutters
        class="py-3"
      >
        <v-col cols="12">
          <h3> {{ saNoticeTypeMapping[notice.securitiesActNoticeType] }} </h3>
        </v-col>
        <v-col cols="12">
          <p class="fs-14">
            Effective Date: {{ yyyyMmDdToPacificDate(notice.effectiveDate, true) || '(Not Entered)' }}
          </p>
        </v-col>
      </v-row>

      <!-- Custom Panel Actions -->
      <template #actions>
        <span class="security-notice-header-action mt-n4 mr-n2">
          <v-btn
            class="security-notice-menu-btn px-0"
            variant="plain"
            color="primary"
            :disabled="isActivePanel"
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
                class="security-notice-menu-btn px-0"
                variant="plain"
                color="primary"
                v-bind="props"
                minWidth="10"
                width="45"
                :disabled="isActivePanel"
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
                :data-test-id="`security-notice-add-sco`"
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
                :data-test-id="`security-notice-add-co`"
                @click="removeNotice"
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

    <v-expansion-panel-text>
      <v-divider class="ml-0 mt-n2 mb-4" />
      <!-- Edit Notice Content-->
      <AddEditNotice
        v-if="editNotice"
        class="px-0 mx-0"
        isEditing
        :notice="notice"
        @cancel="togglePanel"
        @done="handleEditNotice"
      />

      <!-- Add Court Order -->
      <AddEditCourtOrder
        v-else-if="addCourtOrder"
        class="px-0 mx-0"
        @isValid="isValidCourtOrder = $event"
        @cancel="togglePanel"
        @done="handleAddEditCourtOrder"
      />

      <!-- Add Commission Order -->
      <AddEditCommissionOrder
        v-else-if="addCommissionOrder"
        @click="toggleNoticeForm('addCommissionOrder')"
      />
    </v-expansion-panel-text>

    <!-- Order Review Content -->
    <v-expansion-panel-title
      v-for="(order, index) in notice.securitiesActOrders"
      :key="index"
      class="py-4 px-7"
      disabled
      hideActions
    >
      <CourtCommissionOrderReview
        class="rounded-all"
        :order="order"
      />
    </v-expansion-panel-title>
  </v-expansion-panel>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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
  isActivePanel: boolean
}>(), {
  notice: null,
  noticeIndex: null,
  isActivePanel: false
})

/** Local Properties **/
const editNotice = ref(false)
const addCourtOrder = ref(false)
const addCommissionOrder = ref(false)
const isValidCourtOrder = ref(false)

/** Local Functions **/
/** Open and close respective notice and order forms **/
const toggleNoticeForm = (formRef: string) => {
  // Reset form refs
  editNotice.value = false
  addCourtOrder.value = false
  addCommissionOrder.value = false

  switch (formRef) {
    case 'editNotice':
      editNotice.value = true
      break
    case 'addCourtOrder':
      addCourtOrder.value = true
      break
    case 'addCommissionOrder':
      addCommissionOrder.value = true
      break
  }
  togglePanel()
}
/** Remove and set security notice **/
const removeNotice = () => {
  getSecuritiesActNotices.value.splice(props.noticeIndex, 1)
  setSecuritiesActNotices([...getSecuritiesActNotices.value])
}
/** Toggle open and close panel expansion **/
const togglePanel = () => {
  emits('togglePanel', props.noticeIndex)
}
/** Handle notice form edits **/
const handleEditNotice = (notice: AddEditSaNoticeIF): void => {
  // Set add edit notices
  getSecuritiesActNotices.value[props.noticeIndex] = notice
  setAndCloseNotice()
}
const handleAddEditCourtOrder = (courtOrder: CourtOrderIF): void => {
  // Set add edit Court Order
  getSecuritiesActNotices.value[props.noticeIndex].securitiesActOrders.push(courtOrder)
  setAndCloseNotice()
}

const setAndCloseNotice = (): void => {
  setSecuritiesActNotices([...getSecuritiesActNotices.value])

  // Close expanded panel
  togglePanel()
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.notice-content-row {
  background-color: #F2F6FB;
}
:deep(.v-expansion-panel-title) {
  cursor: default;
}
</style>
