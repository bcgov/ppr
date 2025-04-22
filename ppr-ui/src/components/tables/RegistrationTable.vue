<script lang="ts">
import {
  computed,
  defineComponent, onMounted,
  onUpdated,
  reactive,
  ref,
  toRefs,
  watch
} from 'vue'
import { useStore } from '@/store/store'
import { SortingIcon, TableRow } from './common'
import type {
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
import {
  AccountProductCodes,
  AccountProductRoles,
  TableActions,
  mapMhrDescriptionToCodes,
  APIRegistrationTypes
} from '@/enums'
import {
  MHRegistrationTypes,
  RegistrationTypesStandard,
  StatusTypes,
  MhStatusTypes,
  MHRegistrationTypesOrg
} from '@/resources'
import { storeToRefs } from 'pinia'
import { dateToYyyyMmDd, yyyyMmDdToPacificDate, localTodayDate, getFeatureFlag } from '@/utils'
import TableObserver from '@/components/tables/common/TableObserver.vue'

export default defineComponent({
  components: {
    TableObserver,
    SortingIcon,
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
      type: Array as () => BaseHeaderIF[],
      default: [] as BaseHeaderIF[]
    },
    setLoading: {
      type: Boolean,
      default: false
    },
    setMorePages: {
      type: Boolean,
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
      type: Array as () => RegistrationSummaryIF | DraftResultIF | MhrDraftIF
    },
    setSort: {
      type: Object as () => RegistrationSortIF,
      default: null
    }
  },
  emits: [
    'action',
    'error',
    'sort',
    'getNext'
  ],
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
    const { isRoleStaffReg, getAccountProductSubscriptions } = storeToRefs(useStore())
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
      documentId,
      clearFilters
    } = useRegistration(props.setSort)
    const { sortDates } = useTableFeatures()
    const { isMiscTransfersEnabled } = useTransferOwners()

    const localState = reactive({
      expanded: [],
      freezeTableScroll: false,
      loadingPDF: '',
      overrideWidth: false,
      sortAsc: false,
      showDatePicker: false,
      statusTypes: [...StatusTypes],
      mhStatusTypes: MhStatusTypes,
      registrationTypes: computed(() => {
        let registrationTypes = RegistrationTypesStandard

        // Filter out the commercial lien registration type if the feature flag is disabled
        if(!getFeatureFlag('cla-enabled')){
          registrationTypes = RegistrationTypesStandard.filter(item =>
            item?.registrationTypeAPI !== APIRegistrationTypes.COMMERCIAL_LIEN
          )
        }

        return [...registrationTypes].slice(1)
      }),
      mhrRegistrationTypes: computed(() =>
        isMiscTransfersEnabled
          ? MHRegistrationTypes.filter(item =>
            localState.displayGroup[item.group] || item.class === 'registration-list-header')
          : [...MHRegistrationTypesOrg].slice(1)),
      loadingNewPages: false,
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
      newReg: computed(() => { return props.setNewRegItem }),
      search: computed(() => { return props.setSearch }),
      tableFiltersActive: computed((): boolean => {
        return !!(dateTxt.value || registrationNumber.value || registrationType.value ||
          status.value || registeredBy.value || registeringParty.value ||
          securedParties.value || folioNumber.value || documentId.value)
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
      }),
      displayGroup: { // collapse all registration type groups
        1: false,
        2: false,
        3: false,
        4: false
      }
    })

    // Toggle groups in the Registration Type filter
    const toggleGroup = (group: number) => {
      const initial = localState.displayGroup[group]
      localState.displayGroup[group] = !initial
    }

    // Hide all groups in the Registration Type filter
    const hideAllGroups = () => {
      for (const key in localState.displayGroup) {
        localState.displayGroup[key] = false;
      }
    }

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
      }, 300)
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

      submittedStartDate.value = dateToYyyyMmDd(dates.startDate)
      submittedEndDate.value = dateToYyyyMmDd(dates.endDate)
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

    const getNext = (() => {
      // if not loading and reg history exists
      if (!localState.loadingData && props.setRegistrationHistory?.length > 0) {
        emit('getNext')
        localState.loadingNewPages = true
        setTimeout(() => {
          localState.loadingNewPages = false
        }, 2000)
      }
    })
    const getPstDateObj = (date: string): Date => {
      if(!date) return null
      // Regular expression to match timezone offset (e.g., +05:00 or Z for UTC)
      const timeZoneRegex = /([+-]\d{2}:\d{2}|Z)$/;

      if(timeZoneRegex.test(date)) {
        return new Date(date)
      }
      return new Date(yyyyMmDdToPacificDate(date))
    }
    watch(() => dateTxt.value, (val) => {
      if (!val) {
        submittedStartDate.value = null
        submittedEndDate.value = null
      }
      if (val && val !== 'Custom') {
        dateTxt.value = ''
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
        orderVal.value,
        documentId.value
      ], (
        [regParty, regType, regNum, folNum, secParty, regBy, status, startDate, endDate, orderBy, orderVal, documentId]
      ) => {
        // Close Date Picker on Sort
        localState.showDatePicker = false

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
            regType: mapMhrDescriptionToCodes[regType] || regType,
            secParty,
            startDate,
            status,
            documentId
          } as RegistrationSortIF,
          sorting: localState.tableFiltersActive
        })
      }
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

    onUpdated(() => {
      // needed to set overrideWidth to true
      if (localState.firstColRef?.value?.length > 0) {
        if (localState.firstColRef.value[0].clientWidth > 350) {
          localState.overrideWidth = true
        }
      }
    })

    onMounted(() => {
      if (!isRoleStaffReg.value) clearFilters()
    })

    return {
      isMiscTransfersEnabled,
      getNext,
      localTodayDate,
      yyyyMmDdToPacificDate,
      dateSortHandler,
      datePicker,
      dateTxt,
      documentId,
      emitError,
      emitRowAction,
      firstItem,
      getHeaderStyle,
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
      toggleGroup,
      hideAllGroups,
      getPstDateObj,
      ...toRefs(localState)
    }
  }
})
</script>

