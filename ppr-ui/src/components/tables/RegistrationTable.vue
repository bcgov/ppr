<template>
  <v-card
    ref="tableHeaderRef"
    flat
    class="pa-0 no-gutters"
  >
    <!--    <date-picker-->
    <!--      v-show="showDatePicker"-->
    <!--      ref="datePicker"-->
    <!--      :set-end-date="submittedEndDate"-->
    <!--      :set-start-date="submittedStartDate"-->
    <!--      :set-disable-end-date="!isPpr"-->
    <!--      @submit="updateDateRange($event)"-->
    <!--    />-->
    <v-table
      id="registration-table"
      ref="regTable"
      :class="{
        'freeze-scroll': freezeTableScroll,
        'full-width': headers.length <= 1,
        'registration-table': true
      }"
      fixed-header
      height="100%"
    >
      <template #default>
        <thead v-if="setHeaders.length > 1">
          <tr>
            <th
              v-for="(header, index) in setHeaders"
              :key="index"
              :ref="header.value + 'Ref'"
              :class="header.class"
              class="text-left py-2"
              :style="overrideWidth ? getHeaderStyle(overrideWidth, header.value) : ''"
            >
              <v-row
                class="reg-header-row"
                no-gutters
                @click="toggleOrderBy(header.value, header.sortable)"
              >
                <v-col
                  class="text-pre"
                  :class="{ 'pl-7': header.value === 'actions' }"
                >
                  {{ header.text }}
                  <!-- Date Sort Icon/Button -->
                  <SortingIcon
                    v-if="header.value === orderBy && header.sortable"
                    :sort-asc="sortAsc"
                    @sort-event="dateSortHandler(setRegistrationHistory, 'createDateTime', $event)"
                  />
                </v-col>
              </v-row>
              <v-row
                class="reg-filter-row pl-2 py-2"
                no-gutters
              >
                <v-col>
                  <v-text-field
                    v-if="header.value === 'registrationNumber' || header.value === 'mhrNumber'"
                    v-model="registrationNumber"
                    variant="filled"
                    single-line
                    hide-details="true"
                    type="text"
                    label="Number"
                    density="compact"
                  />
                  <div v-if="header.value === 'registrationType'">
                    <RegistrationBarTypeAheadList
                      v-if="hasRPPR"
                      id="reg-type-select"
                      :default-label="'Registration Type'"
                      :default-dense="true"
                      :default-clearable="true"
                      :default-clear="shouldClearType"
                      @selected="selectRegistration($event)"
                    />
                    <v-select
                      v-else
                      id="txt-type"
                      v-model="registrationType"
                      :items="registrationTypes"
                      single-line
                      item-title="registrationTypeUI"
                      item-value="registrationTypeAPI"
                      class="table-registration-types registration-type-select"
                      variant="filled"
                      clearable
                      density="compact"
                      label="Registration Type"
                    >
                      <template #default="item">
                        <span class="list-item py-3">
                          {{ item.registrationTypeUI }}
                        </span>
                      </template>
                    </v-select>
                  </div>
                  <div v-if="header.value === 'registrationDescription'">
                    <v-select
                      id="txt-type"
                      v-model="registrationType"
                      :items="mhrRegistrationTypes"
                      single-line
                      item-title="registrationTypeUI"
                      item-value="registrationTypeAPI"
                      class="table-registration-types registration-type-select"
                      variant="filled"
                      clearable
                      density="compact"
                      label="Registration Type"
                    >
                      <template #default="item">
                        <span class="list-item py-3">
                          {{ item.registrationTypeUI }}
                        </span>
                      </template>
                    </v-select>
                  </div>
                  <div
                    v-if="header.value === 'createDateTime'"
                    @click="showDatePicker = true"
                  >
                    <v-text-field
                      v-if="header.value === 'createDateTime'"
                      id="reg-textfield"
                      v-model="dateTxt"
                      class="reg-textfield date-filter"
                      :class="{ 'active': dateTxt === 'Custom' }"
                      append-icon="mdi-calendar"
                      density="compact"
                      clearable
                      variant="filled"
                      hide-details="true"
                      :label="'Date'"
                      single-line
                    />
                  </div>
                  <v-select
                    v-if="isPpr && header.value === 'statusType'"
                    v-model="status"
                    :items="statusTypes"
                    hide-details
                    single-line
                    variant="filled"
                    item-class="list-item"
                    label="Status"
                    clearable
                    density="compact"
                  />
                  <v-select
                    v-else-if="header.value === 'statusType'"
                    v-model="status"
                    :items="mhStatusTypes"
                    hide-details
                    single-line
                    variant="filled"
                    item-class="list-item"
                    label="Status"
                    clearable
                    density="compact"
                  />
                  <v-text-field
                    v-if="header.value === 'registeringName'"
                    v-model="registeredBy"
                    variant="filled"
                    single-line
                    hide-details="true"
                    type="text"
                    label="Registered By"
                    density="compact"
                  />
                  <v-text-field
                    v-if="!isPpr && header.value === 'registeringParty'"
                    v-model="registeringParty"
                    variant="filled"
                    single-line
                    hide-details="true"
                    type="text"
                    label="Submitting Party"
                    density="compact"
                  />
                  <v-text-field
                    v-if="header.value === 'clientReferenceId'"
                    v-model="folioNumber"
                    variant="filled"
                    single-line
                    hide-details="true"
                    type="text"
                    label=""
                    density="compact"
                  />
                  <v-btn
                    v-if="header.value === 'actions' && headers.length > 1 && tableFiltersActive"
                    class="clear-filters-btn registration-action ma-0 px-0 pl-6 pt-4"
                    color="primary"
                    :ripple="false"
                    variant="text"
                    @click="clearFilters()"
                  >
                    Clear Filters
                    <v-icon class="pl-1 pt-1">
                      mdi-close
                    </v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </th>
          </tr>
          <!--          <tr v-if="loadingData">-->
          <!--            <div-->
          <!--              class="v-progress-linear v-progress-linear&#45;&#45;absolute theme&#45;&#45;light"-->
          <!--              aria-valuemin="0"-->
          <!--              aria-valuemax="100"-->
          <!--              role="progressbar"-->
          <!--              style="height: 4px;"-->
          <!--            >-->
          <!--              <div-->
          <!--                class="v-progress-linear__background bg-primary"-->
          <!--                style="opacity: 0.3; left: 0%; width: 100%;"-->
          <!--              />-->
          <!--              <div class="v-progress-linear__buffer" />-->
          <!--              <div class="v-progress-linear__indeterminate v-progress-linear__indeterminate&#45;&#45;active">-->
          <!--                <div class="v-progress-linear__indeterminate long bg-primary" />-->
          <!--                <div class="v-progress-linear__indeterminate short bg-primary" />-->
          <!--              </div>-->
          <!--            </div>-->
          <!--          </tr>-->
        </thead>
        <thead v-else>
          <tr>
            <th>
              <p class="pa-10 ma-0">
                No columns selected to show. Please select columns to see registration information.
              </p>
            </th>
          </tr>
        </thead>

        <v-virtual-scroll
          :items="setRegistrationHistory"
          height="2000"
          renderless
        >
          <template #default="{ item }">
            <tbody>
              <!-- Parent Registration items -->
              <!--            <template-->
              <!--              v-for="(item, index) in setRegistrationHistory"-->
              <!--              :key="`registration: ${item.baseRegistrationNumber} - ${index}`"-->
              <!--            >-->
              <TableRow
                :ref="setRowRef(item)"
                class="registration-data-table"
                :set-add-reg-effect="['newRegItem', 'newAndFirstItem'].includes(setRowRef(item))"
                :set-disable-action-shadow="overrideWidth"
                :set-headers="headers"
                :set-is-expanded="item.expand || isNewRegParentItem(item)"
                :set-item="item"
                :is-ppr="isPpr"
                :close-sub-menu="closeSubMenu"
                @action="emitRowAction($event)"
                @error="emitError($event)"
                @freeze-scroll="freezeTableScroll = $event"
                @toggle-expand="item.expand = !item.expand"
              />

              <!-- Children items -->
              <template v-if="item.expand">
                <TableRow
                  v-for="childItem in item.changes"
                  :key="`change-${childItem.documentId || childItem.registrationNumber}`"
                  :ref="setRowRef(childItem)"
                  class="registration-data-table"
                  :is-ppr="isPpr"
                  :set-add-reg-effect="['newRegItem', 'newAndFirstItem'].includes(setRowRef(childItem))"
                  :set-disable-action-shadow="overrideWidth"
                  :set-child="true"
                  :set-headers="setHeaders"
                  :set-item="childItem"
                  @action="emitRowAction($event)"
                  @freeze-scroll="freezeTableScroll = $event"
                />
              </template>
            <!--            </template>-->

            <!-- Simulated Pagination -->
            <!--          <template v-if="morePages">-->
            <!--            <tr>-->
            <!--              <td :colspan="tableLiteralWidth">-->
            <!--                <table-observer @intersect="getNext()" />-->
            <!--                <v-skeleton-loader-->
            <!--                  class="ma-0"-->
            <!--                  :style="`width: ${tableLiteralWidth - 180}px`"-->
            <!--                  type="list-item"-->
            <!--                />-->
            <!--              </td>-->
            <!--            </tr>-->
            <!--          </template>-->
            </tbody>
          </template>
        </v-virtual-scroll>

        <!-- No Data Message -->
        <!--        <tbody v-else>-->
        <!--          <tr>-->
        <!--            <td-->
        <!--              class="text-center"-->
        <!--              :colspan="setHeaders.length"-->
        <!--            >-->
        <!--              {{ tableFiltersActive ? 'No registrations found.' : 'No registrations to show.' }}-->
        <!--            </td>-->
        <!--          </tr>-->
        <!--        </tbody>-->
      </template>
    </v-table>
  </v-card>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  onBeforeMount,
  onUpdated,
  reactive,
  ref,
  toRefs,
  watch
} from 'vue'
import { useStore } from '@/store/store'
import flushPromises from 'flush-promises'
import _ from 'lodash'
import { DatePicker } from '@/components/common'
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'
/* eslint-disable no-unused-vars */
import { SortingIcon, TableRow } from './common'
import {
  RegistrationSummaryIF,
  AccountProductSubscriptionIF,
  RegistrationTypeIF,
  BaseHeaderIF,
  DraftResultIF,
  MhrDraftIF,
  RegistrationSortIF,
  ErrorIF,
  RegTableNewItemI,
  MhRegistrationSummaryIF
} from '@/interfaces'
/* eslint-enable no-unused-vars */
import {
  AccountProductCodes,
  AccountProductRoles,
  TableActions
} from '@/enums'
import { useRegistration } from '@/composables/useRegistration'
import { MHRegistrationTypes, RegistrationTypesStandard, StatusTypes, MhStatusTypes } from '@/resources'
import { storeToRefs } from 'pinia'
import { useTableFeatures } from '@/composables'

