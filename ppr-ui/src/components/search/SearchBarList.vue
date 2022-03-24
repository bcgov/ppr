<template>
  <v-select
          id="search-select"
          class="search-bar-type-select"
          :error-messages="categoryMessage ? categoryMessage : ''"
          filled
          :items="displayItems"
          item-disabled="selectDisabled"
          item-text="searchTypeUI"
          item-value="searchTypeAPI"
          :label="selectedSearchType ? '' : searchTypeLabel"
          return-object
          v-model="selectedSearchType"
        >
        <template v-slot:item="{ item }">
        <template v-if="item.class === 'search-list-header'">
          <v-list-item-content style="padding: 9px 0;">
            <v-row
              :id="`reg-type-drop-${item.group}`"
              style="width: 45rem; pointer-events: all;"
              @click="toggleGroup(item.group)"
            >
              <v-col class="py-0" align-self="center" cols="11">
                <span class="search-list-header">{{ item.textLabel }}</span>
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
        <template v-else class="search-list">
          <v-list-item
            id="btn-security"
            class="copy-normal"
            @click="selectSearchType(item)"
          >
            <v-list-item-title>
              {{ item.searchTypeUI }}
            </v-list-item-title>
          </v-list-item>
        </template>
      </template>
  </v-select>
</template>
<script lang="ts">
import { defineComponent, reactive, toRefs, computed } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { MHRSearchTypes, SearchTypes } from '@/resources'
import { UISearchTypes, APISearchTypes } from '@/enums'
import { SearchTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { getFeatureFlag } from '@/utils'

export default defineComponent({
  name: 'SearchBarList',
  emits: ['selected'],
  props: {
    defaultSelectedSearchType: {
      type: Object as () => SearchTypeIF
    }
  },
  setup (props, { emit }) {
    const {
      isRoleStaffReg
    } = useGetters<any>([
      'isRoleStaffReg'
    ])
    const localState = reactive({
      searchTypes: UISearchTypes,
      searchTypeValues: APISearchTypes,
      selectedSearchType: props.defaultSelectedSearchType,
      searchTypeLabel: 'Select a search category',
      displayItems: computed((): Array<SearchTypeIF> => {
        if (getFeatureFlag('bcregistry-ui-ppr-mhr-staff-only') || isRoleStaffReg.value) {
          if (isRoleStaffReg.value) {
            const allSearchTypes = []
            allSearchTypes.push.apply(allSearchTypes, SearchTypes)
            allSearchTypes.push.apply(allSearchTypes, MHRSearchTypes)
            return allSearchTypes
          }
        }
        return SearchTypes
      }),
      origItems: computed((): Array<SearchTypeIF> => {
        if (getFeatureFlag('bcregistry-ui-ppr-mhr-staff-only') || isRoleStaffReg.value) {
          if (isRoleStaffReg.value) {
            const allSearchTypes = []
            allSearchTypes.push.apply(allSearchTypes, SearchTypes)
            allSearchTypes.push.apply(allSearchTypes, MHRSearchTypes)
            return allSearchTypes
          }
        }
        return SearchTypes
      }),
      displayGroup: {
        1: true,
        2: true
      },
      showMenu: false
    })
    const toggleGroup = (group: number) => {
      localState.displayGroup[group] = !localState.displayGroup[group]
      let newDisplayItems = [] as Array<SearchTypeIF>
      if (!localState.displayGroup[group]) {
        // remove elements from display
        for (let i = 0; i < localState.displayItems.length; i++) {
          const isHeader = localState.displayItems[i].selectDisabled || false
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
          const isHeader = localState.origItems[i].selectDisabled || false
          if (localState.origItems[i].group === group && !isHeader) {
            newDisplayItems.splice(headerIdx + offset, 0, { ...localState.origItems[i] })
            offset++
          }
        }
      }
      localState.displayItems = [...newDisplayItems]
    }
    const selectSearchType = (val: SearchTypeIF) => {
      emit('selected', val)
    }

    return {
      selectSearchType,
      toggleGroup,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
div.v-menu__content.theme--light.menuable__content__active {
  left: auto !important;
}
.actions__more-actions__btn {
  width: 50px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  box-shadow: none;
  margin-left: 1px;
}
.actions__more-actions.more-actions {
  overflow: auto;
}
.search-bar-btn {
  min-width: 0 !important;
  width: 285px;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  background-color: $primary-blue;
  color: white;
  height: 2.85rem;
  font-weight: normal;
  box-shadow: none;
}
.search-list-item {
  color: $gray7 !important;
}
::v-deep .v-list-item__title, .v-list-item__action {
  color: $gray7 !important;
  font-size: 0.875rem !important;
  min-height: 0;
  padding: 11.5px 22px;
}
::v-deep .v-list-item__title:hover{
  background-color: $gray1;
  color: $primary-blue !important;
}
::v-deep .v-list-item {
  padding: 0;
}
</style>
