<template>
  <v-container fluid :class="$style['breadcrumb-row']" class="view-container px-15 py-0">
    <div class="container pa-0">
      <v-row no-gutters class="container" style="padding: 6px 0;">
        <v-col cols="auto">
          <v-row no-gutters>
            <v-col cols="auto">
              <v-btn id="breadcrumb-back-btn" :class="$style['back-btn']" exact :href="buildHref(backUrl)" icon small>
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
            <v-breadcrumbs-item
              slot="item"
              slot-scope="{ item }"
              exact :href="buildHref(item.href)"
              data-test-id='breadcrumb-item'
            >
              <span v-if="!item.disabled" :class="[$style['underlined'], $style['breadcrumb-text']]">
                {{ handleStaff(item.text) }}
              </span>
              <span v-else :class="$style['breadcrumb-text']">{{ handleStaff(item.text) }}</span>
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
import { computed, defineComponent, reactive, toRefs, Ref } from '@vue/composition-api' // eslint-disable-line
import { useGetters } from 'vuex-composition-helpers'
// local
import { BreadcrumbIF } from '@/interfaces' // eslint-disable-line
import {
  tombstoneBreadcrumbDashboard,
  tombstoneBreadcrumbDischarge,
  tombstoneBreadcrumbRenewal,
  tombstoneBreadcrumbAmendment,
  tombstoneBreadcrumbRegistration,
  tombstoneBreadcrumbSearch,
  tombstoneBreadcrumbSearchConfirm,
  breadcrumbsTitles
} from '@/resources'
import { RouteNames } from '@/enums'
import { getDescriptiveUserRole } from '@/utils'

export default defineComponent({
  name: 'Breadcrumb',
  props: {
    setCurrentPath: String,
    setCurrentPathName: String
  },
  setup (props) {
    const {
      getRegistrationNumber,
      getRegistrationType,
      isRoleStaff,
      getUserRoles
    } = useGetters<any>(['getRegistrationNumber', 'getRegistrationType', 'isRoleStaff', 'getUserRoles'])
    const currentPath = toRefs(props).setCurrentPath
    const routeName = toRefs(props).setCurrentPathName as Ref<RouteNames>
    const localState = reactive({
      isStaff: computed((): boolean => {
        return isRoleStaff.value
      }),
      backUrl: computed((): string => {
        const length = localState.breadcrumbs?.length || 0
        if (length > 1) {
          return localState.breadcrumbs[length - 2].href || sessionStorage.getItem('REGISTRY_URL')
        }
      }),
      breadcrumbs: computed((): Array<BreadcrumbIF> => {
        const roleBasedBreadcrumbTitle = breadcrumbsTitles[getDescriptiveUserRole(getUserRoles.value)]
        if ((routeName.value === RouteNames.DASHBOARD) || (routeName.value === RouteNames.SIGN_IN)) {
          tombstoneBreadcrumbDashboard[1].text = roleBasedBreadcrumbTitle || tombstoneBreadcrumbDashboard[1].text
          return tombstoneBreadcrumbDashboard
        } else if ((routeName.value === RouteNames.SEARCH) || (routeName.value === RouteNames.MHRSEARCH)) {
          tombstoneBreadcrumbSearch[1].text = roleBasedBreadcrumbTitle
          return tombstoneBreadcrumbSearch
        } else if (routeName.value === RouteNames.MHRSEARCH_CONFIRM) {
          tombstoneBreadcrumbSearchConfirm[1].text = roleBasedBreadcrumbTitle ||
            tombstoneBreadcrumbSearchConfirm[1].text
          return tombstoneBreadcrumbSearchConfirm
        } else if (currentPath.value?.includes('discharge')) {
          const dischargeBreadcrumb = [...tombstoneBreadcrumbDischarge]
          dischargeBreadcrumb[1].text = roleBasedBreadcrumbTitle
          dischargeBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Total Discharge` || dischargeBreadcrumb[2].text
          return dischargeBreadcrumb
        } else if (currentPath.value?.includes('renew')) {
          const renewBreadcrumb = [...tombstoneBreadcrumbRenewal]
          renewBreadcrumb[1].text = roleBasedBreadcrumbTitle || renewBreadcrumb[1].text
          renewBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Renewal` || renewBreadcrumb[2].text
          return renewBreadcrumb
        } else if (currentPath.value?.includes('amend')) {
          const amendBreadcrumb = [...tombstoneBreadcrumbAmendment]
          amendBreadcrumb[1].text = roleBasedBreadcrumbTitle || amendBreadcrumb[1].text
          amendBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Amendment` || amendBreadcrumb[2].text
          return amendBreadcrumb
        } else {
          const registrationBreadcrumb = [...tombstoneBreadcrumbRegistration]
          registrationBreadcrumb[1].text = roleBasedBreadcrumbTitle || registrationBreadcrumb[1].text
          registrationBreadcrumb[2].text =
            getRegistrationType.value?.registrationTypeUI || registrationBreadcrumb[2].text
          return registrationBreadcrumb
        }
      })
    })

    const handleStaff = (breadcrumbText): string => {
      if (localState.isStaff) {
        breadcrumbText = breadcrumbText.replace('My', 'Staff')
      }
      return breadcrumbText
    }

    const buildHref = (href: string): string => {
      return `${href}${getParams()}`
    }

    /** Returns URL param string with Account ID if present, else empty string. */
    const getParams = (): string => {
      const accountId = sessionStorage.getItem('ACCOUNT_ID')
      return accountId ? `?accountid=${accountId}` : ''
    }

    return {
      handleStaff,
      buildHref,
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
