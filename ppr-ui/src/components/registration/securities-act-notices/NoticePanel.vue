<template>
  <v-expansion-panel class="notice-panel">
    <v-expansion-panel-title
      disableIconRotate
      :disabled="false"
      class="mb-2"
    >
      <v-row
        noGutters
        class="py-3"
      >
        <v-col cols="12">
          <h3> {{ saNoticeTypeMapping[notice.noticeType] }} </h3>
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
            :disabled="false"
            :ripple="false"
          >
            <span class="pr-4">
              <v-icon size="small">mdi-pencil</v-icon>
              Edit Notice
            </span>
            <v-divider
              vertical
            />
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
                :disabled="isActive"
                :ripple="false"
                v-bind="props"
                minWidth="10"
                width="45"
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

              <!-- Actions other than Cancel Note-->
              <!--              <v-list-item-->
              <!--                v-for="option in noteOptions"-->
              <!--                :key="UnitNotesInfo[option].header"-->
              <!--                :data-test-id="`security-notice-option-${option}`"-->
              <!--                @click="handleOptionSelection(option, note)"-->
              <!--              >-->
              <!--                <v-list-item-subtitle class="text-right">-->
              <!--                  <v-icon-->
              <!--                    color="primary"-->
              <!--                    size="1.125rem"-->
              <!--                  >{{ UnitNotesInfo[option].dropdownIcon }}</v-icon>-->
              <!--                  {{ UnitNotesInfo[option].dropdownText }}-->
              <!--                </v-list-item-subtitle>-->
              <!--              </v-list-item>-->

            </v-list>
          </v-menu>
        </span>
      </template>
    </v-expansion-panel-title>

    <v-expansion-panel-text class="mb-2">
      <v-divider class="ml-0 mt-n2 mb-4" />
      <AddEditNotice
        class="px-0 mx-0"
        isEditing
        :notice="notice"
        @cancel="emits('closePanel', noticeIndex)"
        @done="handleEditNotice"
      />
      <!-- Primary Notice Content-->
      <v-row
        noGutters
        class="notice-content-row rounded-all"
      >
        <v-col class="pa-8">
          Future Court Order and Commission Orders
        </v-col>
      </v-row>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup lang="ts">
import { AddEditSaNoticeIF } from '@/interfaces'
import { saNoticeTypeMapping } from '@/enums'
import { yyyyMmDdToPacificDate } from '@/utils/date-helper'
import { AddEditNotice } from '@/components/registration'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

/** Composables **/
const { setSecuritiesActNotices } = useStore()
const { getSecuritiesActNotices } = storeToRefs(useStore())

/** Props **/
const props = withDefaults(defineProps<{
  notice: AddEditSaNoticeIF,
  noticeIndex: number
}>(), {
  notice: null,
  noticeIndex: null
})

/** Emits **/
const emits = defineEmits<{
  closePanel: [value: number]
}>()

/** Local Functions **/
const handleEditNotice = (notice: AddEditSaNoticeIF) => {
  // Set add edit notices
  getSecuritiesActNotices.value[props.noticeIndex] = notice
  setSecuritiesActNotices([...getSecuritiesActNotices.value])

  // Close expanded panel
  emits('closePanel', props.noticeIndex)
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.notice-content-row {
  background-color: #F2F6FB;
}
</style>
