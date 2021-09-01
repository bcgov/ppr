<template>
  <v-container fluid no-gutters class="pa-0">
    <registration-confirmation
      attach="#app"
      :options="dischargeConfirmationDialog"
      :display="showDialog"
      :registrationNumber="currentRegistrationNumber"
      @proceed="dischargeSubmit()"
      @confirmationClose="closeConfirmation()"
    />
    <div :class="$style['col-selection']">
      <v-text-field
        v-model="search"
        :class="[$style['text-input-style'], 'column-selection', 'mr-4']"
        append-icon="mdi-magnify"
        label="Find Registrations Containing"
        dense
        single-line
        hide-details
        style="width:250px"
      ></v-text-field>
      <v-select
        id="column-selection"
        dense
        :class="[$style['text-input-style'], 'column-selection']"
        attach
        autocomplete="off"
        :items="colheaders"
        :menu-props="dropdownPropsXl"
        multiple
        hide-details="true"
        placeholder="Columns to Show"
        style="width: 200px;"
        v-model="selectedHeaderValues"
      >
        <template v-slot:selection="{ index }">
          <span v-if="index === 0">Columns to Show</span>
        </template>
      </v-select>
    </div>
    <v-card
      v-if="showSubmittedDatePicker"
      :class="[$style['date-selection'], 'registration-date']"
      elevation="6"
    >
      <v-row no-gutters>
        <v-col cols="6" :class="$style['picker-title']"
          >Select Start Date:</v-col
        >
        <v-col cols="6" :class="[$style['picker-title'], 'pl-4']"
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
            flat
            ripple
            small
            @click="updateSubmittedRange"
            >OK</v-btn
          >
          <v-btn
            class="date-selection-btn ml-4"
            flat
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
      class="registration-table pt-4"
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
      no-data-text="No registrations created yet."
    >
      <template slot="header" :headers="getDisplayedHeaders">
        <thead>
          <tr>
            <th
              v-for="(header, i) in getDisplayedHeaders"
              :class="header.class"
              :key="'find-header-' + i"
              class="text-left header-row-1 pa-0 pl-2"
              @click="selectAndSort(header.value)"
            >
              <span>
                {{ header.text }}
                <v-icon
                  v-if="
                    header.value === selectedSort &&
                      currentOrder === 'asc' &&
                      header.sortable
                  "
                  small
                  style="color: black;"
                >
                  mdi-arrow-down
                </v-icon>
                <v-icon
                  v-else-if="
                    header.value === selectedSort &&
                      currentOrder === 'desc' &&
                      header.sortable
                  "
                  small
                  style="color: black;"
                >
                  mdi-arrow-up
                </v-icon>
              </span>
            </th>
          </tr>
        </thead>
      </template>
      <template v-slot:body.prepend>
        <tr class="filter-row">
          <td v-if="selectedHeaderValues.includes('registrationNumber')">
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="registrationNumber"
              type="text"
              label="Number"
              dense
            ></v-text-field>
          </td>
          <td v-if="selectedHeaderValues.includes('registrationType')">
            <registration-bar-type-ahead-list
              v-if="hasRPPR"
              :defaultLabel="labelText"
              :defaultDense="true"
              @selected="selectRegistration($event)"
            />
            <v-select
              v-else
              :items="registrationTypes"
              single-line
              item-text="registrationTypeUI"
              item-value="registrationTypeAPI"
              filled
              dense
              clearable
              label="Registration Type"
              v-model="registrationType"
              id="txt-type"
            >
              <template slot="item" slot-scope="data">
                <span class="list-item">
                  {{ data.item.registrationTypeUI }}
                </span>
              </template>
            </v-select>
          </td>
          <td v-if="selectedHeaderValues.includes('createDateTime')">
            <v-text-field
              filled
              single-line
              id="reg-textfield"
              data-test-id="reg-date-text"
              v-model="registrationDateFormatted"
              hint="YYYY/MM/DD"
              append-icon="mdi-calendar"
              @click="showSubmittedDatePicker = true"
              dense
              hide-details="true"
            />
          </td>
          <td v-if="selectedHeaderValues.includes('statusType')">
            <v-select
              :items="statusTypes"
              single-line
              filled
              dense
              label="Status"
              v-model="status"
              id="txt-status"
              @change="filterResults"
              clearable
            >
              <template slot="item" slot-scope="data">
                <span class="list-item">
                  {{ data.item.text }}
                </span>
              </template>
            </v-select>
          </td>
          <td v-if="selectedHeaderValues.includes('registeringName')">
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="registeredBy"
              type="text"
              label="Registered By"
              dense
            ></v-text-field>
          </td>
          <td v-if="selectedHeaderValues.includes('registeringParty')">
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="registeringParty"
              type="text"
              label="Registering Party"
              dense
            ></v-text-field>
          </td>
          <td v-if="selectedHeaderValues.includes('securedParties')">
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="securedParties"
              type="text"
              label="Secured Parties"
              dense
            ></v-text-field>
          </td>
          <td v-if="selectedHeaderValues.includes('clientReferenceId')">
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="folioNumber"
              type="text"
              label=""
              dense
            ></v-text-field>
          </td>
          <td v-if="selectedHeaderValues.includes('expireDays')">
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="daysToExpiry"
              type="text"
              label="Days to Expiry"
              dense
            ></v-text-field>
          </td>
          <td></td>
          <td></td>
        </tr>
      </template>
      <template v-slot:item="row" class="registration-data-table">
        <tr
          :key="row.item.id"
          class="registration-row"
          v-if="!row.item.hide"
          :class="rowClass(row.item)"
        >
          <td
            v-if="selectedHeaderValues.includes('registrationNumber')"
            v-html="
              displayRegistrationNumber(
                row.item.baseRegistrationNumber,
                row.item.registrationNumber
              )
            "
          ></td>
          <td v-if="selectedHeaderValues.includes('registrationType')">
            {{ getRegistrationType(row.item.registrationType) }}
          </td>
          <td v-if="selectedHeaderValues.includes('createDateTime')">
            {{ getFormattedDate(row.item.createDateTime) }}
          </td>
          <td v-if="selectedHeaderValues.includes('statusType')">
            {{ getStatusDescription(row.item.statusType) }}
          </td>
          <td v-if="selectedHeaderValues.includes('registeringName')">
            {{ row.item.registeringName }}
          </td>
          <td v-if="selectedHeaderValues.includes('registeringParty')">
            {{ row.item.registeringParty || '' }}
          </td>
          <td v-if="selectedHeaderValues.includes('securedParties')">
            {{ row.item.securedParties || '' }}
          </td>
          <td v-if="selectedHeaderValues.includes('clientReferenceId')">
            {{ row.item.clientReferenceId }}
          </td>
          <td v-if="selectedHeaderValues.includes('expireDays')">
            {{ row.item.expireDays || '' }}
          </td>
          <td v-if="selectedHeaderValues.includes('vs')">
            <v-btn
              :id="`pdf-btn-${row.item.id}`"
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
            <div class="actions" v-if="row.item.statusType === 'D'">
              <span class="edit-action">
                <v-btn
                  color="primary"
                  :class="$style['edit-btn']"
                  :id="'class-' + row.index + '-change-added-btn'"
                >
                  <span>Edit</span>
                </v-btn>
              </span>

              <span class="actions__more">
                <v-menu offset-y left nudge-bottom="4">
                  <template v-slot:activator="{ on }">
                    <v-btn
                      small
                      v-on="on"
                      color="primary"
                      class="actions__more-actions__btn"
                      :class="$style['down-btn']"
                    >
                      <v-icon>mdi-menu-down</v-icon>
                    </v-btn>
                  </template>
                  <v-list class="actions__more-actions">
                    <v-list-item>
                      <v-list-item-subtitle>
                        <v-icon small>mdi-delete</v-icon>
                        <span class="ml-1">Delete</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </span>
            </div>

            <div class="actions" v-if="row.item.statusType !== 'D'">
              <span class="edit-action">
                <v-btn
                  color="primary"
                  :class="$style['edit-btn']"
                  :id="'class-' + row.index + '-change-added-btn'"
                >
                  <span>Open</span>
                </v-btn>
              </span>

              <span class="actions__more">
                <v-menu offset-y left nudge-bottom="4">
                  <template v-slot:activator="{ on }">
                    <v-btn
                      small
                      v-on="on"
                      color="primary"
                      class="actions__more-actions__btn"
                      :class="$style['down-btn']"
                    >
                      <v-icon>mdi-menu-down</v-icon>
                    </v-btn>
                  </template>
                  <v-list class="actions__more-actions registration-actions">
                    <v-list-item v-if="isAllowedAmendment(row.item)">
                      <v-list-item-subtitle>
                        <v-icon small>mdi-pencil</v-icon>
                        <span class="ml-1">Amend</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item v-if="isAllowedDischarge(row.item)">
                      <v-list-item-subtitle>
                        <v-icon small>mdi-note-remove-outline</v-icon>
                        <span class="ml-1" @click="discharge(row.item)"
                          >Total Discharge</span
                        >
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item
                      v-if="isAllowedRenewal(row.item)"
                      :disabled="row.item.expireDays === -99"
                    >
                      <v-tooltip
                        left
                        content-class="left-tooltip pa-2"
                        transition="fade-transition"
                        :disabled="row.item.expireDays !== -99"
                      >
                        <template v-slot:activator="{ on }">
                          <v-list-item-subtitle v-on="on">
                            <v-icon small>mdi-calendar-clock</v-icon>
                            <span class="ml-1">Renew</span>
                          </v-list-item-subtitle>
                        </template>
                        Infinite registrations cannot be renewed.
                      </v-tooltip>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-subtitle>
                        <v-icon small>mdi-delete</v-icon>
                        <span class="ml-1">Remove from table</span>
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
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  computed,
  onMounted
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'