<template>
  <v-card
    ref="tableHeaderRef"
    flat
    class="pa-0 noGutters"
  >
    <!-- Ranged Date Picker for DateTime Filtering -->
    <RangeDatePicker
      v-if="showDatePicker"
      id="ranged-date-picker"
      ref="datePicker"
      :default-start-date="getPstDateObj(submittedStartDate)"
      :default-end-date="getPstDateObj(submittedEndDate)"
      :default-max-date="new Date()"
      @submit="updateDateRange($event)"
    />

    <v-table
      id="registration-table"
      ref="regTable"
      :class="{
        'freeze-scroll': freezeTableScroll,
        'full-width': headers.length <= 1,
        'registration-table': true,
        'min-table-height': showDatePicker
      }"
      fixed-header
    >
      <template #default>
        <thead v-if="setHeaders.length > 1">
          <tr>
            <th>
              <span class="fs-13 font-weight-medium">SORT BY:</span>
            </th>
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
            </th>
          </tr>
          <tr>
            <th>
              <span class="fs-13 font-weight-medium">FILTER BY:</span>
            </th>
            <th
              v-for="(header, index) in setHeaders"
              :key="index"
              :ref="header.value + 'Ref'"
              :class="header.class"
              class="text-left py-2"
              :style="overrideWidth ? getHeaderStyle(overrideWidth, header.value) : ''"
            >
              <v-row
                class="reg-filter-row py-2"
                no-gutters
              >
                <v-col>
                  <v-text-field
                    v-if="header.value === 'registrationNumber' || header.value === 'mhrNumber'"
                    v-model="registrationNumber"
                    variant="filled"
                    color="primary"
                    single-line
                    :hide-details="true"
                    type="text"
                    label="Number"
                    density="compact"
                    aria-hidden="true"
                  />
                  <template v-if="header.value === 'registrationType'">
                    <RegistrationBarTypeAheadList
                      v-if="hasRPPR"
                      id="reg-type-select"
                      class="reg-type-ahead-input"
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
                      color="primary"
                      clearable
                      hide-details
                      density="compact"
                      label="Registration Type"
                      aria-hidden="true"
                    >
                      <template #default="item">
                          <span class="list-item py-3">
                            {{ item.registrationTypeUI }}
                          </span>
                      </template>
                    </v-select>
                  </template>

                  <div v-if="header.value === 'registrationDescription'">
                    <v-select
                      id="txt-type"
                      v-model="registrationType"
                      :items="mhrRegistrationTypes"
                      :menu-props="isMiscTransfersEnabled ? { maxHeight: 440, width: 500 } : {}"
                      single-line
                      item-title="registrationTypeUI"
                      item-value="registrationTypeAPI"
                      class="table-registration-types registration-type-select"
                      variant="filled"
                      color="primary"
                      clearable
                      hide-details
                      density="compact"
                      label="Registration Type"
                      aria-hideen="true"
                      @update:menu="isMiscTransfersEnabled ? hideAllGroups() : ''"
                    >
                      <template
                        v-if="isMiscTransfersEnabled"
                        #item="{ props, item }"
                      >
                        <template v-if="item.raw.class === 'registration-list-header'">
                          <v-divider
                            v-if="item.raw.group !== 1"
                            class="mx-4"
                          />
                          <v-list-item
                            v-if="item.raw.class === 'registration-list-header'"
                            class="registration-list-item font-weight-bold fs-14 py-3"
                          >
                            <v-row
                              :id="`transfer-type-group-${item.raw.group}`"
                              no-gutters
                              @click="toggleGroup(item.raw.group)"
                            >
                              <v-col>
                                {{ item.raw.text }}
                              </v-col>
                              <v-col
                                cols="auto"
                              >
                                <v-btn
                                  variant="plain"
                                  size="18"
                                  color="primary"
                                  class="mt-n2"
                                  :append-icon="displayGroup[item.raw.group] ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                                />
                              </v-col>
                            </v-row>
                          </v-list-item>
                        </template>
                        <v-list-item
                          v-else
                          :id="`transfer-type-item-${index}`"
                          :title="item.raw.registrationTypeUI"
                          class="copy-normal gray7 fs-14 py-3 pl-8"
                          v-bind="props"
                        />
                      </template>
                      <template
                        v-else
                        #default="item"
                      >
                          <span class="list-item py-3">
                            {{ item.registrationTypeUI }}
                          </span>
                      </template>
                    </v-select>
                  </div>
                  <v-text-field
                    v-if="header.value === 'createDateTime'"
                    id="reg-date-text-field"
                    v-model="dateTxt"
                    class="reg-textfield date-filter"
                    append-inner-icon="mdi-calendar"
                    density="compact"
                    clearable
                    variant="filled"
                    color="primary"
                    hide-details
                    label="Date"
                    single-line
                    persistent-clear
                    :clear-icon="'mdi-close'"
                    aria-hidden="true"
                    @click="showDatePicker = true"
                  />
                  <v-text-field
                    v-if="!isPpr && header.value === 'documentId'"
                    v-model="documentId"
                    variant="filled"
                    color="primary"
                    single-line
                    hide-details="true"
                    type="text"
                    label="Document ID"
                    density="compact"
                    aria-hidden="true"
                  />
                  <v-select
                    v-if="isPpr && header.value === 'statusType'"
                    v-model="status"
                    :items="statusTypes"
                    hide-details
                    single-line
                    variant="filled"
                    color="primary"
                    item-class="list-item"
                    label="Status"
                    clearable
                    density="compact"
                    aria-hidden="true"
                  />
                  <v-select
                    v-else-if="header.value === 'statusType'"
                    v-model="status"
                    :items="mhStatusTypes"
                    hide-details
                    single-line
                    variant="filled"
                    color="primary"
                    item-class="list-item"
                    label="Status"
                    clearable
                    density="compact"
                    aria-hidden="true"
                  />
                  <v-text-field
                    v-if="header.value === 'registeringName'"
                    v-model="registeredBy"
                    variant="filled"
                    color="primary"
                    single-line
                    hide-details="true"
                    type="text"
                    label="Registered By"
                    density="compact"
                    aria-hidden="true"
                  />
                  <v-text-field
                    v-if="!isPpr && header.value === 'registeringParty'"
                    v-model="registeringParty"
                    variant="filled"
                    color="primary"
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
                    color="primary"
                    single-line
                    hide-details="true"
                    type="text"
                    label=""
                    density="compact"
                    aria-hidden="true"
                  />
                  <v-btn
                    v-if="header.value === 'actions' && headers.length > 1 && tableFiltersActive"
                    class="registration-action ma-0"
                    color="primary"
                    :ripple="false"
                    variant="outlined"
                    @click="clearFilters()"
                  >
                    Clear Filters
                    <v-icon size="18" class="pl-3 pt-1">
                      mdi-close
                    </v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </th>
          </tr>
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

        <tr v-if="loadingData">
          <td
            class="text-center"
            :colspan="setHeaders.length"
          >
            <v-progress-linear
              indeterminate
              color="primary"
            />
          </td>
        </tr>
        <tbody v-if="setRegistrationHistory.length">
        <template
          v-for="(item, index) in setRegistrationHistory"
          :key="`row-item:${index}`"
        >
          <!-- Parent Registration items -->
          <TableRow
            :ref="setRowRef(item)"
            class="registration-data-table"
            :set-add-reg-effect="['newRegItem', 'newAndFirstItem'].includes(setRowRef(item))"
            :set-disable-action-shadow="overrideWidth"
            :set-headers="headers"
            :set-is-expanded="item.expand || isNewRegParentItem(item)"
            :set-item="item"
            :is-ppr="isPpr"
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
        </template>
        <!-- Simulated Pagination -->
        <template v-if="setMorePages">
          <tr>
            <td :colspan="setHeaders.length">
              <TableObserver @intersect="getNext()" />
              <v-progress-linear
                v-if="loadingNewPages"
                indeterminate
                color="primary"
              />
            </td>
          </tr>
        </template>
        </tbody>
        <!-- No Data Message -->
        <tbody v-else>
        <tr>
          <td
            class="text-center"
            :colspan="setHeaders.length"
          >
            {{ tableFiltersActive ? 'No registrations found.' : 'No registrations to show.' }}
          </td>
        </tr>
        </tbody>
      </template>
    </v-table>
  </v-card>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.registration-table {
  max-height: 700px;
  min-height: 250px;

  :deep(.v-label, .v-field-label) {
    font-size: .875rem;
  }
}
.min-table-height {
  min-height: 650px;
}
.reg-type-ahead-input {
  :deep(.v-input__control)   {
    height: 45px;
  }
}
</style>
