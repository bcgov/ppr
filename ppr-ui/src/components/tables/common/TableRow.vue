<template>
  <tr :class="{
      'registration-row': true,
      'rollover-effect': applyRolloverEffect,
      'base-registration-row': !isChild && !isDraft(item),
      'draft-registration-row': isDraft(item) && !isChild,
      'font-italic': isDraft(item)
    }"
  >
    <td
      v-if="inSelectedHeaders('registrationNumber')"
      :class="isChild || isExpanded ? $style['border-left']: ''"
    >
      <v-row no-gutters>
        <v-col v-if="item.changes" class="pr-2" cols="auto">
          <v-btn
            :class="$style['btn-expand']"
            class="btn-row-expand-arr"
            color="white"
            icon
            small
            @click="toggleExpand(item)"
            @mouseover="rollover = true"
            @mouseleave="rollover = false"
          >
            <v-icon v-if="isExpanded">mdi-chevron-up</v-icon>
            <v-icon v-else>mdi-chevron-down</v-icon>
          </v-btn>
        </v-col>
        <v-col style="padding-top: 2px;">
          <p v-if="isDraft(item)" :class="{ 'ma-0': true, 'pl-9': isChild }">Pending</p>
          <!-- child drafts will sometimes show outside their base reg during the sort -->
          <div v-if="isChild || (isDraft(item) && item.baseRegistrationNumber)" :class="isChild ? 'pl-9' : ''">
            <p class="ma-0">{{ item.registrationNumber }}</p>
            <p class="ma-0" style="font-size: 0.75rem !important;">
              <b>Base Registration: {{ item.baseRegistrationNumber }}</b>
            </p>
          </div>
          <p v-else class="ma-0">
            <b>{{ item.baseRegistrationNumber }}</b>
          </p>
        </v-col>
      </v-row>
    </td>
    <td
      v-if="inSelectedHeaders('registrationType')"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    >
      <div>
        {{ getRegistrationType(item.registrationType) }}
        <span v-if="!isChild"> - Base Registration</span>
      </div>
      <v-btn
        v-if="item.changes"
        :class="[$style['btn-txt'], 'pa-0']"
        class="btn-row-expand-txt"
        color="primary"
        text
        underlined
        @click="toggleExpand(item)"
        @mouseover="rollover = true"
        @mouseleave="rollover = false"
      >
        <label style="cursor: pointer;">
          <span v-if="!isExpanded">View </span>
          <span v-else>Hide </span>
          Amendments
        </label>
      </v-btn>
    </td>
    <td v-if="inSelectedHeaders('createDateTime')" :class="isChild || item.expanded ? $style['border-left']: ''">
      <span v-if="!isDraft(item)">
        {{ getFormattedDate(item.createDateTime) }}
      </span>
      <span v-else>
        Not Registered
      </span>
    </td>
    <td
      v-if="inSelectedHeaders('statusType')"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    >
      <div v-if="!isChild || isDraft(item)">
        {{ getStatusDescription(item.statusType) }}
        <p v-if="!isChild && item.hasDraft" class="ma-0">
          <i>* Draft Amendment</i>
        </p>
      </div>
    </td>
    <td
      v-if="inSelectedHeaders('registeringName')"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    >
      {{ getRegisteringName(item.registeringName) }}
    </td>
    <td
      v-if="inSelectedHeaders('registeringParty')"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    >
      {{ item.registeringParty || '' }}
    </td>
    <td
      v-if="inSelectedHeaders('securedParties')"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    >
      {{ item.securedParties || '' }}
    </td>
    <td
      v-if="inSelectedHeaders('clientReferenceId')"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    >
      {{ item.clientReferenceId }}
    </td>
    <td
      v-if="inSelectedHeaders('expireDays')"
      v-html="showExpireDays(item)"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    />
    <td
      v-if="inSelectedHeaders('vs')"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    >
      <v-btn
        :id="`pdf-btn-${item.id}`"
        v-if="!isDraft(item) && item.path"
        class="pdf-btn px-0 mt-n3"
        depressed
        :loading="item.path === loadingPDF"
        @click="downloadPDF(item.path)"
      >
        <img src="@/assets/svgs/pdf-icon-blue.svg">
        <span class="pl-1">PDF</span>
      </v-btn>
      <v-tooltip
        v-else-if="!isDraft(item)"
        class="pa-2"
        content-class="top-tooltip"
        nudge-right="2"
        top
        transition="fade-transition"
      >
        <template v-slot:activator="{ on, attrs }">
          <v-icon color="primary" v-bind="attrs" v-on="on">mdi-information-outline</v-icon>
        </template>
        <div class="pt-2 pb-2">
          {{ tooltipTxtPdf }}
        </div>
      </v-tooltip>
    </td>

    <!-- Action Btns -->
    <td
      v-if="headers.length > 1"
      class="actions-cell pl-2 py-4"
      :style="disableActionShadow ? 'box-shadow: none; border-left: none;' : ''"
    >
      <v-row v-if="!isChild || isDraft(item)" class="actions" no-gutters>
        <v-col class="edit-action pa-0" cols="auto">
          <v-btn
            v-if="isDraft(item)"
            :class="$style['edit-btn']"
            color="primary"
            elevation="0"
            @click="editDraft(item)"
          >
            <span>Edit</span>
          </v-btn>
          <v-btn
            v-else-if="isRepairersLien(item) && isActive(item)"
            :class="$style['edit-btn']"
            style="flex:0"
            color="primary"
            elevation="0"
            @click="handleAction(item, TableActions.DISCHARGE)"
          >
            <span :class="[$style['discharge-btn'], 'text-wrap']">Total Discharge</span>
          </v-btn>
          <v-btn
            v-else-if="!isExpired(item) && !isDischarged(item)"
            :class="$style['edit-btn']"
            color="primary"
            elevation="0"
            @click="handleAction(item, TableActions.AMEND)"
          >
            <span>Amend</span>
          </v-btn>
          <v-btn
            v-else
            color="primary"
            style="height:36px"
            elevation="0"
            @click="handleAction(item, TableActions.REMOVE)"
          >
            <span :class="[$style['remove-btn'], 'text-wrap']">Remove From<br>Table</span>
          </v-btn>
        </v-col>
        <v-col class="actions__more pa-0" v-if="!isExpired(item) && !isDischarged(item)">
          <v-menu offset-y left nudge-bottom="4" @input="freezeScrolling($event)">
            <template v-slot:activator="{ on: onMenu, value }">
              <v-btn
                small
                elevation="0"
                v-on="onMenu"
                color="primary"
                class="actions__more-actions__btn reg-table"
                :class="$style['down-btn']"
              >
                <v-icon v-if="value">mdi-menu-up</v-icon>
                <v-icon v-else>mdi-menu-down</v-icon>
              </v-btn>
            </template>
            <v-list v-if="isDraft(item)" class="actions__more-actions registration-actions">
              <v-list-item
                @click="deleteDraft(item, TableActions.DELETE)"
              >
                <v-list-item-subtitle>
                  <v-icon small>mdi-delete</v-icon>
                  <span class="ml-1">Delete Draft</span>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
            <v-list v-else class="actions__more-actions registration-actions">
               <v-list-item v-if="isRepairersLien(item)" @click="handleAction(item, TableActions.AMEND)">
                <v-list-item-subtitle>
                  <v-icon small>mdi-pencil</v-icon>
                  <span class="ml-1">Amend</span>
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item
                v-if="isActive(item) && !isExpired(item) && !isDischarged(item) && !isRepairersLien(item)"
                @click="handleAction(item, TableActions.DISCHARGE)"
              >
                <v-list-item-subtitle>
                  <v-icon small>mdi-note-remove-outline</v-icon>
                  <span class="ml-1">Total Discharge</span>
                </v-list-item-subtitle>
              </v-list-item>
              <v-tooltip
                left
                content-class="left-tooltip pa-2 mr-2"
                transition="fade-transition"
                :disabled="!isRenewalDisabled(item)"
              >
                <template v-slot:activator="{ on: onTooltip }">
                  <div v-on="onTooltip">
                    <v-list-item
                      v-if="isActive(item) && !isExpired(item) && !isDischarged(item)"
                      :disabled="isRenewalDisabled(item)"
                      @click="handleAction(item, TableActions.RENEW)"
                    >
                      <v-list-item-subtitle>
                        <v-icon small>mdi-calendar-clock</v-icon>
                        <span class="ml-1">Renew</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </div>
                </template>
                <span v-if="item.expireDays === -99">
                  Infinite registrations cannot be renewed.
                </span>
              </v-tooltip>
              <v-list-item @click="handleAction(item, TableActions.REMOVE)">
                <v-list-item-subtitle>
                  <v-icon small>mdi-delete</v-icon>
                  <span class="ml-1">Remove From Table</span>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-col>
      </v-row>
    </td>
  </tr>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  computed,
  watch
} from '@vue/composition-api'
import { registrationPDF } from '@/utils' // eslint-disable-line