import {
  registrationTableHeaders,
  dischargeConfirmationDialog
} from '@/resources'
import { registrationHistory, draftHistory, registrationPDF } from '@/utils' // eslint-disable-line
import {
  RegistrationSummaryIF, // eslint-disable-line no-unused-vars
  AccountProductSubscriptionIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import {
  AccountProductCodes,
  AccountProductRoles, // eslint-disable-line no-unused-vars
  APIStatusTypes
} from '@/enums'
import { useRegistration } from '@/composables/useRegistration'
import { RegistrationConfirmation } from '@/components/dialogs'
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'

export default defineComponent({
  components: {
    RegistrationConfirmation,
    RegistrationBarTypeAheadList
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit, root }) {
    const {
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      registrationNumber,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      status,
      registrationType,
      registrationTypes,
      daysToExpiry,
      submittedStartDate,
      submittedEndDate,
      statusTypes,
      tableData,
      filterResults,
      originalData
    } = useRegistration()
    const { getAccountProductSubscriptions } = useGetters<any>([
      'getAccountProductSubscriptions'
    ])

    const localState = reactive({
      headers: registrationTableHeaders,
      registrationDateFormatted: '',
      showDialog: false,
      currentRegistrationNumber: '',
      showSubmittedDatePicker: false,
      submittedStartDateTmp: null,
      submittedEndDateTmp: null,
      datePickerErr: false,
      registrationDate: '',
      loadingPDF: '',
      loadingData: true,
      currentOrder: 'asc',
      selectedSort: 'number',
      search: '',
      labelText: 'Registration Type',
      selectedHeaderValues: [
        'registrationNumber',
        'registrationType',
        'createDateTime',
        'statusType',
        'registeringName',
        'registeringParty',
        'securedParties',
        'clientReferenceId',
        'expireDays',
        'vs'
      ],
      dropdownPropsXl: {
        minWidth: '200px',
        maxHeight: 'none'
      },
      colheaders: computed(function () {
        const columns = [...localState.headers]
        columns.pop()
        return columns
      }),
      getDisplayedHeaders: computed(function () {
        const displayed = []
        for (let i = 0; i < localState.headers.length; i++) {
          if (localState.headers[i].display) {
            displayed.push(localState.headers[i])
          }
        }
        return displayed
      })
    })

    const hasRPPR = computed(() => {
      const productSubscriptions = getAccountProductSubscriptions.value as AccountProductSubscriptionIF
      return (
        productSubscriptions?.[AccountProductCodes.RPPR].roles.includes(
          AccountProductRoles.EDIT
        ) || false
      )
    })

    const rowClass = (item: RegistrationSummaryIF): string => {
      if (item.statusType === 'D') {
        return 'font-italic'
      } else {
        if (item.baseRegistrationNumber === item.registrationNumber) {
          return 'base-registration-row'
        }
      }

      return ''
    }

    const displayRegistrationNumber = (
      baseReg: string,
      actualReg: string
    ): string => {
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

    const formatDate = (date: string): string => {
      if (!date) return ''
      const [year, month, day] = date.split('-')
      return `${year}/${month}/${day}`
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
      localState.registrationDateFormatted = 'Custom'
    }

    const resetSubmittedRange = () => {
      // reset validation
      localState.datePickerErr = false
      // reset tmp values
      localState.submittedStartDateTmp = localState.submittedStartDate
      localState.submittedEndDateTmp = localState.submittedEndDate
      // reset submittedInterval (will not trigger a search)
      // hide date picker
      localState.showSubmittedDatePicker = false
    }

    const selectRegistration = (val: RegistrationTypeIF) => {
      registrationType.value = val.registrationTypeAPI
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

    const discharge = (item): void => {
      localState.currentRegistrationNumber = item.registrationNumber as string
      localState.showDialog = true
    }

    const dischargeSubmit = (): void => {
      emit('discharge', localState.currentRegistrationNumber)
    }

    const closeConfirmation = (): void => {
      localState.showDialog = false
    }

    const isAllowedRenewal = (item): boolean => {
      if (item.statusType === APIStatusTypes.ACTIVE) {
        return true
      }
      return false
    }

    const isAllowedDischarge = (item): boolean => {
      if (item.statusType === APIStatusTypes.ACTIVE) {
        return true
      }
      return false
    }

    const isAllowedAmendment = (item): boolean => {
      if (item.statusType === APIStatusTypes.ACTIVE) {
        return true
      }
      return false
    }

    /** Get the drafts and financing statements from the api. */
    onMounted(async () => {
      try {
        const registrations = await registrationHistory()
        const drafts = await draftHistory()
        if (drafts) {
          Array.prototype.push.apply(tableData.value, drafts)
          // assign a draft status to draft agreements
          for (let i = 0; i < tableData.value.length; i++) {
            if (!tableData.value[i].statusType) {
              tableData.value[i].statusType = 'D'
            }
            if (!tableData.value[i].registrationNumber) {
              tableData.value[i].registrationNumber = 'Pending'
            }
          }
        }
        if (registrations) {
          Array.prototype.push.apply(tableData.value, registrations)
        }
        localState.loadingData = false
        originalData.value = tableData.value
      } catch (error) {
        alert(error)
      }
    })

    watch(
      () => localState.registrationDate,
      (val: string) => {
        localState.registrationDateFormatted = formatDate(val)
      }
    )

    watch(
      () => localState.selectedHeaderValues,
      val => {
        if (val) {
          for (let i = 0; i < localState.headers.length; i++) {
            // disclude the unchecked values, always include actions
            if (
              !val.includes(localState.headers[i].value) &&
              localState.headers[i].value !== 'actions'
            ) {
              localState.headers[i].display = false
            } else {
              localState.headers[i].display = true
            }
          }
        }
      }
    )

    return {
      getFormattedDate,
      dischargeConfirmationDialog,
      closeConfirmation,
      getRegistrationType,
      getStatusDescription,
      discharge,
      dischargeSubmit,
      rowClass,
      registrationNumber,
      displayRegistrationNumber,
      registrationType,
      registrationTypes,
      hasRPPR,
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
      isAllowedRenewal,
      isAllowedDischarge,
      isAllowedAmendment,
      updateSubmittedRange,
      resetSubmittedRange,
      downloadPDF,
      selectAndSort,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.reg-table {
  max-height: 550px;
  overflow-y: scroll;
}
.length-trust-label {
  font-size: 0.875rem;
}
.summary-text {
  font-size: 14px;
  color: $gray7;
}
.title-text {
  color: $gray9 !important;
}
.summary-cell {
  overflow: visible;
  text-overflow: inherit;
  white-space: inherit;
}
.date-selection {
  border-radius: 5px;
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
.picker-title {
  font-size: 14px;
  font-weight: bold;
  color: $gray9;
}

.col-selection {
  position: relative;
  top: -100px;
  float: right;
  height: 0px;
  display: inline-flex;
}
.text-input-style {
  background-color: white !important;
  border: 1px solid var(--outline);
  height: 45px;
  font-size: 13px;
  margin: 0;
  color: var(--text);
  label {
    font-size: 13px;
    color: $gray7 !important;
  }
  span {
    color: $gray7;
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
  font-size: 12px !important;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
.down-btn {
  height: 30px !important;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
</style>
