<template>
  <v-container fluid class="pa-0 no-gutters" ref="tableHeaderRef" style="position: relative">
    <date-picker
      v-show="showDatePicker"
      ref="datePicker"
      :setEndDate="submittedEndDate"
      :setStartDate="submittedStartDate"
      :setDisableEndDate="!isPpr"
      @submit="updateDateRange($event)"
    />

    <v-data-table
      id="registration-table"
      :class="{
        'freeze-scroll': freezeTableScroll,
        'full-width': headers.length <= 1,
        'registration-table': true
      }"
      ref="regTable"
      disable-pagination
      disable-sort
      :expanded.sync="expanded"
      fixed-header
      :headers="headers"
      height="100%"
      hide-default-footer
      hide-default-header
      :items="registrationHistory"
      item-key="baseRegistrationNumber"
      mobile-breakpoint="0"
      :no-data-text="tableFiltersActive ? 'No registrations found.' : 'No registrations to show.'"
    >
      <template v-slot:header="{ props }">
        <thead v-if="headers.length > 1">
          <tr>
            <th
              v-for="(header, index) in props.headers"
              :key="index"
              :class="header.class"
              class="text-left pa-0"
              :ref="header.value + 'Ref'"
              :style="overrideWidth ? getHeaderStyle(overrideWidth, header.value) : ''"
            >
              <v-row class="my-reg-header pl-3" no-gutters @click="toggleOrderBy(header.value, header.sortable)">
                <v-col :class="{ 'pl-7': header.value === 'actions' }">
                  {{ header.text }}
                  <span v-if="header.value === orderBy && header.sortable">
                    <v-icon v-if="orderVal === 'asc'" small style="color: black;">
                      mdi-arrow-up
                    </v-icon>
                    <v-icon v-else small style="color: black;">
                      mdi-arrow-down
                    </v-icon>
                  </span>
                </v-col>
              </v-row>
              <v-row class="my-reg-filter pl-3 pt-2" no-gutters>
                <v-col>
                  <v-text-field
                    v-if="header.value === 'registrationNumber' || header.value === 'mhrNumber'"
                    filled
                    single-line
                    hide-details="true"
                    v-model="registrationNumber"
                    type="text"
                    label="Number"
                    dense
                  />
                  <div v-if="header.value === 'registrationType'">
                    <registration-bar-type-ahead-list
                      v-if="hasRPPR"
                      id="reg-type-select"
                      :defaultLabel="'Registration Type'"
                      :defaultDense="true"
                      :defaultClearable="true"
                      :defaultClear="shouldClearType"
                      @selected="selectRegistration($event)"
                    />
                    <v-select
                      v-else
                      :items="registrationTypes"
                      single-line
                      item-text="registrationTypeUI"
                      item-value="registrationTypeAPI"
                      class="table-registration-types"
                      filled
                      dense
                      clearable
                      label="Registration Type"
                      v-model="registrationType"
                      id="txt-type"
                      :menu-props="{ bottom: true, offsetY: true }"
                    >
                      <template slot="item" slot-scope="data">
                        <span class="list-item">
                          {{ data.item.registrationTypeUI }}
                        </span>
                      </template>
                    </v-select>
                  </div>
                  <div v-if="header.value === 'registrationDescription'">
                    <v-select
                      :items="mhrRegistrationTypes"
                      single-line
                      item-text="registrationTypeUI"
                      item-value="registrationTypeAPI"
                      class="table-registration-types"
                      filled
                      dense
                      clearable
                      label="Registration Type"
                      v-model="registrationType"
                      id="txt-type"
                      :menu-props="{ bottom: true, offsetY: true }"
                    >
                      <template slot="item" slot-scope="data">
                        <span class="list-item">
                          {{ data.item.registrationTypeUI }}
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
                      class="reg-textfield date-filter"
                      :class="{ 'active': dateTxt === 'Custom' }"
                      append-icon="mdi-calendar"
                      dense
                      clearable
                      filled
                      hide-details="true"
                      :label="'Date'"
                      single-line
                      v-model="dateTxt"
                    />
                  </div>
                  <v-select
                    v-if="isPpr && header.value === 'statusType'"
                    :items="statusTypes"
                    hide-details
                    single-line
                    filled
                    dense
                    item-class="list-item"
                    label="Status"
                    :menu-props="{ bottom: true, offsetY: true }"
                    v-model="status"
                    clearable
                  />
                  <v-select
                    v-else-if="header.value === 'statusType'"
                    :items="mhStatusTypes"
                    hide-details
                    single-line
                    filled
                    dense
                    item-class="list-item"
                    label="Status"
                    :menu-props="{ bottom: true, offsetY: true }"
                    v-model="status"
                    clearable
                  />
                  <v-text-field
                    v-if="header.value === 'registeringName'"
                    filled
                    single-line
                    hide-details="true"
                    v-model="registeredBy"
                    type="text"
                    label="Registered By"
                    dense
                  />
                  <v-text-field
                    v-if="!isPpr && header.value === 'registeringParty'"
                    filled
                    single-line
                    hide-details="true"
                    v-model="registeringParty"
                    type="text"
                    label="Submitting Party"
                    dense
                  />
                  <v-text-field
                    v-if="header.value === 'clientReferenceId'"
                    filled
                    single-line
                    hide-details="true"
                    v-model="folioNumber"
                    type="text"
                    label=""
                    dense
                  />
                  <v-btn
                    v-if="header.value === 'actions' && headers.length > 1 && tableFiltersActive"
                    class="clear-filters-btn registration-action ma-0 px-0 pl-6 pt-4"
                    color="primary"
                    :ripple="false"
                    text
                    @click="clearFilters()"
                  >
                    Clear Filters
                    <v-icon class="pl-1 pt-1">mdi-close</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </th>
          </tr>
          <tr v-if="loadingData">
            <div
              class="v-progress-linear v-progress-linear--absolute theme--light"
              aria-valuemin="0"
              aria-valuemax="100"
              role="progressbar"
              style="height: 4px;"
            >
              <div class="v-progress-linear__background primary" style="opacity: 0.3; left: 0%; width: 100%;" />
              <div class="v-progress-linear__buffer" />
              <div class="v-progress-linear__indeterminate v-progress-linear__indeterminate--active">
                <div class="v-progress-linear__indeterminate long primary" />
                <div class="v-progress-linear__indeterminate short primary" />
              </div>
            </div>
          </tr>
        </thead>
        <thead v-else>
          <tr>
            <th>
              <p class="pa-10 ma-0" >
                No columns selected to show. Please select columns to see registration information.
              </p>
            </th>
          </tr>
        </thead>
      </template>
      <template v-slot:item="{ expand, item, isExpanded }">
        <TableRow
          class="registration-data-table"
          :ref="setRowRef(item)"
          :setAddRegEffect="['newRegItem', 'newAndFirstItem'].includes(setRowRef(item))"
          :setDisableActionShadow="overrideWidth"
          :setHeaders="headers"
          :setIsExpanded="isExpanded || isNewRegParentItem(item)"
          :setItem="item"
          :isPpr="isPpr"
          @action="emitRowAction($event)"
          @error="emitError($event)"
          @freezeScroll="freezeTableScroll = $event"
          @toggleExpand="item.expand = !isExpanded, expand(!isExpanded)"
        />
      </template>
      <template v-slot:expanded-item="{ item }">
        <TableRow
          v-for="change in item.changes"
          class="registration-data-table"
          :key="`change-${change.documentId || change.registrationNumber}`"
          :ref="setRowRef(change)"
          :isPpr="isPpr"
          :setAddRegEffect="['newRegItem', 'newAndFirstItem'].includes(setRowRef(change))"
          :setDisableActionShadow="overrideWidth"
          :setChild="true"
          :setHeaders="headers"
          :setItem="change"
          @action="emitRowAction($event)"
          @freezeScroll="freezeTableScroll = $event"
        />
      </template>
      <template v-slot:[`body.append`]>
        <tr v-if="morePages">
          <td :colspan="tableLiteralWidth">
            <table-observer @intersect="getNext()" />
            <v-skeleton-loader class="ma-0" :style="`width: ${tableLiteralWidth - 180}px`" type="list-item" />
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  onUpdated,
  reactive,
  ref,
  toRefs,
  watch
} from 'vue-demi'
import { useStore } from '@/store/store'
import flushPromises from 'flush-promises'
import _ from 'lodash'
import { DatePicker } from '@/components/common'
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'
import { TableObserver, TableRow } from './common'
/* eslint-disable no-unused-vars */
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