export default defineComponent({
  components: {
    SortingIcon,
    DatePicker,
    RegistrationBarTypeAheadList,
    TableRow
  },
  props: {
    isPpr: {
      type: Boolean,
      default: false
    },
    isMhr: {
      type: Boolean,
      default: false
    },
    setHeaders: {
      default: [] as BaseHeaderIF[]
    },
    setLoading: {
      default: false
    },
    setMorePages: {
      default: false
    },
    setNewRegItem: {
      default: null,
      type: Object as () => RegTableNewItemI
    },
    setSearch: {
      type: String,
      default: ''
    },
    setRegistrationHistory: {
      default: () => [],
      // To fix: Vue3 supports TS in templates
      type: Array as () => RegistrationSummaryIF | DraftResultIF | MhrDraftIF | any
    },
    setSort: {
      type: Object as () => RegistrationSortIF,
      default: null
    }
  },
  setup (props, { emit }) {
    // refs
    const regTable = ref(null)
    // refs for scrolling
    const datePicker = ref(null)
    const firstItem = ref(null) // first item in table
    const newRegItem = ref(null) // new item in table
    const newAndFirstItem = ref(null) // new item and first item in table
    // refs for setting header widths dynamically
    const tableHeaderRef = ref(null)
    const registrationNumberRef = ref(null)
    const registrationTypeRef = ref(null)
    const createDateTimeRef = ref(null)
    const statusTypeRef = ref(null)
    const registeringNameRef = ref(null)
    const registeringPartyRef = ref(null)
    const securedPartiesRef = ref(null)
    const clientReferenceIdRef = ref(null)
    const refs = [
      registrationNumberRef,
      registrationTypeRef,
      createDateTimeRef,
      statusTypeRef,
      registeringNameRef,
      registeringPartyRef,
      securedPartiesRef,
      clientReferenceIdRef
    ]
    const headersToRefsIndex = {
      registrationNumber: 0,
      registrationType: 1,
      createDateTime: 2,
      statusType: 3,
      registeringName: 4,
      registeringParty: 5,
      securedParties: 6,
      clientReferenceId: 7
    }
    // getters
    const { getAccountProductSubscriptions } = storeToRefs(useStore())
    // helpers
    const {
      // filters
      registrationNumber,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      status,
      registrationType,
      submittedStartDate,
      submittedEndDate,
      orderBy,
      orderVal,
      // other table stuff
      shouldClearType,
      dateTxt,
      clearFilters
    } = useRegistration(props.setSort)
    const { sortDates } = useTableFeatures()

    const localState = reactive({
      expanded: [],
      freezeTableScroll: false,
      loadingPDF: '',
      overrideWidth: false,
      sortAsc: false,
      registrationTypes: [...RegistrationTypesStandard].slice(1),
      mhrRegistrationTypes: [...MHRegistrationTypes].slice(1),
      showDatePicker: false,
      statusTypes: [...StatusTypes],
      mhStatusTypes: MhStatusTypes,
      closeSubMenu: false,
      hasRPPR: computed(() => {
        const productSubscriptions =
          getAccountProductSubscriptions.value as AccountProductSubscriptionIF
        return (
          productSubscriptions?.[AccountProductCodes.RPPR]?.roles
            .includes(AccountProductRoles.EDIT) || false
        )
      }),
      headers: computed(() => {
        return props.setHeaders
      }),
      loadingData: computed(() => {
        return props.setLoading
      }),
      morePages: computed(() => {
        return props.setMorePages
      }),
      newReg: computed(() => { return props.setNewRegItem }),
      search: computed(() => { return props.setSearch }),
      tableFiltersActive: computed((): boolean => {
        return !!(dateTxt.value || registrationNumber.value || registrationType.value ||
          status.value || registeredBy.value || registeringParty.value ||
          securedParties.value || folioNumber.value)
      }),
      tableHeadersWidth: computed(() => {
        const width = tableHeaderRef?.value?.clientWidth || 0
        if (width > 1360) return 1360
        return width
      }),
      tableLiteralWidth: computed(() => {
        return regTable?.value?.$el?.clientWidth || 0
      }),
      firstColRef: computed(() => {
        if (props.setHeaders?.length < 1) return null
        else if (localState.tableHeadersWidth === 0) return null
        return refs[headersToRefsIndex[localState.headers[0].value]]
      }),
      firstColWidth: computed(() => {
        if (!localState.firstColRef) return 0
        if (localState.firstColRef.value?.length > 0) {
          return localState.firstColRef.value[0]?.clientWidth || 0
        }
        return 0
      })
    })

    const emitError = (error: ErrorIF): void => {
      emit('error', error)
    }

    const emitRowAction = ({ action, docId, regNum, mhrInfo }): void => {
      emit('action', {
        action: action as TableActions,
        docId: docId as string,
        regNum: regNum as string,
        mhrInfo: mhrInfo as MhRegistrationSummaryIF
      })
    }

    const getHeaderStyle = (overrideWidth: boolean, header: string): string => {
      if (overrideWidth && header !== 'actions') {
        return `min-width: ${(localState.tableHeadersWidth - 180) / (localState.headers.length - 1)}px`
      }
      if (overrideWidth && header === 'actions') {
        return 'box-shadow: none; border-left: none; border-bottom: 1px solid #dee2e6 !important;'
      }
      return ''
    }

    const isFirstItem = (item: RegistrationSummaryIF | DraftResultIF): boolean => {
      const firstBaseReg = props.setRegistrationHistory[0].baseRegistrationNumber
      const firstDocId = props.setRegistrationHistory[0].documentId
      return item.baseRegistrationNumber
        ? item.baseRegistrationNumber === firstBaseReg
        : (item as DraftResultIF).documentId === firstDocId
    }

    const isFirstItemMhr = (item: MhRegistrationSummaryIF | MhrDraftIF): boolean => {
      const firstMhrNumber = props.setRegistrationHistory[0].mhrNumber
      const firstDocId = props.setRegistrationHistory[0].draftNumber
      return item.mhrNumber
        ? item.mhrNumber === firstMhrNumber
        : item.draftNumber === firstDocId
    }

    const isNewRegItem =
      (item: RegistrationSummaryIF | DraftResultIF | MhrDraftIF | MhRegistrationSummaryIF): boolean => {
        const draftItem = item as any // Either DraftResultIF or MhrDraftIF
        const regItem = item as RegistrationSummaryIF
        const mhRegItem = item as MhRegistrationSummaryIF
        const registrationNumber = regItem.registrationNumber || mhRegItem.mhrNumber
        if (registrationNumber && registrationNumber === localState.newReg?.addedReg) {
        // reg num is not blank and equals newly added reg num
          return true
        } else if (
          (draftItem.documentId && draftItem.documentId === localState.newReg?.addedReg) ||
          (draftItem.draftNumber && draftItem.draftNumber === localState.newReg?.addedReg)
        ) {
        // doc id is not blank and equals newly added doc id
          return true
        }
        return false
      }

    const isNewRegParentItem = (item: RegistrationSummaryIF | MhRegistrationSummaryIF): boolean => {
      const regItem = item as RegistrationSummaryIF
      const mhRegItem = item as MhRegistrationSummaryIF
      if (item.expand === undefined && item.changes !== undefined) item.expand = false
      const registrationNumber = regItem.registrationNumber || mhRegItem.mhrNumber
      return (
        !!localState.newReg?.addedRegParent &&
        localState.newReg.addedRegParent !== '' &&
        localState.newReg.addedRegParent === registrationNumber
      )
    }

    const scrollToRef = (ref: any): void => {
      setTimeout(() => {
        if (ref?.value?.$el?.scrollIntoView) {
          ref.value.$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
        // if a child row it will be an array
        if (ref?.value?.length > 0 && ref?.value[0].$el?.scrollIntoView) {
          ref.value[0].$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 500)
    }

    const setRowRef = (item: RegistrationSummaryIF | DraftResultIF | MhRegistrationSummaryIF | MhrDraftIF): string => {
      const isFirst = props.isPpr
        ? isFirstItem(item as RegistrationSummaryIF | DraftResultIF)
        : isFirstItemMhr(item as MhRegistrationSummaryIF | MhrDraftIF)
      const isNewReg = isNewRegItem(item)
      if (isFirst && isNewReg) return 'newAndFirstItem'
      if (isFirst) return 'firstItem'
      if (isNewReg) return 'newRegItem'
      return ''
    }

    const toggleOrderBy = (header: string, sortable: boolean) => {
      if (!sortable) { return }

      if (header === orderBy.value) {
        // toggle asc vs desc
        if (orderVal.value === 'desc') { orderVal.value = 'asc' } else { orderVal.value = 'desc' }
      } else {
        // set new order by
        orderBy.value = header
        orderVal.value = 'desc'
      }
      // need both (only one ref will scroll)
      scrollToRef(firstItem)
      scrollToRef(newAndFirstItem)
    }

    const updateDateRange = (dates: { endDate: Date, startDate: Date }) => {
      if (!(dates.endDate && dates.startDate)) dateTxt.value = ''
      else dateTxt.value = 'Custom'

      submittedStartDate.value = dates.startDate
      submittedEndDate.value = dates.endDate
      localState.showDatePicker = false
    }

    const selectRegistration = (val: RegistrationTypeIF) => {
      shouldClearType.value = false
      registrationType.value = val?.registrationTypeAPI || ''
    }

    /** Date sort handler to sort and change sort icon state **/
    const dateSortHandler = (registrationHistory: Array<any>, dateType: string, reverse: boolean) => {
      localState.sortAsc = !localState.sortAsc
      sortDates(registrationHistory, dateType, reverse)
    }

    const getNext = _.throttle(() => {
      // if not loading and reg history exists
      if (!localState.loadingData && props.setRegistrationHistory?.length > 0) {
        emit('getNext')
      }
    }, 500, { trailing: false })

    watch(() => dateTxt.value, (val) => {
      if (!val) {
        submittedStartDate.value = null
        submittedEndDate.value = null
      }
      if (val && val !== 'Custom') {
        dateTxt.value = ''
      }
    })

    watch(() => localState.showDatePicker, async (val) => {
      if (val) {
        await flushPromises()
        setTimeout(() => {
          // wait to ensure it is visible before attempting to scroll to it
          if (datePicker?.value?.$el?.scrollIntoView) {
            datePicker.value.$el.scrollIntoView({ behavior: 'smooth' })
          }
        }, 500)
      }
    })

    // filter watchers (triggers the sorting)
    watch(
      () => [
        registeringParty.value,
        registrationType.value,
        registrationNumber.value,
        folioNumber.value,
        securedParties.value,
        registeredBy.value,
        status.value,
        submittedStartDate.value,
        submittedEndDate.value,
        orderBy.value,
        orderVal.value
      ], _.debounce((
        [regParty, regType, regNum, folNum, secParty, regBy, status, startDate, endDate, orderBy, orderVal]
      ) => {
        // need both (only one ref will scroll)
        scrollToRef(firstItem)
        scrollToRef(newAndFirstItem)

        emit('sort', {
          sortOptions: {
            endDate,
            folNum: props.isPpr ? folNum : folNum.toUpperCase(),
            orderBy,
            orderVal,
            regBy,
            regNum,
            regParty,
            regType,
            secParty,
            startDate,
            status
          } as RegistrationSortIF,
          sorting: localState.tableFiltersActive
        })
      }, 1000)
    )

    watch(() => localState.firstColWidth, (val) => {
      // needed to set overrideWidth back to false
      if (!localState.firstColRef || val < 350) localState.overrideWidth = false
    })

    // Triggers scrolling on changes to the registration history
    watch(() => props.setRegistrationHistory,
      () => {
        if (localState.newReg?.addedReg) {
          // need both (only one ref will scroll)
          scrollToRef(newRegItem)
          scrollToRef(newAndFirstItem)
        }
      },
      { deep: true }
    )

    // Ensures filtering is cleared when returing to dashboard from registrations
    onBeforeMount(() => {
      clearFilters()
    })

    onUpdated(() => {
      // needed to set overrideWidth to true
      if (localState.firstColRef?.value?.length > 0) {
        if (localState.firstColRef.value[0].clientWidth > 350) {
          localState.overrideWidth = true
        }
      }
    })

    return {
      dateSortHandler,
      datePicker,
      dateTxt,
      emitError,
      emitRowAction,
      firstItem,
      getHeaderStyle,
      getNext,
      isNewRegItem,
      isNewRegParentItem,
      newRegItem,
      newAndFirstItem,
      orderBy,
      orderVal,
      registrationNumber,
      registrationType,
      regTable,
      scrollToRef,
      setRowRef,
      shouldClearType,
      selectRegistration,
      toggleOrderBy,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      status,
      updateDateRange,
      clearFilters,
      submittedEndDate,
      submittedStartDate,
      TableActions,
      tableHeaderRef,
      registrationNumberRef,
      registrationTypeRef,
      createDateTimeRef,
      statusTypeRef,
      registeringNameRef,
      registeringPartyRef,
      securedPartiesRef,
      clientReferenceIdRef,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.registration-table {
  max-height: 700px;
  :deep(.v-label, .v-field-label) {
    font-size: .875rem;
  }
}

//.reg-header-row {
//  height: 40px;
//}

//.reg-filter-row {
//  height: 70px;
//}

//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row:hover:not(.v-data-table__expanded__content):not(.v-data-table__empty-wrapper),
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row td.actions-cell,
//.registration-row {
//  // $blueSelected 0.5 opacity colour at full opacity (needed for .actions-cell overlay)
//  background-color: #f2f6fb !important;
//  min-width: 164px;
//  -moz-transition: background-color 1.5s ease;
//  -o-transition: background-color 1.5s ease;
//  -webkit-transition: background-color 1.5s ease;
//  transition: background-color 1.5s ease;
//  z-index: 3;
//}
//.registration-row td {
//  padding-left: 12px !important;
//}
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.base-registration-row:hover:not(.v-data-table__expanded__content):not(.v-data-table__empty-wrapper),
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.base-registration-row td.actions-cell,
//.registration-row.base-registration-row {
//  background-color: white !important;
//  font-weight: bold;
//}
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.base-registration-row.rollover-effect:hover:not(.v-data-table__expanded__content):not(.v-data-table__empty-wrapper),
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.base-registration-row.rollover-effect td.actions-cell,
//.registration-row.base-registration-row.rollover-effect {
//  background-color: $blueSelected !important;
//}
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.draft-registration-row:hover:not(.v-data-table__expanded__content):not(.v-data-table__empty-wrapper),
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.draft-registration-row td.actions-cell,
//.registration-row.draft-registration-row {
//  // $gray1 0.5 opacity colour at full opacity (needed for .actions-cell overlay)
//  background: #f8f9fa !important;
//}
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.added-reg-effect:hover:not(.v-data-table__expanded__content):not(.v-data-table__empty-wrapper),
//#registration-table.v-data-table .v-data-table__wrapper table tbody tr.registration-row.added-reg-effect td.actions-cell,
//.registration-row.added-reg-effect,
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.draft-registration-row.added-reg-effect:hover:not(.v-data-table__expanded__content):not(.v-data-table__empty-wrapper),
//#registration-table.v-data-table .v-data-table__wrapper table tbody
//tr.registration-row.draft-registration-row.added-reg-effect td.actions-cell,
//.registration-row.draft-registration-row.added-reg-effect {
//  background-color: $greenSelected !important;
//}
//
//#registration-table.v-data-table tr.v-data-table__empty-wrapper td {
//  text-align: left;
//}
//#reg-textfield {
//  cursor: pointer !important;
//}
//.clear-filters-btn, .clear-filters-btn::before, .clear-filters-btn::after {
//  background-color: transparent !important;
//  height: 1rem !important;
//  min-width: 0 !important;
//}
//.pdf-btn {
//  background-color: transparent !important;
//  color: $primary-blue !important;
//  justify-content: start;
//}
//.pdf-btn::before {
//  background-color: transparent !important;
//  color: $primary-blue !important;
//}
//.pdf-btn-text {
//  text-decoration: underline;
//}
//.edit-btn {
//  border-bottom-right-radius: 0;
//  border-top-right-radius: 0;
//  font-size: 14px !important;
//  font-weight: normal !important;
//  height: 35px !important;
//  width: 100px;
//}
//.down-btn {
//  border-bottom-left-radius: 0;
//  border-top-left-radius: 0;
//  height: 35px !important;
//  width: 35px;
//}
//:deep(.registration-type-select .v-select__selections:first-child) {
//  width: 125px;
//}
</style>