// local types/helpers/etc.
import {
  RegistrationSummaryIF, // eslint-disable-line no-unused-vars
  BaseHeaderIF, // eslint-disable-line no-unused-vars
  DraftResultIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import {
  APIRegistrationTypes,
  APIStatusTypes, // eslint-disable-line no-unused-vars
  DraftTypes, // eslint-disable-line no-unused-vars
  TableActions // eslint-disable-line no-unused-vars
} from '@/enums'
import { useRegistration } from '@/composables/useRegistration'

export default defineComponent({
  name: 'TableRow',
  props: {
    setDisableActionShadow: { default: false },
    setChild: { default: false },
    setHeaders: { default: [] as BaseHeaderIF[] },
    setIsExpanded: { default: false },
    setItem: { default: {} as (RegistrationSummaryIF | DraftResultIF) }
  },
  emits: ['action', 'error', 'freezeScroll', 'toggleExpand'],
  setup (props, { emit }) {
    const {
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      getRegisteringName,
      registrationNumber,
      registeringParty,
      hasRenewal,
      securedParties
    } = useRegistration(null)

    const localState = reactive({
      loadingPDF: '',
      rollover: false,
      applyRolloverEffect: computed((): boolean => {
        return localState.rollover || localState.isExpanded
      }),
      disableActionShadow: computed((): boolean => {
        return props.setDisableActionShadow
      }),
      headers: computed(() => {
        return props.setHeaders
      }),
      isChild: computed(() => {
        return props.setChild
      }),
      isExpanded: computed(() => {
        return props.setIsExpanded
      }),
      item: computed(() => {
        if (!isDraft(props.setItem) && !props.setChild) {
          // if base reg && not draft check to update expand
          const baseReg = props.setItem as RegistrationSummaryIF
          if (baseReg.expand !== undefined && (baseReg.expand !== props.setIsExpanded)) {
            toggleExpand(props.setItem)
          }
        }
        return props.setItem
      })
    })

    const deleteDraft = (item: DraftResultIF): void => {
      emit('action', {
        action: TableActions.DELETE,
        docId: item.documentId,
        regNum: item.baseRegistrationNumber
      })
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

    const getDayOfYear = (dateOfYear: Date) => {
      var start = new Date(dateOfYear.getFullYear(), 0, 0)
      var diff = (dateOfYear.valueOf() - start.valueOf()) +
        ((start.getTimezoneOffset() - dateOfYear.getTimezoneOffset()) * 60 * 1000)
      var oneDay = 1000 * 60 * 60 * 24
      return Math.floor(diff / oneDay)
    }

    const freezeScrolling = (isMenuOpen: boolean) => {
      emit('freezeScroll', isMenuOpen)
    }

    const handleAction = (item: RegistrationSummaryIF, action: TableActions): void => {
      emit('action', { action: action, regNum: item.baseRegistrationNumber })
    }

    const inSelectedHeaders = (search: string) => {
      return localState.headers.find((header) => { return header.value === search })
    }

    const isActive = (item: RegistrationSummaryIF): boolean => {
      return item.statusType === APIStatusTypes.ACTIVE
    }

    const isDischarged = (item: RegistrationSummaryIF): boolean => {
      return item.statusType === APIStatusTypes.DISCHARGED
    }

    const isRenewalDisabled = (item: RegistrationSummaryIF): boolean => {
      return (item.expireDays === -99)
    }

    const isDraft = (item: any): boolean => {
      // RegistrationSummaryIF | DraftResultIF
      return item.type !== undefined
    }

    const isExpired = (item: RegistrationSummaryIF): boolean => {
      return item.statusType === APIStatusTypes.EXPIRED
    }

    const isRepairersLien = (item: RegistrationSummaryIF): boolean => {
      return item.registrationType === APIRegistrationTypes.REPAIRERS_LIEN
    }

    const showExpireDays = (item: RegistrationSummaryIF): string => {
      if (localState.isChild) return ''
      if (isExpired(item) || isDischarged(item)) return '—'

      const days = item.expireDays
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
          const currentDayOfYear = getDayOfYear(dateToday)
          const expDayOfYear = getDayOfYear(dateExpiry)
          let daysDiff = expDayOfYear - currentDayOfYear
          if (daysDiff < 0) {
            dateExpiry.setFullYear(dateExpiry.getFullYear() - 1)
            daysDiff = 365 + daysDiff
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

    const toggleExpand = (val: any) => {
      emit('toggleExpand', val)
    }

    const tooltipTxtPdf = 'Verification Statements are only available ' +
      'to Secured Parties or the Registering Party of this filing. To ' +
      'view the details of this registration you must conduct a search.'

    watch(() => props.setItem, (val) => {
    }, { deep: true, immediate: true })

    return {
      freezeScrolling,
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      getRegisteringName,
      showExpireDays,
      deleteDraft,
      editDraft,
      handleAction,
      registrationNumber,
      registeringParty,
      securedParties,
      isActive,
      isDischarged,
      isDraft,
      isExpired,
      isRepairersLien,
      isRenewalDisabled,
      hasRenewal,
      downloadPDF,
      inSelectedHeaders,
      TableActions,
      toggleExpand,
      tooltipTxtPdf,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.border-left:nth-child(1) {
  border-left: 3px solid $primary-blue
}
.btn-expand {
  background-color: $primary-blue;
  height: 25px !important;
  width: 25px !important;
}
.btn-txt, .btn-txt::before, .btn-txt::after {
  background-color: transparent !important;
  font-size: 0.75rem !important;
  height: 14px !important;
  min-width: 0 !important;
  text-decoration: underline;
}
.down-btn {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
  height: 35px !important;
  width: 35px;
}
.edit-btn {
  border-bottom-right-radius: 0;
  border-top-right-radius: 0;
  font-size: 14px !important;
  font-weight: normal !important;
  height: 35px !important;
  width: 100px;
}
.remove-btn {
  width: 105px;
  font-weight: normal !important;
  line-height: 14px !important;
}
.discharge-btn {
  line-height: 14px;
  width: 90px;
}
</style>
