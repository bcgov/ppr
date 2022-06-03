<template>
  <v-container fluid class="px-0">
    <registration-other-dialog
      attach="#app"
      :options="registrationOtherDialog"
      :display="showDialog"
      @proceed="dialogSubmit($event)"
    />
    <v-autocomplete
      class="registrationTypeAhead rounded-top"
      :class="{ 'reg-filter': isClearable }"
      allow-overflow
      filled
      :filter="filterList"
      full-width
      hide-details
      :items="displayItems"
      item-text="text"
      :label="dropdownLabel"
      :menu-props="{ maxHeight: '388px', bottom: true, offsetY: true }"
      offset="1000"
      return-object
      v-model="selected"
      :dense="isDense"
      :clearable="isClearable"
      @keypress="showAllGroups()"
    >
      <template v-slot:item="{ parent, item }">
        <template v-if="item.class === 'registration-list-header'">
          <v-list-item-content style="padding: 9px 0;">
            <v-row
              :id="`reg-type-drop-${item.group}`"
              style="width: 45rem; pointer-events: all;"
              @click="toggleGroup(item.group)"
            >
              <v-col class="py-0" align-self="center" cols="11">
                <span class="registration-list-header">{{ item.text }}</span>
              </v-col>
              <v-col class="py-0" align-self="center" cols="auto">
                <v-btn icon small style="pointer-events: all;">
                  <v-icon v-if="displayGroup[item.group]" class="expand-icon" color="primary">mdi-chevron-up</v-icon>
                  <v-icon v-else class="expand-icon" color="primary">mdi-chevron-down</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </v-list-item-content>
        </template>
        <template v-else class="registration-list">
          <v-list-item-content class="py-3">
            <span class="registration-list-item" v-html="`${parent.genFilteredText(item.text)}`"></span>
          </v-list-item-content>
        </template>
      </template>
    </v-autocomplete>
  </v-container>
</template>
<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'

import { RegistrationOtherDialog } from '@/components/dialogs'
import { APIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { MhrRegistrationType, RegistrationTypes } from '@/resources'
import { registrationOtherDialog } from '@/resources/dialogOptions'
import { useGetters } from 'vuex-composition-helpers'
import { getFeatureFlag } from '@/utils'

export default defineComponent({
  components: {
    RegistrationOtherDialog
  },
  props: {
    defaultLabel: String,
    defaultDense: Boolean,
    defaultClearable: { default: false },
    defaultClear: { default: false }
  },
  name: 'RegistrationBarTypeAheadList',
  emits: ['selected'],
  setup (props, { emit }) {
    const {
      isRoleStaff
    } = useGetters<any>([
      'isRoleStaff'
    ])

    const localState = reactive({
      displayGroup: {
        1: true,
        2: true,
        3: true
      },
      displayItems: [...RegistrationTypes],
      origItems: [...RegistrationTypes],
      selected: null,
      showDialog: false,
      dropdownLabel: props.defaultLabel,
      isDense: props.defaultDense,
      isClearable: props.defaultClearable,
      includeMhrSelection: computed((): boolean => {
        return isRoleStaff.value && getFeatureFlag('mhr-ui-enabled')
      })
    })
    const dialogSubmit = (proceed: boolean) => {
      if (proceed) emit('selected', localState.selected)
      else {
        localState.selected = null
      }
      localState.showDialog = false
    }
    const filterList = (item: RegistrationTypeIF, queryText: string, itemText: string) => {
      return itemText.toLocaleLowerCase().indexOf(queryText.toLocaleLowerCase()) > -1 || item.disabled
    }
    const showAllGroups = () => {
      for (let i = 0; i < Object.keys(localState.displayGroup).length; i++) {
        // if display for the group is set to false then toggle it
        if (!localState.displayGroup[i]) toggleGroup(i)
      }
    }
    const toggleGroup = (group: number) => {
      localState.displayGroup[group] = !localState.displayGroup[group]
      let newDisplayItems = [] as Array<RegistrationTypeIF>
      if (!localState.displayGroup[group]) {
        // remove elements from display
        for (let i = 0; i < localState.displayItems.length; i++) {
          const isHeader = localState.displayItems[i].disabled || false
          // if item is not part of the group or is a header add to new list
          if (localState.displayItems[i].group !== group || isHeader) {
            newDisplayItems.push({ ...localState.displayItems[i] })
          }
        }
      } else {
        // add items to their proper spot in the display list
        newDisplayItems = [...localState.displayItems]
        // get the index of the group header
        let headerIdx = 0
        for (let i = 0; i < newDisplayItems.length; i++) {
          if (newDisplayItems[i].group === group) {
            headerIdx = i
            break
          }
        }
        // insert the items of that group after their header in the display list
        let offset = 1
        for (let i = 0; i < localState.origItems.length; i++) {
          const isHeader = localState.origItems[i].disabled || false
          if (localState.origItems[i].group === group && !isHeader) {
            newDisplayItems.splice(headerIdx + offset, 0, { ...localState.origItems[i] })
            offset++
          }
        }
      }
      localState.displayItems = [...newDisplayItems]
    }
    const selectRegistration = (val: RegistrationTypeIF) => {
      if (val?.registrationTypeAPI === APIRegistrationTypes.OTHER) {
        localState.showDialog = true
      } else {
        emit('selected', val)
      }
    }

    onMounted(() => {
      // start with group 2 + 3 closed
      toggleGroup(2)
      toggleGroup(3)
    })

    watch(() => localState.selected, (val: RegistrationTypeIF) => {
      if (localState.isClearable) emit('selected', val)
      else if (val) selectRegistration(val)
    })

    watch(() => props.defaultClear, (val: boolean) => {
      if (val) {
        localState.selected = null
      }
    })

    watch(() => localState.includeMhrSelection, (val: boolean) => {
      if (val) {
        localState.origItems.push(MhrRegistrationType)
      }
    }, { deep: true, immediate: true })

    return {
      dialogSubmit,
      filterList,
      registrationOtherDialog,
      selectRegistration,
      showAllGroups,
      toggleGroup,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
::v-deep .v-text-field--filled .v-input__control .v-input__slot {
  max-height: 45px;
  min-height: 45px;
}

#registrationTypeAhead ::v-deep .v-select__slot, ::v-deep .v-input__slot {
  max-height: 45px;
  label {
    color: $gray7 !important;
    font-size: 14px;
    margin-top: -4px;
    padding-left: 6px;
  }
}

::v-deep .v-text-field--full-width .v-input__append-inner, .v-text-field--enclosed .v-input__append-inner {
  margin-top: 11px !important;
}

::v-deep .theme--light.v-list-item:not(.v-list-item--active):not(.v-list-item--disabled) {
  color: $gray7 !important;
  min-height: 0;
}

::v-deep .theme--light.v-list-item--disabled {
  min-height: 0;
}

.v-input__icon--clear {
  .v-icon {
    font-size: 18px;
  }
}
</style>
