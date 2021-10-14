<template>
  <v-container fluid no-gutters class="pa-0">
    <v-card
      v-if="showSubmittedDatePicker"
      :class="[$style['date-selection'], 'registration-date']"
      elevation="6"
    >
      <v-row no-gutters>
        <v-col cols="6" :class="pickerStartClass">Select Start Date:</v-col>
        <v-col cols="6" class="pl-4" :class="pickerEndClass"
          >Select End Date:</v-col
        >
      </v-row>
      <v-row>
        <v-col cols="6">
          <v-date-picker
            color="primary"
            :max="submittedEndDateTmp"
            v-model="submittedStartDateTmp"
          />
        </v-col>
        <v-col cols="6">
          <v-date-picker
            color="primary"
            :min="submittedStartDateTmp"
            v-model="submittedEndDateTmp"
          />
        </v-col>
      </v-row>
      <v-row no-gutters justify="end">
        <v-col cols="auto pr-4">
          <v-btn
            class="date-selection-btn bold"
            text
            ripple
            small
            @click="updateSubmittedRange"
            >OK</v-btn
          >
          <v-btn
            class="date-selection-btn ml-4"
            text
            ripple
            small
            @click="resetSubmittedRange"
            >Cancel</v-btn
          >
        </v-col>
      </v-row>
    </v-card>

    <v-data-table
      v-if="!loadingData"
      id="registration-table"
      class="registration-table pl-4"
      :class="$style['reg-table']"
      :headers="headers"
      :items="tableData"
      :search="search"
      sort-by="registrationNumber"
      :sort-desc="[false, true]"
      disable-pagination
      disable-sort
      hide-default-footer
      hide-default-header
      fixed-header
      height="600px"
      no-data-text="No registrations created yet."
    >
      <template v-slot:header="{ props }">
        <th
          v-for="(header, index) in props.headers"
          :key="index"
          :class="header.class"
          class="border-btm text-left pa-0"
        >
          <v-row class="my-reg-header pl-2 pt-8" no-gutters @click="selectAndSort(header.value)">
            <v-col>
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
          <v-row class="border-tp my-reg-filter pl-2 pt-5" no-gutters>
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
                @click="showSubmittedDatePicker = true"
              >
                <v-text-field
                  v-if="header.value === 'createDateTime'"
                  filled
                  single-line
                  id="reg-textfield"
                  data-test-id="reg-date-text"
                  v-model="registrationDateFormatted"
                  hint="YYYY/MM/DD"
                  append-icon="mdi-calendar"
                  dense
                  clearable
                  hide-details="true"
                />
              </div>
              <v-select
                v-if="header.value === 'statusType'"
                :items="statusTypes"
                hide-details
                single-line
                filled
                dense
                label="Status"
                v-model="status"
                id="txt-status"
                @change="filterResults(tableData)"
                clearable
              >
                <template slot="item" slot-scope="data">
                  <span class="list-item">
                    {{ data.item.text }}
                  </span>
                </template>
              </v-select>
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
                v-if="header.value === 'actions'"
                :class="[$style['clear-filters-btn'], 'registration-action', 'ma-0', 'pa-0']"
                color="primary"
                text
                @click="clearFilters()"
              >
                Clear Filters
                <v-icon class="pl-1 pt-1">mdi-close</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </th>
      </template>
      <template v-slot:item="row" class="registration-data-table">
        <tr
          :key="row.item.id"
          class="registration-row"
          v-if="!row.item.hide"
          :class="rowClass(row.item)"
        >
          <td
            v-if="inSelectedHeaders('registrationNumber')"
            v-html="
              displayRegistrationNumber(
                row.item.baseRegistrationNumber,
                row.item.registrationNumber
              )
            "
          ></td>
          <td v-if="inSelectedHeaders('registrationType')">
            {{ getRegistrationType(row.item.registrationType) }}
          </td>
          <td v-if="inSelectedHeaders('createDateTime')">
            <span v-if="row.item && !row.item.type">
              {{ getFormattedDate(row.item.createDateTime) }}
            </span>
            <span v-else>
              Not Registered
            </span>
          </td>
          <td v-if="inSelectedHeaders('statusType')">
            {{ getStatusDescription(row.item.statusType) }}
          </td>
          <td v-if="inSelectedHeaders('registeringName')">
            {{ row.item.registeringName }}
          </td>
          <td v-if="inSelectedHeaders('registeringParty')">
            {{ row.item.registeringParty || '' }}
          </td>
          <td v-if="inSelectedHeaders('securedParties')">
            {{ row.item.securedParties || '' }}
          </td>
          <td v-if="inSelectedHeaders('clientReferenceId')">
            {{ row.item.clientReferenceId }}
          </td>
          <td
            v-if="inSelectedHeaders('expireDays')"
            v-html="showExpireDays(row.item.expireDays)"
          ></td>
          <td v-if="inSelectedHeaders('vs')">
            <v-btn
              :id="`pdf-btn-${row.item.id}`"
              v-if="row.item && !row.item.type"
              :class="[$style['pdf-btn'], 'px-0', 'mt-n3']"
              depressed
              :loading="row.item.path === loadingPDF"
              @click="downloadPDF(row.item.path)"
            >
              <v-icon class="ma-0" left small>mdi-file-pdf-outline</v-icon>
              <span :class="[$style['pdf-btn-text'], 'ma-0']">PDF</span>
            </v-btn>
          </td>

          <!-- Action Btns -->
          <td class="actions-cell px-0 py-4">
            <div class="actions" v-if="row.item && row.item.type">
              <span class="edit-action">
                <v-btn
                  color="primary"
                  elevation="0"
                  :class="$style['edit-btn']"
                  :id="'class-' + row.index + '-change-added-btn'"
                >
                  <span @click="editDraft(row.item)">Edit</span>
                </v-btn>
              </span>

              <span class="actions__more">
                <v-menu offset-y left nudge-bottom="4">
                  <template v-slot:activator="{ on }">
                    <v-btn
                      small
                      v-on="on"
                      elevation="0"
                      color="primary"
                      class="actions__more-actions__btn"
                      :class="$style['down-btn']"
                    >
                      <v-icon>mdi-menu-down</v-icon>
                    </v-btn>
                  </template>
                  <v-list class="actions__more-actions">
                    <v-list-item>
                      <v-list-item-subtitle @click="deleteDraft(row.item, TableActions.DELETE)">
                        <v-icon small>mdi-delete</v-icon>
                        <span class="ml-1">Delete Draft</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </span>
            </div>
            <div class="actions" v-if="row.item && !row.item.type">
              <span class="edit-action">
                <v-btn
                  color="primary"
                  elevation="0"
                  :class="$style['edit-btn']"
                  :id="'class-' + row.index + '-change-added-btn'"
                >
                  <span>Open</span>
                </v-btn>
              </span>

              <span class="actions__more">
                <v-menu offset-y left nudge-bottom="4">
                  <template v-slot:activator="{ on: onMenu }">
                    <v-btn
                      small
                      elevation="0"
                      v-on="onMenu"
                      color="primary"
                      class="actions__more-actions__btn"
                      :class="$style['down-btn']"
                    >
                      <v-icon>mdi-menu-down</v-icon>
                    </v-btn>
                  </template>
                  <v-list class="actions__more-actions registration-actions">
                    <v-list-item v-if="isActive(row.item)">
                      <v-list-item-subtitle @click="handleAction(row.item, TableActions.AMEND)">
                        <v-icon small>mdi-pencil</v-icon>
                        <span class="ml-1">Amend</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item v-if="isActive(row.item)">
                      <v-list-item-subtitle @click="handleAction(row.item, TableActions.DISCHARGE)">
                        <v-icon small>mdi-note-remove-outline</v-icon>
                        <span class="ml-1">Total Discharge</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-tooltip
                      left
                      content-class="left-tooltip pa-2 mr-2"
                      transition="fade-transition"
                      :disabled="row.item.expireDays !== -99"
                    >
                      <template v-slot:activator="{ on: onTooltip }">
                        <div v-on="onTooltip">
                          <v-list-item
                            v-if="isActive(row.item)"
                            :disabled="row.item.expireDays === -99"
                          >
                            <v-list-item-subtitle @click="handleAction(row.item, TableActions.RENEW)">
                              <v-icon small>mdi-calendar-clock</v-icon>
                              <span class="ml-1">Renew</span>
                            </v-list-item-subtitle>
                          </v-list-item>
                        </div>
                      </template>
                      Infinite registrations cannot be renewed.
                    </v-tooltip>
                    <v-list-item>
                      <v-list-item-subtitle @click="handleAction(row.item, TableActions.REMOVE)">
                        <v-icon small>mdi-delete</v-icon>
                        <span class="ml-1">Remove From Table</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </span>
            </div>
          </td>
        </tr>
      </template>
    </v-data-table>
    <v-snackbar
      class="my-reg-snackbar"
      timeout="4000"
      v-model="showSnackbar"
    >
      <v-row no-gutters>
        <v-col cols="11">
          Registration was successfully added to your table.
        </v-col>
        <v-col cols="1">
          <v-btn
            class="snackbar-btn-close float-right ma-0 mr-n2 pa-0"
            icon
            :ripple="false"
            small
            @click="showSnackbar = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-snackbar>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  computed
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { registrationPDF } from '@/utils' // eslint-disable-line
// local components
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'
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
  APIStatusTypes, // eslint-disable-line no-unused-vars
  DraftTypes, // eslint-disable-line no-unused-vars
  TableActions // eslint-disable-line no-unused-vars
} from '@/enums'
import { useRegistration } from '@/composables/useRegistration'

