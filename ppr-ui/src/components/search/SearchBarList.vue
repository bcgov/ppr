<template>
  <v-select
          id="search-select"
          class="search-bar-type-select"
          ref="searchSelect"
          :error-messages="categoryMessage ? categoryMessage : ''"
          filled
          :items="displayItems"
          item-disabled="selectDisabled"
          item-text="searchTypeUI"
          item-value="searchTypeAPI"
          :label="selectedSearchType ? '' : searchTypeLabel"
          return-object
          v-model="selectedSearchType"
          @focus="updateSelections()"
        >
        <template v-slot:item="{ item }">
        <template v-if="item.class === 'search-list-header'">
          <v-list-item-content style="padding: 9px 0;">
            <v-row
              :id="`srch-type-drop-${item.group}`"
              style="width: 45rem; pointer-events: all;"
              @click="toggleGroup(item.group)"
            >
              <v-col class="py-0" align-self="center" cols="11">
                <span class="search-list-header"><v-icon class="menu-icon" :color="item.color">{{item.icon}}</v-icon>
                {{ item.textLabel }}</span>
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
            v-if="displayGroup[item.group]"
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
import { defineComponent, reactive, toRefs, computed, ref } from '@vue/composition-api'
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
    },
    defaultCategoryMessage: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    const {
      isRoleStaffReg,
      hasPprRole,
      hasMhrRole
    } = useGetters<any>([
      'isRoleStaffReg',
      'hasPprRole',
      'hasMhrRole'
    ])
    const searchSelect = ref(null)
    const localState = reactive({
      searchTypes: UISearchTypes,
      searchTypeValues: APISearchTypes,
      selectedSearchType: props.defaultSelectedSearchType,
      categoryMessage: computed((): string => {
        return props.defaultCategoryMessage
      }),
      searchTypeLabel: computed((): string => {
        if (localState.selectedSearchType?.searchTypeUI) {
          return localState.selectedSearchType.searchTypeUI
        }
        return 'Select a search category'
      }),
      origItems: computed((): Array<SearchTypeIF> => {
        const allSearchTypes = []
        if (isRoleStaffReg.value) {
          if (getFeatureFlag('mhr-ui-enabled')) {
            // allSearchTypes.push.apply(allSearchTypes, SearchTypes)
            allSearchTypes.push.apply(allSearchTypes, MHRSearchTypes)
            console.log(allSearchTypes)
            return allSearchTypes
          } else {
            allSearchTypes.push.apply(allSearchTypes, SearchTypes)
            allSearchTypes.shift()
            return allSearchTypes
          }
        }
        if (hasPprRole.value) {
          allSearchTypes.push.apply(allSearchTypes, SearchTypes)
          // we can pop the title off if there is only one search type
          if (!hasMhrRole.value) {
            allSearchTypes.shift()
          }
        }
        if (hasMhrRole.value) {
          allSearchTypes.push.apply(allSearchTypes, MHRSearchTypes)
          // we can pop the title off if there is only one search type
          if (!hasPprRole.value) {
            allSearchTypes.shift()
          }
        }
        return allSearchTypes
      }),
      displayItems: [],
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
      localState.selectedSearchType = val
      searchSelect.value.blur()
    }
    const updateSelections = () => {
      localState.displayItems = localState.origItems
    }

    return {
      updateSelections,
      searchSelect,
      selectSearchType,
      toggleGroup,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
.copy-normal {
  color: $gray7 !important;
  padding-left: 20px;
}
.search-list-header {
  color: $gray9 !important;
  font-weight:bold;
}
</style>
