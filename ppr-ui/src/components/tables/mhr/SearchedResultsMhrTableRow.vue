<template>
    <td>
      <v-checkbox
        :model-value="item.selected"
        :ripple="false"
        hide-details
        class="align-start"
        @click="onSelectionCheckboxClick(item)"
      />
    </td>
    <template
      v-for="header in headers"
      :key="header.value"
    >
      <td v-if="header.value === 'ownerName'">
        {{ getOwnerName(item) }}
      </td>
      <td v-else-if="header.value === 'ownerStatus'">
        {{ getOwnerStatusText(item) }}
      </td>
      <td v-else-if="header.value === 'mhrNumber'">
        {{ item.mhrNumber }}
      </td>
      <td v-else-if="header.value === 'status'">
        {{ item.status }}
      </td>
      <td v-else-if="header.value === 'manufacturerName'">
        {{ item.manufacturerName }}
      </td>
      <td v-else-if="header.value === 'baseInformation.year'">
        {{ item.baseInformation.year || '-' }}
      </td>
      <td v-else-if="header.value === 'baseInformation.make'">
        {{ item.baseInformation.make || '-' }} / {{ item.baseInformation.model || '-' }}
      </td>
      <td v-else-if="header.value === 'homeLocation'">
        {{ item.homeLocation }}
      </td>
      <td v-else-if="header.value === 'serialNumber'">
        {{ item.activeCount > 1 ? `${item.serialNumber} (${item.activeCount})` : `${item.serialNumber}` }}
      </td>
      <td
        v-else-if="header.value === 'edit'" 
        class="lien-col">
        <v-tooltip
          location="top"
          content-class="top-tooltip"
          transition="fade-transition"
        >
          <template #activator="{ props }">
            <span v-bind="props">
              <v-checkbox
                :model-value="item.includeLienInfo"
                class="align-start"
                :label="`Include lien information`"
                :disabled="!item.selected"
                :ripple="false"
                hide-details
                @click="setIncludeLienInfo(item)"
              />
            </span>
          </template>
          <div class="pt-2 pb-2">
            Select this to include a Personal Property Registry (PPR) lien search for the manufactured
            home for an additional fee.
            You must have the manufactured home selected before you can include the home's lien search.
          </div>
        </v-tooltip>
      </td>
    </template>
  </template>
  
  <script lang="ts">
  import { defineComponent, reactive, toRefs } from 'vue'

  import type { BaseHeaderIF, ManufacturedHomeSearchResultIF } from '@/interfaces'
  
  export default defineComponent({
    name: 'SearchedResultsMhrTableRow',
    props: {
      headers: {
        type: Array as () => Array<BaseHeaderIF>,
        default: () => []
      },
      item: {
        type: Object as () => ManufacturedHomeSearchResultIF,
        default: () => {}
      },
    },
    emits: [
      'onSelectionCheckboxClick',
      'setIncludeLienInfo'
    ],
    setup (props, {emit}) {
      const getOwnerStatus = (ownerStatus: string): string => {
      if (ownerStatus === 'PREVIOUS') {
        if (ownerStatus === 'PREVIOUS') return 'HISTORICAL'
        else return ownerStatus
      } else return ''
    }
      const getOwnerName = (item: ManufacturedHomeSearchResultIF): string => {
      if (item?.ownerName) {
        return `
          ${item.ownerName?.last},
          ${item.ownerName?.first}
          ${item.ownerName?.middle || item.ownerName?.second || ''}`
      } else if (item?.organizationName) {
        return item.organizationName
      } else return '-'
    }

    // return adaptive text for owner status count(s)
    const getOwnerStatusText = (item: ManufacturedHomeSearchResultIF): string => {
      let returnText = ''
      if (item.activeCount > 0) {
        returnText += 'ACTIVE'
        if (item.activeCount > 1) returnText += ` (${item.activeCount})`
        hasMultipleStatus(item) ? returnText += ',\n' : returnText += '\n'
      }
      if (item.exemptCount > 0) {
        returnText += 'EXEMPT'
        if (item.exemptCount > 1) returnText += ` (${item.exemptCount})`
        hasMultipleStatus(item) ? returnText += ',\n' : returnText += '\n'
      }
      if (item.historicalCount > 0) {
        returnText += 'HISTORICAL'
        if (item.historicalCount > 1) returnText += ` (${item.historicalCount})`
      }
      return returnText
    }

    const hasMultipleStatus = (item: ManufacturedHomeSearchResultIF): boolean => {
      return (item.activeCount > 0 && item.exemptCount > 0) ||
        (item.activeCount > 0 && item.historicalCount > 0) ||
        (item.exemptCount > 0 && item.historicalCount > 0)
    }

    const onSelectionCheckboxClick = (item: ManufacturedHomeSearchResultIF) => {
      emit('onSelectionCheckboxClick', item)
    }

    const setIncludeLienInfo = (item: ManufacturedHomeSearchResultIF) => {
      emit('setIncludeLienInfo', item)
    }
  
      return {
        getOwnerName,
        getOwnerStatus,
        getOwnerStatusText,
        hasMultipleStatus,
        onSelectionCheckboxClick,
        setIncludeLienInfo,
      }
    }
  })
  </script>
  
  <style lang="scss" scoped>
  @import '@/assets/styles/theme.scss';
  .selected-row {
    td {
      background: $blueSelected;
    }
  }
  .lien-col {
    min-width: 12rem;
  }
  </style>
  