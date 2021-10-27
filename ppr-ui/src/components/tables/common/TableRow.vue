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
          <p v-if="isDraft(item)" class="ma-0 pl-9">Pending</p>
          <div v-else-if="isChild" class="pl-9">
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
      </div>
    </td>
    <td
      v-if="inSelectedHeaders('registeringName')"
      :class="isChild || item.expanded ? $style['border-left']: ''"
    >
      {{ item.registeringName }}
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
        v-if="!isDraft(item)"
        class="pdf-btn px-0 mt-n3"
        depressed
        :loading="item.path === loadingPDF"
        @click="downloadPDF(item.path)"
      >
        <svg
          width="19px"
          height="19px"
          viewBox="0 0 19 19"
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          xmlns:xlink="http://www.w3.org/1999/xlink"
        >
          <title>new pdf icon copy 4</title>
          <defs>
            <filter color-interpolation-filters="auto" id="filter-1">
              <feColorMatrix
                in="SourceGraphic"
                type="matrix"
                values="0 0 0 0 1.000000 0 0 0 0 1.000000 0 0 0 0 1.000000 0 0 0 1.000000 0"
              />
            </filter>
          </defs>
          <g id="Symbols" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
            <g id="My-Searches" transform="translate(-1105.000000, -368.000000)">
              <g id="new-pdf-icon-copy-5" transform="translate(1105.000000, 368.000000)">
                <g id="file-document-outline-(1)" fill="#1669BB" fill-rule="nonzero">
                  <path
                    d="M3.63984674,1.9 L3.63984674,17.1 C3.63984674,18.149341 4.47095034,19 5.49616858,
                      19 L16.6340996,19 C17.6593179,19 18.4904215,18.149341 18.4904215,17.1 L18.4904215,
                      5.7 L12.9214559,0 L5.49616858,0 C4.47095034,0 3.63984674,0.850658975 3.63984674,
                      1.9 Z M11.993295,1.4952381 L11.993295,5.2452381 C11.993295,5.52138047 12.2171526,
                      5.7452381 12.493295,5.7452381 L17.0388615,5.7452381 C17.3150039,
                      5.7452381 17.5388615,5.96909572 17.5388615,6.2452381 L17.5388615,
                      17.5047619 C17.5388615,17.7809043 17.3150039,18.0047619 17.0388615,
                      18.0047619 L5.09140668,18.0047619 C4.8152643,18.0047619 4.59140668,
                      17.7809043 4.59140668,17.5047619 L4.59140668,1.4952381 C4.59140668,
                      1.21909572 4.8152643,0.995238095 5.09140668,0.995238095 L11.493295,
                      0.995238095 C11.7694374,0.995238095 11.993295,1.21909572 11.993295,
                      1.4952381 Z M0,9.04705882 L0,13.7529412 C4.47140469e-16,14.3052259 0.44771525,
                      14.7529412 1,14.7529412 L13.7777778,14.7529412 C14.3300625,14.7529412 14.7777778,
                      14.3052259 14.7777778,13.7529412 L14.7777778,9.04705882 C14.7777778,
                      8.49477407 14.3300625,8.04705882 13.7777778,8.04705882 L1,8.04705882 C0.44771525,
                      8.04705882 -1.78657678e-16,8.49477407 0,9.04705882 Z"
                    id="Shape"
                  />
                </g>
                <g id="PDF" transform="translate(1.585568, 9.144000)" filter="url(#filter-1)">
                  <g>
                    <path
                      d="M1.00455182,
                        4.75 L1.00455182,3.06022409 L1.43697479,3.06022409 C2.82072829,3.06022409 3.2797619,
                        2.32177871 3.2797619,1.48354342 C3.2797619,0.558823529 2.74089636,
                        0 1.51680672,0 L0,0 L0,4.75 L1.00455182,4.75 Z M1.33718487,2.23529412 L1.00455182,
                        2.23529412 L1.00455182,0.824929972 L1.46358543,0.824929972 C1.99579832,
                        0.824929972 2.26190476,1.05777311 2.26190476,1.51680672 C2.26190476,
                        2.02240896 1.90266106,2.23529412 1.33718487,2.23529412 Z M5.52170868,4.75 C7.15161064,
                        4.75 8.1162465,3.93172269 8.1162465,2.32843137 C8.1162465,0.81162465 7.15161064,
                        0 5.66806723,0 L4.17787115,0 L4.17787115,4.75 L5.52170868,4.75 Z M5.61484594,
                        3.91841737 L5.18242297,3.91841737 L5.18242297,0.824929972 L5.72128852,
                        0.824929972 C6.59943978,0.824929972 7.07177871,1.31057423 7.07177871,
                        2.35504202 C7.07177871,3.3995098 6.58613445,3.91841737 5.61484594,
                        3.91841737 Z M10.0920868,4.75 L10.0920868,2.87394958 L11.7020308,2.87394958 L11.7020308,
                        2.04901961 L10.0920868,2.04901961 L10.0920868,0.824929972 L11.8217787,
                        0.824929972 L11.8217787,0 L9.10084034,0 L9.10084034,4.75 L10.0920868,4.75 Z"
                      fill="#1669BB"
                      fill-rule="nonzero"
                    />
                  </g>
                </g>
              </g>
            </g>
          </g>
        </svg>
        <span class="pl-1">PDF</span>
      </v-btn>
    </td>

    <!-- Action Btns -->
    <td v-if="headers.length > 1" class="actions-cell pl-2 py-4">
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
            :class="$style['edit-btn']"
            color="primary"
            elevation="0"
          >
            <span>Re-Register</span>
          </v-btn>
        </v-col>
        <v-col class="actions__more pa-0">
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
              <v-list-item
                v-if="isActive(item) && !isExpired(item) && !isDischarged(item)"
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
                :disabled="item.expireDays !== -99"
              >
                <template v-slot:activator="{ on: onTooltip }">
                  <div v-on="onTooltip">
                    <v-list-item
                      v-if="isActive(item) && !isExpired(item) && !isDischarged(item)"
                      :disabled="item.expireDays === -99"
                      @click="handleAction(item, TableActions.RENEW)"
                    >
                      <v-list-item-subtitle>
                        <v-icon small>mdi-calendar-clock</v-icon>
                        <span class="ml-1">Renew</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </div>
                </template>
                Infinite registrations cannot be renewed.
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
  APIStatusTypes, // eslint-disable-line no-unused-vars
  DraftTypes, // eslint-disable-line no-unused-vars
  TableActions // eslint-disable-line no-unused-vars
} from '@/enums'
import { useRegistration } from '@/composables/useRegistration'