export default defineComponent({
  components: {
    RegistrationBarTypeAheadList
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
      default: [] as RegistrationSummaryIF[] | DraftResultIF[]
    },
    toggleSnackBar: {
      default: false
    }
  },
  setup (props, { emit }) {
    const {
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      registrationNumber,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      shouldClearType,
      status,
      registrationType,
      registrationTypes,
      daysToExpiry,
      submittedStartDate,
      submittedEndDate,
      registrationDateFormatted,
      statusTypes,
      tableData,
      filterResults,
      clearFilters,
      originalData
    } = useRegistration()
    const { getAccountProductSubscriptions } = useGetters<any>([
      'getAccountProductSubscriptions'
    ])

    const localState = reactive({
      currentOrder: 'asc',
      datePickerErr: false,
      loadingPDF: '',
      registrationDate: '',
      registrationDateFormatted: '',
      selectedSort: 'number',
      showSubmittedDatePicker: false,
      submittedStartDateTmp: null,
      submittedEndDateTmp: null,
      showSnackbar: false,
      hasRPPR: computed(() => {
        const productSubscriptions =
          getAccountProductSubscriptions.value as AccountProductSubscriptionIF
        return (
          productSubscriptions?.[AccountProductCodes.RPPR].roles
            .includes(AccountProductRoles.EDIT) || false
        )
      }),
      headers: computed(() => {
        return props.setHeaders
      }),
      loadingData: computed(() => {
        return props.setLoading
      }),
      pickerStartClass: computed(() => {
        if (!localState.submittedStartDateTmp && localState.datePickerErr) return 'picker-title picker-err'
        return 'picker-title'
      }),
      pickerEndClass: computed(() => {
        if (!localState.submittedEndDateTmp && localState.datePickerErr) return 'picker-title picker-err'
        return 'picker-title'
      }),
      registrationHistory: computed(() => { return props.setRegistrationHistory }),
      search: computed(() => { return props.setSearch })
    })

    const deleteDraft = (item: DraftResultIF): void => {
      emit('action', {
        action: TableActions.DELETE,
        docId: item.documentId
      })
    }

    const displayRegistrationNumber = (baseReg: string, actualReg: string): string => {
      if (!actualReg) actualReg = 'Pending'
      if (baseReg) {
        if (baseReg === actualReg) {
          return '<b>' + baseReg + '</b>'
        }
        return (
          '<b>' +
          baseReg +
          '</b>' +
          '<br><span class="font-italic font-weight-regular">Registration Number:<br>' +
          actualReg +
          '</span>'
        )
      }
      return actualReg
    }

    const downloadPDF = async (path: string): Promise<any> => {
      localState.loadingPDF = path
      const pdf = await registrationPDF(path)
      if (!pdf || pdf?.error) {
        emit('error', { statusCode: 404 })
      } else {
        /* solution from https://github.com/axios/axios/issues/1392 */

        // it is necessary to create a new blob object with mime-type explicitly set
        // otherwise only Chrome works like it should
        const blob = new Blob([pdf], { type: 'application/pdf' })

        // IE doesn't allow using a blob object directly as link href
        // instead it is necessary to use msSaveOrOpenBlob
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
          window.navigator.msSaveOrOpenBlob(blob, path)
        } else {
          // for other browsers, create a link pointing to the ObjectURL containing the blob
          const url = window.URL.createObjectURL(blob)
          const a = window.document.createElement('a')
          window.document.body.appendChild(a)
          a.setAttribute('style', 'display: none')
          a.href = url
          a.download = path.replace('/ppr/api/v1/', '')
          a.click()
          window.URL.revokeObjectURL(url)
          a.remove()
        }
      }
      localState.loadingPDF = ''
    }

    const editDraft = (item: DraftResultIF): void => {
      if (item?.type === DraftTypes.FINANCING_STATEMENT) {
        emit('action', { action: TableActions.EDIT_NEW, docId: item.documentId })
      } else if (item?.type === DraftTypes.AMENDMENT_STATEMENT) {
        emit('action', {
          action: TableActions.EDIT_AMEND,
          docId: item.documentId,
          regNum: item.baseRegistrationNumber
        })
      }
    }

    const handleAction = (item: RegistrationSummaryIF, action: TableActions): void => {
      emit('action', { action: action, regNum: item.baseRegistrationNumber })
    }

    const inSelectedHeaders = (search: string) => {
      return localState.headers.find((header) => { return header.value === search })
    }

    const rowClass = (item): string => {
      if (item?.type) {
        return 'font-italic'
      } else {
        if (item?.baseRegistrationNumber === item?.registrationNumber) {
          return 'base-registration-row'
        }
      }

      return ''
    }

    const showExpireDays = (days: number): string => {
      if (!days) {
        return 'N/A'
      }
      if (days === -99) {
        return 'Infinite'
      } else {
        if (days > 364) {
          const today = new Date()
          const expireDate = new Date()
          expireDate.setDate(expireDate.getDate() + days)

          var dateExpiry = new Date(
            Date.UTC(
              expireDate.getUTCFullYear(),
              expireDate.getUTCMonth(),
              expireDate.getUTCDate()
            )
          )
          var dateToday = new Date(
            Date.UTC(
              today.getUTCFullYear(),
              today.getUTCMonth(),
              today.getUTCDate()
            )
          )

          let daysDiff = dateExpiry.getDate() - dateToday.getDate()
          if (daysDiff < 0) {
            dateExpiry.setFullYear(dateExpiry.getFullYear() - 1)
            daysDiff = dateExpiry.getDate() - dateToday.getDate()
          }
          const years = dateExpiry.getFullYear() - dateToday.getFullYear()

          let yearText = ' years '
          if (years === 1) {
            yearText = ' year '
          }

          return years.toString() + yearText + daysDiff.toString() + ' days'
        }
        if (days < 30) {
          return (
            '<span class="invalid-color">' +
            days.toString() +
            ' days' +
            '</span>'
          )
        }
        return days.toString() + ' days'
      }
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

    const updateSubmittedRange = () => {
      if (
        !localState.submittedStartDateTmp ||
        !localState.submittedEndDateTmp
      ) {
        localState.datePickerErr = true
        return
      }
      localState.datePickerErr = false
      submittedStartDate.value = localState.submittedStartDateTmp
      submittedEndDate.value = localState.submittedEndDateTmp
      localState.showSubmittedDatePicker = false
      registrationDateFormatted.value = 'Custom'
    }

    const resetSubmittedRange = () => {
      // reset validation
      localState.datePickerErr = false
      // reset tmp values
      localState.submittedStartDateTmp = null
      localState.submittedEndDateTmp = null
      // reset submittedInterval (will not trigger a search)
      // hide date picker
      localState.showSubmittedDatePicker = false
    }

    const selectRegistration = (val: RegistrationTypeIF) => {
      shouldClearType.value = false
      registrationType.value = val.registrationTypeAPI
    }

    const isActive = (item: RegistrationSummaryIF): boolean => {
      return item.statusType === APIStatusTypes.ACTIVE
    }

    watch(() => localState.registrationDate, (val: string) => {
      registrationDateFormatted.value = val.replaceAll('-', '/')
    })

    watch(() => localState.registrationHistory, (val) => {
      originalData.value = [...val]
      filterResults(originalData.value)
      emit('registrationTotal', val.length)
    }, { deep: true, immediate: true })

    watch(() => props.toggleSnackBar, () => {
      localState.showSnackbar = true
    })

    return {
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      showExpireDays,
      deleteDraft,
      editDraft,
      handleAction,
      rowClass,
      registrationNumber,
      displayRegistrationNumber,
      registrationType,
      shouldClearType,
      registrationDateFormatted,
      registrationTypes,
      selectRegistration,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      daysToExpiry,
      status,
      statusTypes,
      tableData,
      filterResults,
      isActive,
      updateSubmittedRange,
      resetSubmittedRange,
      downloadPDF,
      clearFilters,
      selectAndSort,
      inSelectedHeaders,
      TableActions,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.clear-filters-btn, .clear-filters-btn::before, .clear-filters-btn::after {
  background-color: transparent !important;
  height: 1rem !important;
  min-width: 0 !important;
}
.reg-table {
  max-height: 620px;
}
.date-selection {
  border-radius: 5px;
  z-index: 10;
  left: 50%;
  margin-top: 140px;
  overflow: auto;
  padding: 24px 34px 24px 34px;
  position: absolute;
  transform: translate(-50%, 0);
  background-color: white;
  width: 700px;
  td {
    padding: 0;
  }
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
  font-weight: normal !important;
  height: 30px !important;
  font-size: 14px !important;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  margin-top: -16px;
}
.down-btn {
  height: 30px !important;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  margin-top: -16px;
}
</style>
