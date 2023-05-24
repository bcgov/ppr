<template>
  <v-tabs
    id="dashboard-tabs"
    active-class="active-tab"
    style="border-radius: 4px 4px 0 0"
    height="64"
    hide-slider centered grow
    v-model="tabNumber"
    @change="onTabChange"
  >
    <v-tab
      tabindex="0"
      class="tab upper-border"
      :ripple="false"
      :class="{ 'mt-1': isMhrTab }"
    >
      <v-icon class="mr-2" :class="{'whiteIcon': isMhrTab}">mdi-account-details</v-icon>
      <b>Personal Property Registrations </b><span class="pl-1">({{ getRegTableTotalRowCount }})</span>
    </v-tab>
    <v-tab
      tabindex="1"
      class="tab upper-border"
      :ripple="false"
      :class="{ 'mt-1': isPprTab }"
    >
      <v-icon class="mr-2" :class="{'whiteIcon': isPprTab}">mdi-home</v-icon>
      <b>Manufactured Home Registrations </b><span class="pl-1">({{ getMhRegTableBaseRegs.length }})</span>
    </v-tab>
    <v-tabs-items class="rounded-b" v-model="tabNumber" touchless>
      <v-tab-item class="px-7">
        <RegistrationsWrapper
          isTabView
          :isPpr="isPprTab"
          :appReady="appReady"
          :appLoadingData="appLoadingData"
          @snackBarMsg="snackBarEvent($event)"
        />
      </v-tab-item>
      <v-tab-item class="px-7">
        <RegistrationsWrapper
          isTabView
          :isMhr="isMhrTab"
          :appReady="appReady"
          :appLoadingData="appLoadingData"
          @snackBarMsg="snackBarEvent($event)"
        />
      </v-tab-item>
    </v-tabs-items>
  </v-tabs>
</template>

<script lang="ts">
// Components
/* eslint-disable no-unused-vars */
import { computed, defineComponent, onMounted, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { RegistrationsWrapper } from '@/components/common'
import { useNewMhrRegistration } from '@/composables'
/* eslint-enable no-unused-vars */

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
  setup (props, context) {
    const store = useStore()
    const {
      // Actions
      setCurrentRegistrationsTab
    } = useStore()
    const {
      // Getters
      getMhRegTableBaseRegs,
      getRegTableTotalRowCount,
      getCurrentRegistrationsTab
    } = storeToRefs(store)

    const {
      fetchMhRegistrations
    } = useNewMhrRegistration()

    const localState = reactive({
      tabNumber: getCurrentRegistrationsTab.value,
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
      await fetchMhRegistrations()
    })

    return {
      snackBarEvent,
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
#dashboard-tabs {
  background: transparent !important;
}
.tab {
  min-height: 64px !important;
  background-color: $BCgovBlue5;
  color: white !important;
  font-size: 1.125rem;
  letter-spacing: 0;
  text-transform: none !important;
  &:hover:not(.active-tab) {
    background-color: $primary-blue
  }
}

.whiteIcon {
  color: white !important;
}

.active-tab {
  color: $gray9 !important;
}

.upper-border {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  min-height: 58px;
  max-height: 58px;
  margin: 0 2.5px;
}

::v-deep {
  .v-tab.active-tab:hover, .v-tab--active {
    background-color: white !important;
    pointer-events: none;
  }

  .v-tabs-bar {
    background-color: transparent !important;
  }
}
</style>
