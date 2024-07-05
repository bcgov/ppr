<template>
  <div class="breadcrumb-row">
    <v-container class="view-container py-0">
      <v-row
        noGutters
        class="py-2"
      >
        <v-col cols="auto">
          <v-row noGutters>
            <v-col cols="auto">
              <v-btn
                id="breadcrumb-back-btn"
                class="back-btn"
                icon
                size="small"
                @click="navigate()"
              >
                <v-icon>mdi-arrow-left</v-icon>
              </v-btn>
            </v-col>
            <v-divider
              vertical
              class="border-opacity-75 pl-3"
              color="white"
            />
          </v-row>
        </v-col>

        <v-col
          cols="auto"
          class="pl-3 pt-1"
        >
          <v-breadcrumbs class="pa-0 breadcrumb-text">
            <v-breadcrumbs-item
              v-for="(item, index) in breadcrumbs"
              :key="item.text"
              class="fs-13 px-0"
              data-test-id="breadcrumb-item"
              :disabled="item.disabled"
              :href="item.href"
              :to="item.to"
            >
              <span>
                {{ handleStaff(item.text) }}
              </span>
              <v-icon
                v-if="index !== breadcrumbs.length-1"
                class="pl-3"
              >
                mdi-chevron-right
              </v-icon>
            </v-breadcrumbs-item>
          </v-breadcrumbs>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from 'vue' // eslint-disable-line
import { useRoute, useRouter } from 'vue-router'
import { useStore } from '@/store/store'
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
  breadcrumbsTitles,
  tombstoneBreadcrumbMhrInformation,
  tombstoneBreadcrumbMhrUnitNote,
  tombstoneBreadcrumbQsApplication,
  tombstoneBreadcrumbExemption,
  tombstoneBreadcrumbMhrCorrection,
  tombstoneBreadcrumbMhrReRegistration
} from '@/resources'
import { RouteNames } from '@/enums'
import { getRoleProductCode } from '@/utils'
import { storeToRefs } from 'pinia'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { useExemptions, useMhrCorrections } from '@/composables'

