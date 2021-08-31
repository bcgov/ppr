<template>
  <v-container fluid :class="$style['breadcrumb-row']" class="view-container px-15 py-0">
    <div class="container pa-0">
      <v-row no-gutters class="container" style="padding: 6px 0;">
        <v-col cols="auto">
          <v-row no-gutters>
            <v-col cols="auto">
              <v-btn id="breadcrumb-back-btn" :class="$style['back-btn']" exact :href="backUrl" icon small>
                <v-icon>mdi-arrow-left</v-icon>
              </v-btn>
            </v-col>
            <v-col class="pl-3" cols="auto" style="padding-top: 2px;">
              <div style="border-right: thin solid #ced4da; height: 28px;" />
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="auto" class="pl-3" style="padding-top: 6px;">
          <v-breadcrumbs class="pa-0" :items="breadcrumbs">
            <v-breadcrumbs-item slot="item" slot-scope="{ item }" exact :href="item.href">
              <span v-if="!item.disabled" :class="[$style['underlined'], $style['breadcrumb-text']]">
                {{ item.text }}
              </span>
              <span v-else :class="$style['breadcrumb-text']">{{ item.text }}</span>
            </v-breadcrumbs-item>
            <v-breadcrumbs-divider class="px-1" slot="divider">
              <v-icon color="white">mdi-chevron-right</v-icon>
            </v-breadcrumbs-divider>
          </v-breadcrumbs>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs, watch, Ref } from '@vue/composition-api' // eslint-disable-line
import { useGetters } from 'vuex-composition-helpers'
// local
import { BreadcrumbIF } from '@/interfaces' // eslint-disable-line
import {
  tombstoneBreadcrumbDashboard,
  tombstoneBreadcrumbDischarge,
  tombstoneBreadcrumbRegistration,
  tombstoneBreadcrumbSearch
} from '@/resources'
import { RouteNames } from '@/enums'

export default defineComponent({
  name: 'Breadcrumb',
  props: {
    setCurrentPath: String,
    setCurrentPathName: String
  },
  setup (props) {
    const {
      getRegistrationNumber,
      getRegistrationType
    } = useGetters<any>(['getRegistrationNumber', 'getRegistrationType'])
    const currentPath = toRefs(props).setCurrentPath
    const routeName = toRefs(props).setCurrentPathName as Ref<RouteNames>
    const localState = reactive({
      backUrl: computed((): string => {
        const length = localState.breadcrumbs?.length || 0
        if (length > 0) {
          return localState.breadcrumbs[length - 1].href || sessionStorage.getItem('BASE_URL')
        }
      }),
      breadcrumbs: computed((): Array<BreadcrumbIF> => {
        if ((routeName.value === RouteNames.DASHBOARD) || (routeName.value === RouteNames.SIGN_IN)) {
          return tombstoneBreadcrumbDashboard
        } else if (routeName.value === RouteNames.SEARCH) {
          return tombstoneBreadcrumbSearch
        } else if (currentPath.value?.includes('discharge')) {
          const dischargeBreadcrumb = [...tombstoneBreadcrumbDischarge]
          dischargeBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Total Discharge` || dischargeBreadcrumb[2].text
          return dischargeBreadcrumb
        } else {
          const registrationBreadcrumb = [...tombstoneBreadcrumbRegistration]
          registrationBreadcrumb[2].text =
            getRegistrationType.value?.registrationTypeUI || registrationBreadcrumb[2].text
          return registrationBreadcrumb
        }
      })
    })
    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.back-btn {
  background-color: white;
  color: $primary-blue !important;
  min-height: 32px !important;
  min-width: 32px !important;
}
.breadcrumb-row {
  background-color: $BCgovBlue3-5;
  color: white;
}
.breadcrumb-text {
  color: white !important;
  font-size: 0.8125rem !important;
}
.underlined {
  color: white !important;
  text-decoration: underline;
}
</style>
