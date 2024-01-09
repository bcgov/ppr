<template>
  <div
    id="registration-bar-type-ahead-list"
    class="px-0"
  >
    <RegistrationOtherDialog
      attach="#app"
      :options="registrationOtherDialog"
      :display="showDialog"
      @proceed="dialogSubmit($event)"
    />
    <v-autocomplete
      v-model="selected"
      class="registrationTypeAhead rounded-top"
      hideDetails
      itemTitle="text"
      variant="filled"
      returnObject
      density="compact"
      color="primary"
      :class="{ 'reg-filter': isClearable, 'bg-white': isLightBackGround }"
      :items="displayItems"
      :label="dropdownLabel"
      :clearable="isClearable"
      :clearIcon="'mdi-close'"
      persistentClear
      @update:search="showAllGroups"
      @update:menu="hideAllGroups"
    >
      <template #item="{ props, item }">
        <template v-if="item.raw.class === 'registration-list-header'">
          <v-list-item
            :id="`reg-type-drop-${item.raw.group}`"
            class="registration-list-item"
            noGutters
          >
            <v-row
              :id="`reg-type-drop-${item.raw.group}`"
              style="pointer-events: all;"
              @click="toggleGroup(item.raw.group)"
            >
              <v-col cols="12">
                <span class="registration-list-header">{{ item.raw.text }}</span>
              </v-col>
            </v-row>
            <template #append>
              <v-btn
                variant="plain"
                size="small"
                @click="toggleGroup(item.raw.group)"
              >
                <v-icon
                  v-if="displayGroup[item.raw.group]"
                  class="expand-icon"
                  color="primary"
                >
                  mdi-chevron-up
                </v-icon>
                <v-icon
                  v-else
                  class="expand-icon"
                  color="primary"
                >
                  mdi-chevron-down
                </v-icon>
              </v-btn>
            </template>
          </v-list-item>
        </template>
        <template v-else-if="item.raw.class === 'registration-list-divider'">
          <v-divider class="mx-4" />
        </template>
        <template v-else-if="displayGroup[item.raw.group]">
          <v-list-item
            v-bind="props"
            class="py-3 registration-list registration-list-item"
            @click="selectRegistration(item.raw)"
          />
        </template>
      </template>
    </v-autocomplete>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { RegistrationOtherDialog } from '@/components/dialogs'
import { APIRegistrationTypes } from '@/enums'
import { RegistrationTypeIF } from '@/interfaces'
import { RegistrationTypes } from '@/resources'
import { registrationOtherDialog } from '@/resources/dialogOptions'

export default defineComponent({
  name: 'RegistrationBarTypeAheadList',
  components: {
    RegistrationOtherDialog
  },
  props: {
    defaultLabel: {
      type: String,
      default: ''
    },
    defaultDense: {
      type: Boolean,
      default: false
    },
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
  emits: ['selected'],
  setup (props, { emit }) {
    const localState = reactive({
      displayGroup: {
        1: false,
        2: false,
        3: false
      },
      selected: null,
      showDialog: false,
      dropdownLabel: props.defaultLabel as string,
      isDense: props.defaultDense,
      isClearable: props.defaultClearable,
      fieldVariant: computed((): string | any => {
        return !props.isLightBackGround ? 'filled' : 'plain'
      }),
      displayItems: computed(() => {
        return filterListByGroupStatus(RegistrationTypes, localState.displayGroup)
      })
    })
    const dialogSubmit = (proceed: boolean) => {
      if (proceed) emit('selected', localState.selected)
      else {
        localState.selected = null
      }
      localState.showDialog = false
    }
    const showAllGroups = () => {
      for (let i = 0; i < Object.keys(localState.displayGroup).length; i++) {
        // if display for the group is set to false then toggle it
        if (!localState.displayGroup[i]) toggleGroup(i)
      }
    }
    const hideAllGroups = () => {
      for (let i = 0; i < Object.keys(localState.displayGroup).length; i++) {
        // if display for the group is set to false then toggle it
        if (localState.displayGroup[i]) toggleGroup(i)
      }
    }
    const toggleGroup = (group: number) => {
      localState.displayGroup[group] = !localState.displayGroup[group]
    }
    const filterListByGroupStatus = (list, groupStatus) => {
      return list.filter(item =>
          item.class === 'registration-list-header' || item.class === 'registration-list-divider' ||
          groupStatus[item.group]
      )
    }
    const selectRegistration = (val: RegistrationTypeIF) => {
      if (val?.registrationTypeAPI === APIRegistrationTypes.OTHER) {
        localState.showDialog = true
      } else {
        emit('selected', val)
      }
    }

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
      RegistrationTypes,
      dialogSubmit,
      registrationOtherDialog,
      selectRegistration,
      showAllGroups,
      hideAllGroups,
      toggleGroup,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
.registrationTypeAhead {
  :deep(.v-label) {
    font-size: .875rem;
  }
}
.registration-list-header {
  color: $gray9;
  font-size: 0.875rem;
  font-weight: bold;
  text-align: center;
}
.registration-list-item {
  width: 730px!important;
}
</style>