export default defineComponent({
  name: 'Breadcrumb',
  setup () {
    const route = useRoute()
    const router = useRouter()
    const { isMhrCorrection } = useMhrCorrections()
    const { exemptionLabel } = useExemptions()
    const {
      // Getters
      getRegistrationNumber,
      getRegistrationType,
      isRoleStaff,
      getUserRoles,
      getUserProductSubscriptionsCodes,
      getMhrInformation,
      getMhrUnitNoteType,
      isMhrReRegistration
    } = storeToRefs(useStore())

    const localState = reactive({
      backUrl: computed((): any => {
        const length = localState.breadcrumbs?.length || 0
        if (length > 1) {
          return localState.breadcrumbs[length - 1].to || localState.breadcrumbs[length - 2].href ||
            sessionStorage.getItem('REGISTRY_URL')
        }
        return ''
      }),
      breadcrumbs: computed((): Array<BreadcrumbIF> => {
        const { name, path } = route
        const roleBasedBreadcrumbTitle = breadcrumbsTitles[
          getRoleProductCode(getUserRoles.value, getUserProductSubscriptionsCodes.value)
        ]
        const allTombstoneBreadcrumbs = [
          tombstoneBreadcrumbDashboard,
          tombstoneBreadcrumbDischarge,
          tombstoneBreadcrumbRenewal,
          tombstoneBreadcrumbAmendment,
          tombstoneBreadcrumbRegistration,
          tombstoneBreadcrumbSearch,
          tombstoneBreadcrumbSearchConfirm,
          tombstoneBreadcrumbMhrInformation,
          tombstoneBreadcrumbMhrCorrection,
          tombstoneBreadcrumbMhrReRegistration,
          tombstoneBreadcrumbMhrUnitNote
        ]
        if (isRoleStaff.value) {
          for (const tombstoneBreadcrumb of allTombstoneBreadcrumbs) {
            tombstoneBreadcrumb[0].text = 'Staff Dashboard'
          }
        }
        if ((name === RouteNames.DASHBOARD) || (name === RouteNames.SIGN_IN)) {
          tombstoneBreadcrumbDashboard[1].text = roleBasedBreadcrumbTitle || tombstoneBreadcrumbDashboard[1].text
          return tombstoneBreadcrumbDashboard
        } else if ((name === RouteNames.SEARCH) || (name === RouteNames.MHRSEARCH)) {
          tombstoneBreadcrumbSearch[1].text = roleBasedBreadcrumbTitle
          return tombstoneBreadcrumbSearch
        } else if (name === RouteNames.MHRSEARCH_CONFIRM) {
          tombstoneBreadcrumbSearchConfirm[1].text = roleBasedBreadcrumbTitle ||
            tombstoneBreadcrumbSearchConfirm[1].text
          return tombstoneBreadcrumbSearchConfirm
        } else if (path?.includes('user-access')) {
          tombstoneBreadcrumbQsApplication[1].text = roleBasedBreadcrumbTitle ||
            tombstoneBreadcrumbQsApplication[1].text
          return tombstoneBreadcrumbQsApplication
        } else if (path?.includes('discharge')) {
          const dischargeBreadcrumb = [...tombstoneBreadcrumbDischarge]
          dischargeBreadcrumb[1].text = roleBasedBreadcrumbTitle
          dischargeBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Total Discharge` || dischargeBreadcrumb[2].text
          return dischargeBreadcrumb
        } else if (path?.includes('renew')) {
          const renewBreadcrumb = [...tombstoneBreadcrumbRenewal]
          renewBreadcrumb[1].text = roleBasedBreadcrumbTitle || renewBreadcrumb[1].text
          renewBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Renewal` || renewBreadcrumb[2].text
          return renewBreadcrumb
        } else if (path?.includes('amend')) {
          const amendBreadcrumb = [...tombstoneBreadcrumbAmendment]
          amendBreadcrumb[1].text = roleBasedBreadcrumbTitle || amendBreadcrumb[1].text
          amendBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Amendment` || amendBreadcrumb[2].text
          return amendBreadcrumb
        } else if ([RouteNames.MHR_INFORMATION, RouteNames.MHR_HISTORY].includes(name as RouteNames)) {
          const mhrInfoBreadcrumb = [...tombstoneBreadcrumbMhrInformation]
          mhrInfoBreadcrumb[2].text = `MHR Number ${getMhrInformation.value.mhrNumber}`
          return mhrInfoBreadcrumb
        } else if (isMhrCorrection.value) {
          const mhrCorrectionBreadcrumb = [...tombstoneBreadcrumbMhrCorrection]
          mhrCorrectionBreadcrumb[2].text = `MHR Number ${getMhrInformation.value.mhrNumber}`
          mhrCorrectionBreadcrumb[3].text = getRegistrationType.value?.text
          return mhrCorrectionBreadcrumb
        } else if (isMhrReRegistration.value) {
          const mhrReRegistrationBreadcrumb = [...tombstoneBreadcrumbMhrReRegistration]
          mhrReRegistrationBreadcrumb[2].text = `MHR Number ${getMhrInformation.value.mhrNumber}`
          return mhrReRegistrationBreadcrumb
        } else if (name === RouteNames.MHR_INFORMATION_NOTE) {
          const mhrUnitNoteBreadcrumb = [...tombstoneBreadcrumbMhrUnitNote]
          mhrUnitNoteBreadcrumb[2].text = `MHR Number ${getMhrInformation.value.mhrNumber}`
          mhrUnitNoteBreadcrumb[3].text = UnitNotesInfo[getMhrUnitNoteType.value].header
          return mhrUnitNoteBreadcrumb
        } else if (path?.includes('exemption')) {
          const exemptionBreadcrumb = [...tombstoneBreadcrumbExemption]
          exemptionBreadcrumb[2].text = `MHR Number ${getMhrInformation.value.mhrNumber}`
          exemptionBreadcrumb[3].text = exemptionLabel.value
          return exemptionBreadcrumb
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
      return isRoleStaff.value ? breadcrumbText.replace('My', 'Staff') : breadcrumbText
    }

    const buildHref = (href: string): string => {
      return `${href}${getParams()}`
    }

    const navigate = (): void => {
      const breadcrumb = localState.breadcrumbs[localState.breadcrumbs.length - 2] as BreadcrumbIF

      if (breadcrumb.to?.name) {
        router.push(breadcrumb.to?.name).catch(error => error)
      } else if (breadcrumb.href) {
        window.location.assign(buildHref(breadcrumb.href))
      }
    }

    /** Returns URL param string with Account ID if present, else empty string. */
    const getParams = (): string => {
      const accountId = sessionStorage.getItem('ACCOUNT_ID')
      return accountId ? `?accountid=${accountId}` : ''
    }

    return {
      handleStaff,
      navigate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.back-btn {
  background-color: white;
  color: $primary-blue !important;
  height: 32px !important;
  width: 32px !important;
}
.breadcrumb-row {
  background-color: $BCgovBlue3-5;
  :deep(.v-breadcrumbs-item--link), :deep(.v-breadcrumbs-item) {
    color: white;
  }
}
:deep(.v-breadcrumbs-item) {
  text-decoration: underline;
}
:deep(.v-breadcrumbs-item--disabled) {
  text-decoration: none!important;
  opacity: unset;
}
</style>
