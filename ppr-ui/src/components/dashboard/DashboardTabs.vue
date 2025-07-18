<template>
  <div
    id="dashboard-tabs"
  >
    <!-- Tabs -->
    <v-tabs
      :model-value="tabNumber"
      hide-slider
      grow
      class="ppr-mhr-tabs"
      @update:model-value="onTabChange"
    >
      <v-tab
        :value="0"
        class="tab"
        :ripple="false"
        tabindex="0"
        :class="{ 'mt-1': isMhrTab }"
      >
        <v-icon
          class="mr-2"
          :class="{'whiteIcon': isMhrTab}"
        >
          mdi-account-details
        </v-icon>
        <b>Personal Property Registrations </b><span class="pl-1">({{ getRegTableTotalRowCount }})</span>
      </v-tab>
      <v-tab
        :value="1"
        class="tab"
        :ripple="false"
        tabindex="0"
        :class="{ 'mt-1': isPprTab }"
      >
        <v-icon
          class="mr-2"
          :class="{'whiteIcon': isPprTab}"
        >
          mdi-home
        </v-icon>
        <b>Manufactured Home Registrations </b><span class="pl-1">({{ getMhRegTableBaseRegs.length }})</span>
      </v-tab>
    </v-tabs>
    <!-- Window Items -->
    <v-window
      :model-value="tabNumber"
      class="rounded-bottom bg-white px-6"
    >
      <v-window-item
        :value="0"
        continuous
      >
        <RegistrationsWrapper
          is-tab-view
          :is-ppr="isPprTab"
          :app-ready="appReady"
          :app-loading-data="appLoadingData"
          @snack-bar-msg="snackBarEvent($event)"
        />
      </v-window-item>
      <v-window-item
        :value="1"
      >
        <RegistrationsWrapper
          is-tab-view
          :is-mhr="isMhrTab"
          :app-ready="appReady"
          :app-loading-data="appLoadingData"
          @snack-bar-msg="snackBarEvent($event)"
        />
      </v-window-item>
    </v-window>
  </div>
</template>

<script lang="ts">
// Components
import { computed, defineComponent, onMounted, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { RegistrationsWrapper } from '@/components/common'
import { useNewMhrRegistration } from '@/composables'

export default defineComponent({
  name: 'DashboardTabs',
  components: {
    RegistrationsWrapper
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    appLoadingData: {
      type: Boolean,
      default: false
    }
  },
  emits: ['snackBarMsg'],
  setup (props, context) {
    const {
      // Actions
      setCurrentRegistrationsTab
    } = useStore()
    const {
      // Getters
      getRegTableMhSortOptions,
      getMhRegTableBaseRegs,
      getRegTableBaseRegs,
      getRegTableTotalRowCount,
      getCurrentRegistrationsTab
    } = storeToRefs(useStore())

    const {
      fetchMhRegistrations
    } = useNewMhrRegistration()

    const localState = reactive({
      tabNumber: computed((): number => {
        return getCurrentRegistrationsTab.value
      }),
      isPprTab: computed((): boolean => {
        return localState.tabNumber === 0
      }),
      isMhrTab: computed((): boolean => {
        return localState.tabNumber === 1
      })
    })

    const snackBarEvent = (msg: string): void => {
      context.emit('snackBarMsg', msg)
    }

    const onTabChange = (clickedTab): void => {
      setCurrentRegistrationsTab(clickedTab)
    }

    onMounted(async () => {
      await fetchMhRegistrations(getRegTableMhSortOptions.value)
    })

    return {
      snackBarEvent,
      getRegTableBaseRegs,
      getMhRegTableBaseRegs,
      getRegTableTotalRowCount,
      getCurrentRegistrationsTab,
      onTabChange,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.ppr-mhr-tabs {
  display: block;
  overflow: visible;
}

.tab {
  min-height: 64px !important;
  background-color: $BCgovBlue5;
  color: white;
  font-size: 1.125rem;
  letter-spacing: 0;
  text-transform: none !important;
  border-radius: 4px 4px 0 0!important;
  &:hover:not(.v-tab--selected) {
    background-color: $primary-blue
  }

  &:nth-child(1) {
    margin-right: 3px; // margin to make space for outline a11y
  }
  &:nth-child(2) {
    margin-left: 3px; // margin to make space for outline a11y
  }
}
.v-tab--selected {
  background-color: white;
  color: $gray9;
  pointer-events: none;
}
.v-window {
  min-height: 400px
}

.v-slide-group-item--active {
  height: unset !important;
}
</style>
