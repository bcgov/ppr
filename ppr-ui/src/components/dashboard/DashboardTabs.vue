<template>
  <v-tabs
    id="dashboard-tabs"
    active-class="active-tab"
    style="border-radius: 4px 4px 0 0"
    height="64"
    hide-slider centered grow
    v-model="tabNumber"
  >
    <v-tab
      tabindex="0"
      class="tab upper-border"
      :ripple="false"
      :class="{ 'mt-1': tabNumber === 1 }"
    >
      <v-icon class="mr-2" :class="{'whiteIcon': tabNumber === 1}">mdi-car</v-icon>
      <b>Personal Property Registrations</b><span class="pl-1">({{ registrationsCount }})</span>
    </v-tab>
    <v-tab
      tabindex="1"
      class="tab upper-border"
      :ripple="false"
      :class="{ 'mt-1': tabNumber === 0 }"
    >
      <v-icon class="mr-2" :class="{'whiteIcon': tabNumber === 0}">mdi-home</v-icon>
      <b>Manufactured Home Registrations</b><span class="pl-1">(10)</span>
    </v-tab>
    <v-tabs-items class="rounded-b" v-model="tabNumber" touchless>
      <v-tab-item class="px-7">
        <PprRegistrations
          isTabView
          :appReady="appReady"
          :appLoadingData="appLoadingData"
          @snackBarMsg="snackBarEvent($event)"
        />
      </v-tab-item>
      <v-tab-item class="px-7">
        <PprRegistrations
          isTabView
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
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { PprRegistrations } from '@/components/registration'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'DashboardTabs',
  components: {
    PprRegistrations
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    appLoadingData: {
      type: Boolean,
      default: false
    },
    registrationsCount: {
      type: Number,
      default: 0
    }
  },
  setup (props, context) {
    const localState = reactive({
      tabNumber: null
    })

    const snackBarEvent = (msg: string): void => {
      context.emit('snackBarMsg', msg)
    }

    return {
      snackBarEvent,
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
  font-size: 1rem;
  letter-spacing: 0;
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
