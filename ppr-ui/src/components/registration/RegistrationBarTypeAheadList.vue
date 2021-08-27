<template>
  <v-container fluid class="px-0">
    <registration-other-dialog
      attach="#app"
      :options="registrationOtherDialog"
      :display="showDialog"
      @proceed="dialogSubmit($event)"
    />
    <v-autocomplete
      id="registrationTypeAhead"
      class="registrationTypeAhead rounded-top"
      allow-overflow
      filled
      :filter="filterList"
      full-width
      hide-details
      :items="displayItems"
      item-text="text"
      label="Start a new Registration (Select a type)"
      :menu-props="{ maxHeight: '388px' }"
      offset="1000"
      return-object
      v-model="selected"
      @keypress="showAllGroups()"
    >
      <template v-slot:item="{ parent, item }">
        <template v-if="item.class === 'registration-list-header'">
          <v-list-item-content style="padding: 9px 0;">
            <v-row style="width: 45rem;">
              <v-col class="py-0" align-self="center" cols="11">
                <span class="registration-list-header">{{ item.text }}</span>
              </v-col>
              <v-col class="py-0" align-self="center" cols="auto">
                <v-btn icon small @click="toggleGroup(item.group)" style="pointer-events: all;">
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
import { defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'

import { RegistrationOtherDialog } from '@/components/dialogs'
import { APIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { registrationOtherDialog, RegistrationTypes } from '@/resources'

export default defineComponent({
  components: {
    RegistrationOtherDialog
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
      showDialog: false
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
      if (val) selectRegistration(val)
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
::v-deep .theme--light.v-list-item:not(.v-list-item--active):not(.v-list-item--disabled) {
  color: $gray7 !important;
  min-height: 0;
}

::v-deep .theme--light.v-list-item--disabled {
  min-height: 0;
}
</style>
