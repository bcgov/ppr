<template>
  <v-container fluid no-gutters class="pa-0">
    <div :class="$style['col-selection']">
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
      :headers="getDisplayedHeaders"
      :items="tableData"
      disable-pagination
      hide-default-footer
      :sort-by.sync="sortBy"
      :sort-desc.sync="sortDesc"
      no-data-text="No registrations created yet."
    >
      <template v-slot:body.prepend>
        <tr class="filter-row">
          <td v-if="selectedHeaderValues.includes('number')">
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
          <td v-if="selectedHeaderValues.includes('type')">
            <v-select
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
          <td v-if="selectedHeaderValues.includes('rdate')">
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
          <td v-if="selectedHeaderValues.includes('status')">
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
          <td v-if="selectedHeaderValues.includes('rby')">
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
          <td v-if="selectedHeaderValues.includes('rparty')">
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
          <td v-if="selectedHeaderValues.includes('sp')">
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
          <td v-if="selectedHeaderValues.includes('folio')">
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
          <td v-if="selectedHeaderValues.includes('edays')">
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
          :class="draftClass(row.item.statusType)"
        >
          <td class="font-weight-bold" v-if="selectedHeaderValues.includes('number')"
          v-html="displayRegistrationNumber(row.item.baseRegistrationNumber, row.item.registrationNumber)">
          </td>
          <td v-if="selectedHeaderValues.includes('type')">
            {{ getRegistrationType(row.item.registrationType) }}
          </td>
          <td v-if="selectedHeaderValues.includes('rdate')">
            {{ getFormattedDate(row.item.createDateTime) }}
          </td>
          <td v-if="selectedHeaderValues.includes('status')">
            {{ getStatusDescription(row.item.statusType) }}
          </td>
          <td v-if="selectedHeaderValues.includes('rby')"></td>
          <td v-if="selectedHeaderValues.includes('rparty')">
            {{ row.item.registeringParty || '' }}
          </td>
          <td v-if="selectedHeaderValues.includes('sp')">
            {{ row.item.securedParties || '' }}
          </td>
          <td v-if="selectedHeaderValues.includes('folio')">
            {{ row.item.clientReferenceId }}
          </td>
          <td v-if="selectedHeaderValues.includes('edays')">
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
                  <v-list class="actions__more-actions">
                    <v-list-item>
                      <v-list-item-subtitle>
                        <v-icon small>mdi-pencil</v-icon>
                        <span class="ml-1">Amend</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-subtitle>
                        <v-icon small>mdi-clipboard-check-outline</v-icon>
                        <span class="ml-1" @click="discharge(row.item)">Total Discharge</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-subtitle>
                        <v-icon small>mdi-calendar-clock</v-icon>
                        <span class="ml-1">Renew</span>
                      </v-list-item-subtitle>
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

import { registrationTableHeaders } from '@/resources'
import { registrationHistory, draftHistory, registrationPDF } from '@/utils' // eslint-disable-line
import { useRegistration } from '@/composables/useRegistration'

export default defineComponent({
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

    const localState = reactive({
      headers: registrationTableHeaders,
      registrationDateFormatted: '',
      showSubmittedDatePicker: false,
      submittedStartDateTmp: null,
      submittedEndDateTmp: null,
      datePickerErr: false,
      registrationDate: '',
      loadingPDF: '',
      loadingData: true,
      sortBy: 'number',
      sortDesc: false,
      selectedHeaderValues: [
        'number',
        'type',
        'rdate',
        'status',
        'rby',
        'rparty',
        'sp',
        'folio',
        'edays',
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

    const draftClass = (val: string): string => {
      if (val === 'D') {
        return 'font-italic'
      }
      return ''
    }

    const displayRegistrationNumber = (baseReg: string, actualReg: string): string => {
      if (baseReg) {
        if (baseReg === actualReg) {
          return baseReg
        }
        return baseReg + '<br><span class="font-italic font-weight-regular">Registration Number:<br>' +
          actualReg + '</span>'
      }
      return actualReg
    }

    const formatDate = (date: string): string => {
      if (!date) return ''
      const [year, month, day] = date.split('-')
      return `${year}/${month}/${day}`
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
      const registrationNumber = item.registrationNumber as string
      emit('discharge', registrationNumber)
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
            tableData.value[i].statusType = 'D'
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
      getRegistrationType,
      getStatusDescription,
      discharge,
      draftClass,
      registrationNumber,
      displayRegistrationNumber,
      registrationType,
      registrationTypes,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      daysToExpiry,
      status,
      statusTypes,
      tableData,
      filterResults,
      updateSubmittedRange,
      resetSubmittedRange,
      downloadPDF,
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
}
.text-input-style {
  background-color: white !important;
  border: 1px solid var(--outline);
  height: 45px;
  font-size: 13px;
  margin: 0;
  color: var(--text);
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
