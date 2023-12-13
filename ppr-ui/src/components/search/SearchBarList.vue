<template>
  <v-select
    id="search-select"
    ref="searchSelect"
    v-model="selectedSearchType"
    class="search-bar-type-select"
    :class="{ 'wide-menu' : !isSingleSearchOption }"
    :errorMessages="categoryMessage ? categoryMessage : ''"
    variant="filled"
    color="primary"
    :items="optionsList"
    itemTitle="searchTypeUI"
    itemValue="searchTypeAPI"
    :label="searchTypeLabel"
    returnObject
    :menuProps="isSingleSearchOption
      ? { bottom: true, offsetY: true }
      : { maxHeight: 400, offset: -55 }"
    @focus="updateSelections()"
  >
    <template #item="{ props, item }">
      <!-- Grouped List Items -->
      <template v-if="item.raw.class === 'search-list-header'">
        <v-list-item
          class="py-2"
          :class="{ 'top-border' : item.raw.icon === 'mdi-home' }"
        >
          <v-row
            :id="`search-type-drop-${item.raw.group}`"
            class="py-3 search-list-header-row"
            @click="toggleGroup(item.raw.group)"
          >
            <v-col
              class="py-0 pl-3"
              alignSelf="center"
            >
              <span class="search-list-header">
                <v-icon
                  class="mt-n2"
                  :color="item.color"
                >{{ item.raw.icon }}</v-icon>
                {{ item.raw.textLabel }}
              </span>
            </v-col>
            <v-col
              cols="auto"
              class="py-0"
              alignSelf="center"
            >
              <v-btn
                variant="text"
                size="18"
                color="primary"
                class="mt-n2"
                :appendIcon="displayGroup[item.raw.group] ? 'mdi-chevron-up' : 'mdi-chevron-down'"
              />
            </v-col>
          </v-row>
        </v-list-item>
      </template>

      <!-- Individual Options -->
      <v-list-item
        v-else
        :id="`list-${item.raw.searchTypeAPI.toLowerCase().replaceAll('_','-')}`"
        class="copy-normal search-list"
        :class="{ 'select-menu-padding' : !isSingleSearchOption }"
        v-bind="props"
        @click="selectSearchType({ ...item.raw })"
      />
    </template>
  </v-select>
</template>
<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { MHRSearchTypes, SearchTypes } from '@/resources'
import { APISearchTypes, UISearchTypes } from '@/enums'
import { SearchTypeIF } from '@/interfaces'
import { getFeatureFlag } from '@/utils'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'SearchBarList',
  props: {
    defaultSelectedSearchType: {
      type: Object as () => SearchTypeIF,
      default: () => {}
    },
    defaultCategoryMessage: {
      type: String,
      default: ''
    }
  },
  emits: ['selected'],
  setup (props, { emit }) {
    const {
      isRoleStaffReg,
      isRoleStaff,
      hasPprEnabled,
      hasMhrEnabled
    } = storeToRefs(useStore())
    const searchSelect = ref(null)
    const localState = reactive({
      searchTypes: UISearchTypes,
      searchTypeValues: APISearchTypes,
      selectedSearchType: props.defaultSelectedSearchType,
      optionsList: computed(() => {
        return (localState.displayItems.filter(item =>
          localState.displayGroup[item.group] || item.class === 'search-list-header'
        ))
      }),
      categoryMessage: computed((): string => {
        return props.defaultCategoryMessage
      }),
      searchTypeLabel: computed((): string => {
        if (!localState.selectedSearchType) {
          return 'Select a search category'
        }
        // display searchTypeUI label when both groups are collapsed
        if (Object.values(localState.displayGroup).every(group => group === false)) {
          return localState.selectedSearchType.searchTypeUI
        }
        // display searchTypeUI label even if other group is expanded
        if (!localState.displayGroup[localState.selectedSearchType.group]) {
          return localState.selectedSearchType.searchTypeUI
        }
        return ''
      }),
      origItems: computed((): Array<SearchTypeIF> => {
        const allSearchTypes = []

        // Staff Only Options
        if (isRoleStaff.value || isRoleStaffReg.value) {
          if (getFeatureFlag('mhr-ui-enabled')) {
            allSearchTypes.push(...SearchTypes, ...MHRSearchTypes)
            return allSearchTypes
          } else {
            allSearchTypes.push(...SearchTypes)
            return allSearchTypes.slice(1)
          }
        } else {
          // Client Only Blocks
          if (hasPprEnabled.value && hasMhrEnabled.value) {
            allSearchTypes.push(...SearchTypes, ...MHRSearchTypes)
            return allSearchTypes
          }

          if (hasPprEnabled.value) {
            allSearchTypes.push(...SearchTypes)
            return allSearchTypes.slice(1)
          }

          if (hasMhrEnabled.value) {
            allSearchTypes.push(...MHRSearchTypes)
            return allSearchTypes.slice(1)
          }
        }

        return allSearchTypes
      }),
      isSingleSearchOption: computed((): boolean => {
        return ((hasPprEnabled.value && !hasMhrEnabled.value) || (!hasPprEnabled.value && hasMhrEnabled.value)) &&
          !(isRoleStaff.value || isRoleStaffReg.value)
      }),
      displayItems: [],
      displayGroup: {
        1: !(isRoleStaff.value || isRoleStaffReg.value)
          ? (hasPprEnabled.value && !hasMhrEnabled.value)
          : !hasMhrEnabled.value,
        2: !(isRoleStaff.value || isRoleStaffReg.value) && (!hasPprEnabled.value && hasMhrEnabled.value)
      },
      showMenu: false
    })

    const toggleGroup = (group: number) => {
      const initial = localState.displayGroup[group]
      // collapse both groups as only one group can be expanded at once
      localState.displayGroup = {
        1: false,
        2: false
      }
      // expand desired group
      localState.displayGroup[group] = !initial
      localState.displayItems = [...localState.origItems]
    }
    const selectSearchType = (val: SearchTypeIF) => {
      emit('selected', val)
      localState.selectedSearchType = val
      searchSelect.value.blur()
    }
    const updateSelections = () => {
      localState.displayItems = localState.origItems
      if (hasPprEnabled.value && hasMhrEnabled.value) {
        localState.displayGroup = { 1: false, 2: false }
      }
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
.select-menu-padding {
  padding-left: 46px!important;
}
.search-list-header {
  color: $gray9;
  font-weight:bold;
  .v-icon {
    color: $app-blue!important;
  }
}
:deep(.search-list-header-row:hover) {
  cursor: pointer!important;
}
</style>