export default defineComponent({
  components: {
    DatePicker,
    RegistrationBarTypeAheadList,
    TableObserver,
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
      default: [] as (RegistrationSummaryIF | DraftResultIF)[]
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

    const localState = reactive({
      expanded: [],
      freezeTableScroll: false,
      loadingPDF: '',
      overrideWidth: false,
      registrationTypes: [...RegistrationTypesStandard].slice(1),
      mhrRegistrationTypes: [...MHRegistrationTypes].slice(1),
      showDatePicker: false,
      statusTypes: [...StatusTypes],
      mhStatusTypes: MhStatusTypes,
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
      registrationHistory: computed(() => { return props.setRegistrationHistory }),
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
      const firstBaseReg = localState.registrationHistory[0].baseRegistrationNumber
      const firstDocId = localState.registrationHistory[0].documentId
      return item.baseRegistrationNumber
        ? item.baseRegistrationNumber === firstBaseReg
        : (item as DraftResultIF).documentId === firstDocId
    }

    const isFirstItemMhr = (item: MhRegistrationSummaryIF | MhrDraftIF): boolean => {
      const firstMhrNumber = localState.registrationHistory[0].mhrNumber
      const firstDocId = localState.registrationHistory[0].draftNumber
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
      if (ref?.value?.$el?.scrollIntoView) {
        ref.value.$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
      // if a child row it will be an array
      if (ref?.value?.length > 0 && ref?.value[0].$el?.scrollIntoView) {
        ref.value[0].$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
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

    const getNext = _.throttle(() => {
      // if not loading and reg history exists
      if (!localState.loadingData && localState.registrationHistory?.length > 0) {
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
        // wait to ensure it is visible before attempting to scroll to it
        if (datePicker?.value?.$el?.scrollIntoView) {
          datePicker.value.$el.scrollIntoView({ behavior: 'smooth' })
        }
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
            endDate: endDate,
            folNum: props.isPpr ? folNum : folNum.toUpperCase(),
            orderBy: orderBy,
            orderVal: orderVal,
            regBy: regBy,
            regNum: regNum,
            regParty: regParty,
            regType: regType,
            secParty: secParty,
            startDate: startDate,
            status: status
          } as RegistrationSortIF,
          sorting: localState.tableFiltersActive
        })
      }, 1000)
    )

    watch(() => localState.firstColWidth, (val) => {
      // needed to set overrideWidth back to false
      if (!localState.firstColRef || val < 350) localState.overrideWidth = false
    })

    onUpdated(() => {
      // needed to set overrideWidth to true
      if (localState.firstColRef?.value?.length > 0) {
        if (localState.firstColRef.value[0].clientWidth > 350) {
          localState.overrideWidth = true
        }
      }

      // if new reg -> scroll to new reg
      if (localState.newReg?.addedReg) {
        // need both (only one ref will scroll)
        scrollToRef(newRegItem)
        scrollToRef(newAndFirstItem)
      }
    })

    return {
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
#reg-textfield {
  cursor: pointer !important;
}
.clear-filters-btn, .clear-filters-btn::before, .clear-filters-btn::after {
  background-color: transparent !important;
  height: 1rem !important;
  min-width: 0 !important;
}
.pdf-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  justify-content: start;
}
.pdf-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.pdf-btn-text {
  text-decoration: underline;
}
.edit-btn {
  border-bottom-right-radius: 0;
  border-top-right-radius: 0;
  font-size: 14px !important;
  font-weight: normal !important;
  height: 35px !important;
  width: 100px;
}
.down-btn {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
  height: 35px !important;
  width: 35px;
}
</style>
