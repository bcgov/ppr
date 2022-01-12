<template>
  <v-container fluid no-gutters class="pa-0">
    <date-picker
      v-show="showDatePicker"
      ref="datePicker"
      :setEndDate="submittedEndDate"
      :setStartDate="submittedStartDate"
      @submit="updateDateRange($event)"
    />

    <v-data-table
      v-if="!loadingData"
      id="registration-table"
      :class="{
        'freeze-scroll': freezeTableScroll,
        'full-width': headers.length <= 1,
        'registration-table': true
      }"
      disable-pagination
      disable-sort
      :expanded.sync="expanded"
      fixed-header
      :headers="headers"
      height="100%"
      hide-default-footer
      hide-default-header
      :items="tableData"
      item-key="baseRegistrationNumber"
      mobile-breakpoint="0"
      :no-data-text="tableFiltersActive ? 'No registrations found.' : 'No registrations created yet.'"
      :sort-desc="[false, true]"
    >
      <template v-slot:header="{ props }">
        <thead v-if="headers.length > 1">
          <tr>
            <th
              v-for="(header, index) in props.headers"
              :key="index"
              :class="header.class"
              class="text-left pa-0"
            >
              <v-row class="my-reg-header pl-3" no-gutters @click="selectAndSort(header.value)">
                <v-col :class="{ 'pl-7': header.value === 'actions' }">
                  {{ header.text }}
                  <span v-if="header.value === selectedSort && header.sortable">
                    <v-icon v-if="currentOrder === 'asc'" small style="color: black;">
                      mdi-arrow-down
                    </v-icon>
                    <v-icon v-else small style="color: black;">
                      mdi-arrow-up
                    </v-icon>
                  </span>
                </v-col>
              </v-row>
              <v-row class="my-reg-filter pl-3 pt-2" no-gutters>
                <v-col>
                  <v-text-field
                    v-if="header.value === 'registrationNumber'"
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
                  <div
                    v-if="header.value === 'createDateTime'"
                    @click="showDatePicker = true"
                  >
                    <v-text-field
                      v-if="header.value === 'createDateTime'"
                      :id="$style['reg-textfield']"
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
                    v-if="header.value === 'statusType'"
                    :items="statusTypes"
                    hide-details
                    single-line
                    filled
                    dense
                    item-class="list-item"
                    label="Status"
                    :menu-props="{ bottom: true, offsetY: true }"
                    v-model="status"
                    @change="filterResults(tableData)"
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
                    v-if="header.value === 'registeringParty'"
                    filled
                    single-line
                    hide-details="true"
                    v-model="registeringParty"
                    type="text"
                    label="Registering Party"
                    dense
                  />
                  <v-text-field
                    v-if="header.value === 'securedParties'"
                    filled
                    single-line
                    hide-details="true"
                    v-model="securedParties"
                    type="text"
                    label="Secured Parties"
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
                    :class="[$style['clear-filters-btn'], 'registration-action', 'ma-0', 'px-0', 'pl-6', 'pt-4']"
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
      <template v-slot:item="{ expand, item, isExpanded }" class="registration-data-table">
        <table-row
          :setHeaders="headers"
          :setIsExpanded="isExpanded"
          :setItem="item"
          @action="emitRowAction($event)"
          @freezeScroll="freezeTableScroll = $event"
          @toggleExpand="item.expand = !isExpanded, expand(!isExpanded)"
        />
      </template>
      <template v-slot:expanded-item="{ item }" class="registration-data-table">
        <table-row
          v-for="change in item.changes"
          :key="change.documentId"
          :setChild="true"
          :setHeaders="headers"
          :setItem="change"
          @action="emitRowAction($event)"
          @freezeScroll="freezeTableScroll"
        />
      </template>
    </v-data-table>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  watch
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import flushPromises from 'flush-promises'
// local components
import { DatePicker } from '@/components/common'
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'
import { TableRow } from './common'
// local types/helpers/etc.
import {
  RegistrationSummaryIF, // eslint-disable-line no-unused-vars
  AccountProductSubscriptionIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  BaseHeaderIF, // eslint-disable-line no-unused-vars
  DraftResultIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import {
  AccountProductCodes, // eslint-disable-line no-unused-vars
  AccountProductRoles, // eslint-disable-line no-unused-vars
  TableActions // eslint-disable-line no-unused-vars
} from '@/enums'
import { useRegistration } from '@/composables/useRegistration'
import { RegistrationTypesStandard, StatusTypes } from '@/resources'

export default defineComponent({
  components: {
    DatePicker,
    RegistrationBarTypeAheadList,
    TableRow
  },
  props: {
    setHeaders: {
      default: [] as BaseHeaderIF[]
    },
    setLoading: {
      default: false
    },
    setSearch: {
      type: String,
      default: ''
    },
    setRegistrationHistory: {
      default: [] as (RegistrationSummaryIF | DraftResultIF)[]
    }
  },
  setup (props, { emit }) {
    // refs
    const datePicker = ref(null)
    // getters
    const { getAccountProductSubscriptions } = useGetters<any>([
      'getAccountProductSubscriptions'
    ])
    // helpers
    const {
      dateTxt,
      registrationNumber,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      shouldClearType,
      status,
      registrationType,
      submittedStartDate,
      submittedEndDate,
      originalData,
      tableData,
      filterResults,
      clearFilters
    } = useRegistration()

    const localState = reactive({
      currentOrder: 'asc',
      expanded: [],
      freezeTableScroll: false,
      loadingPDF: '',
      registrationTypes: [...RegistrationTypesStandard].slice(1),
      selectedSort: 'createDateTime',
      showDatePicker: false,
      statusTypes: [...StatusTypes],
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
      registrationHistory: computed(() => { return props.setRegistrationHistory }),
      search: computed(() => { return props.setSearch }),
      tableFiltersActive: computed((): boolean => {
        if (
          dateTxt.value || registrationNumber.value || registrationType.value ||
          status.value || registeredBy.value || registeringParty.value ||
          securedParties.value || folioNumber.value
        ) {
          return true
        }
        return false
      })
    })

    const emitRowAction = ({ action, docId, regNum }): void => {
      emit('action', {
        action: action as TableActions,
        docId: docId as string,
        regNum: regNum as string
      })
    }

    const selectAndSort = (col: string) => {
      if (!localState.headers.find(c => c.value === col).sortable) {
        return
      }
      let direction = 'asc'
      if (col === localState.selectedSort) {
        if (localState.currentOrder === 'asc') {
          direction = 'desc'
        }
      }

      if (direction === 'desc') {
        tableData.value.sort((a, b) =>
          a[col] > b[col] ? 1 : b[col] > a[col] ? -1 : 0
        )
      } else {
        tableData.value.sort((a, b) =>
          a[col] < b[col] ? 1 : b[col] < a[col] ? -1 : 0
        )
      }
      localState.currentOrder = direction
      localState.selectedSort = col
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

    watch(() => dateTxt.value, (val) => {
      if (!val) {
        submittedStartDate.value = null
        submittedEndDate.value = null
      }
      if (val && val !== 'Custom') {
        dateTxt.value = ''
      }
    })

    watch(() => localState.registrationHistory, (val) => {
      originalData.value = [...val]
      tableData.value = filterResults(originalData.value)
    }, { deep: true, immediate: true })

    watch(() => localState.showDatePicker, async (val) => {
      if (val) {
        await flushPromises()
        // wait to ensure it is visible before attempting to scroll to it
        if (datePicker?.value?.$el?.scrollIntoView) {
          datePicker.value.$el.scrollIntoView({ behavior: 'smooth' })
        }
      }
    })

    return {
      datePicker,
      dateTxt,
      emitRowAction,
      registrationNumber,
      registrationType,
      shouldClearType,
      selectRegistration,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      status,
      originalData,
      tableData,
      filterResults,
      updateDateRange,
      clearFilters,
      selectAndSort,
      submittedEndDate,
      submittedStartDate,
      TableActions,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
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
