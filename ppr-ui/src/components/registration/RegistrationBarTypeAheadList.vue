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
      :class="{ 'reg-filter': isClearable, 'light-background': isLightBackGround }"
      allow-overflow
      :filled="!isLightBackGround"
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
          <v-list-item-content>
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
        <template v-else>
          <v-list-item-content class="py-3 registration-list">
            <span class="registration-list-item" v-html="`${parent.genFilteredText(item.text)}`"></span>
          </v-list-item-content>
        </template>
      </template>
    </v-autocomplete>
  </v-container>
</template>
<script lang="ts">
import { defineComponent, onMounted, reactive, toRefs, watch } from 'vue'

import { RegistrationOtherDialog } from '@/components/dialogs'
import { APIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { RegistrationTypes } from '@/resources'
import { registrationOtherDialog } from '@/resources/dialogOptions'

export default defineComponent({
  components: {
    RegistrationOtherDialog
  },
  props: {
    defaultLabel: String,
    defaultDense: Boolean,
    defaultClearable: {
      type: Boolean,
      default: false
    },
    defaultClear: {
      type: Boolean,
      default: false
    },
    isLightBackGround: {
      type: Boolean,
      default: false
    }
  },
  name: 'RegistrationBarTypeAheadList',
  emits: ['selected'],
  setup (props, { emit }) {
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
      isClearable: props.defaultClearable
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
.light-background {
  padding: 0;
  background: white;
}

::v-deep .v-text-field .v-input__control .v-input__slot {
  min-height: 45px;
  max-height: 45px;
  padding-left: 10px;
  padding-right: 10px;
  .v-input__append-inner {
    margin-top: 10px;
  }
}

::v-deep .v-text-field--filled .v-input__control .v-input__slot {
  .v-input__append-inner {
    margin-top: 10px !important;
  }
}

::v-deep .v-select__slot, ::v-deep .v-input__slot {
  label {
    color: $gray7 !important;
    font-size: 14px;
    margin-top: -2px;
    padding-left: 6px;
  }
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