export default defineComponent({
  name: 'TableRow',
  props: {
    setChild: { default: false },
    setHeaders: { default: [] as BaseHeaderIF[] },
    setIsExpanded: { default: false },
    setItem: { default: {} as (RegistrationSummaryIF | DraftResultIF) }
  },
  emits: ['action', 'error', 'toggleExpand'],
  setup (props, { emit }) {
    const {
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      registrationNumber,
      registeringParty,
      securedParties
    } = useRegistration()

    const localState = reactive({
      loadingPDF: '',
      rollover: false,
      applyRolloverEffect: computed((): boolean => {
        return localState.rollover || localState.isExpanded
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

    const getDayOfYear = (dateOfYear: Date) => {
      var start = new Date(dateOfYear.getFullYear(), 0, 0)
      var diff = (dateOfYear.valueOf() - start.valueOf()) +
        ((start.getTimezoneOffset() - dateOfYear.getTimezoneOffset()) * 60 * 1000)
      var oneDay = 1000 * 60 * 60 * 24
      return Math.floor(diff / oneDay)
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

    const isDraft = (item: any): boolean => {
      // RegistrationSummaryIF | DraftResultIF
      return item.type !== undefined
    }

    const isExpired = (item: RegistrationSummaryIF): boolean => {
      return item.statusType === APIStatusTypes.EXPIRED
    }

    const showExpireDays = (item: RegistrationSummaryIF): string => {
      if (localState.isChild) return ''
      if (isExpired(item) || isDischarged(item)) return '&nbsp;-'

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

    watch(() => props.setItem, (val) => {
    }, { deep: true, immediate: true })

    return {
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      showExpireDays,
      deleteDraft,
      editDraft,
      handleAction,
      registrationNumber,
      displayRegistrationNumber,
      registeringParty,
      securedParties,
      status,
      isActive,
      isDischarged,
      isDraft,
      isExpired,
      downloadPDF,
      inSelectedHeaders,
      TableActions,
      toggleExpand,
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
</style>
