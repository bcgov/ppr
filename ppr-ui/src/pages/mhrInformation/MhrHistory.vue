<template>
  <v-container
    v-if="dataLoaded"
    id="mhr-history"
    class="px-0 footer-view-container"
    fluid
  >
    <!-- Loading Overlay -->
    <v-overlay
      v-model="loading"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="30"
        indeterminate
      />
    </v-overlay>

    <!-- View Content -->
    <div class="container pa-0 pt-4">
      <v-row
        id="registration-header"
        no-gutters
        class="pt-3 pb-3 soft-corners-top"
      >
        <v-col>
          <h1>Historical Manufactured Home Information</h1>
          <p class="mt-7">
            This is the current information for this registration as of
            <span class="font-weight-bold">{{ pacificDate(new Date()) }}</span>.
          </p>
        </v-col>
      </v-row>

      <!-- Tabbed Mhr History Tables -->
      <TabbedContainer
        :tab-config="mhHistoryTabConfig"
        class="mt-4"
      >
        <template #tab-0>
          <SimpleTable
            :table-headers="homeDescriptionHeaders"
            :table-data="mhrHistory.descriptions"
          >
            <template #content-slot="{ content }">
              <MhrHistoryDescription :content="content" />
            </template>
          </SimpleTable>
        </template>
        <template #tab-1>
          <SimpleTable
            :table-headers="homeLocationHeaders"
            :table-data="mapLocationsApiToUi(mhrHistory.locations)"
          >
            <template #content-slot="{ content }">
              <MhrHistoryLocations
                :content="content"
                :registrations="mhrHistory.registrations"
              />
            </template>
          </SimpleTable>
        </template>
        <template #tab-2>
          <SimpleTable
            :table-headers="homeOwnerHeaders"
            :table-data="mapOwnersApiToUi(mhrHistory.owners)"
          >
            <template #cell-slot-1="{ content }: { content: OwnerIF }">
              <div class="icon-text">
                <v-icon
                  class="mt-n1"
                >
                  {{ getHomeOwnerIcon(content.partyType, !content?.individualName) }}
                </v-icon>
                <span class="pl-2">
                  <template v-if="content?.individualName">
                    {{ content.individualName.first }}
                    {{ content.individualName.middle }}
                    {{ content.individualName.last }}
                  </template>
                  <template v-else>
                    {{ content.organizationName }}
                  </template>
                  <template v-if="content.description">
                    <br>
                    <span class="fs-14 font-weight-regular gray7">{{ content.description }}</span>
                  </template>
                </span>
              </div>
            </template>
            <template #content-slot="{ content }">
              <MhrHistoryOwners :content="content" />
            </template>
          </SimpleTable>
        </template>
      </TabbedContainer>
    </div>

    <!-- Footer -->
    <v-footer class="bg-white pt-4 pb-11">
      <v-container>
        <v-row no-gutters>
          <v-col cols="12">
            <v-btn
              id="reg-back-btn"
              variant="outlined"
              color="primary"
              class="pr-5 float-right"
              @click="goToDash"
            >
              <v-icon
                color="primary"
                class="pt-1"
              >
                mdi-chevron-left
              </v-icon> Back
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-footer>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getMhrHistory } from '@/utils/mhr-api-helper'
import { pacificDate , getFeatureFlag } from '@/utils'
import { useAuth, useNavigation } from '@/composables'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { TabbedContainer, SimpleTable } from '@/components/common'
import {
  homeDescriptionHeaders,
  homeLocationHeaders,
  homeOwnerHeaders,
  mhHistoryTabConfig
} from '@/resources/mhr-history'
import { MhrHistoryDescription, MhrHistoryLocations, MhrHistoryOwners } from '@/components/mhrHistory'
import {
  ApiHomeTenancyTypes,
  HomeLocationTypes,
  HomeLocationUiTypes,
  HomeOwnerPartyTypes,
  HomeTenancyTypes
} from '@/enums'
import type { OwnerIF } from '@/interfaces'

/** Composables **/
const { isAuthenticated } = useAuth()
const { goToDash } = useNavigation()
const { getMhrInformation } = storeToRefs(useStore())

/** Props **/
const props = withDefaults(defineProps<{
  appReady?: boolean
}>(), {
  appReady: false
})

/** Local Properties **/
const dataLoaded = ref(true)
const loading = ref(false)
const mhrHistory = ref({})


onMounted(async (): Promise<void> => {
  // do not proceed if app is not ready
  // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
  if (!props.appReady || !isAuthenticated.value || !getFeatureFlag('mhr-history-enabled')) {
    await goToDash()
    return
  }

  // Fetch Manufactured Home History
  loading.value = true
  mhrHistory.value = await getMhrHistory(getMhrInformation.value?.mhrNumber)
  loading.value = false
})

const getHomeOwnerIcon = (partyType: HomeOwnerPartyTypes, isBusiness = false): string => {
  const uniqueRoleIcon = isBusiness
    ? 'custom:ExecutorBusinessIcon'
    : 'custom:ExecutorPersonIcon'
  const ownerIcon = isBusiness
    ? 'mdi-domain'
    : 'mdi-account'

  switch (partyType) {
    case HomeOwnerPartyTypes.EXECUTOR:
    case HomeOwnerPartyTypes.ADMINISTRATOR:
    case HomeOwnerPartyTypes.TRUSTEE:
      return uniqueRoleIcon
    case HomeOwnerPartyTypes.OWNER_IND:
    case HomeOwnerPartyTypes.OWNER_BUS:
      return ownerIcon
  }
}

/**
 * Maps an API home location type to a UI home location type.
 *
 * @param {HomeLocationTypes} apiType - The API home location type to map.
 * @returns {HomeLocationUiTypes} The corresponding UI home location type.
 */
function mapApiToUiLocationType(apiType: HomeLocationTypes): HomeLocationUiTypes {
  switch (apiType) {
    case HomeLocationTypes.LOT:
      return HomeLocationUiTypes.LOT
    case HomeLocationTypes.HOME_PARK:
      return HomeLocationUiTypes.HOME_PARK
    case HomeLocationTypes.OTHER_RESERVE:
      return HomeLocationUiTypes.OTHER_RESERVE
    case HomeLocationTypes.OTHER_STRATA:
      return HomeLocationUiTypes.OTHER_STRATA
    case HomeLocationTypes.OTHER_TYPE:
      return HomeLocationUiTypes.OTHER_TYPE
    default:
      return HomeLocationUiTypes.NOT_ENTERED
  }
}

/**
 * Maps the `locationType` and `otherType` properties in each location object to the UI location types.
 *
 * @param {Array<any>} locations - The array of location objects.
 * @returns {Array<any>} The new array with updated location types.
 */
function mapLocationsApiToUi(locations: Array<any>): Array<any> {
  return locations.map(location => ({
    ...location,
    locationType: mapApiToUiLocationType(location.locationType)
  }))
}

/**
 * Maps an API home tenancy type to a UI home tenancy type.
 *
 * @param {ApiHomeTenancyTypes} apiType - The API home tenancy type to map.
 * @returns {HomeTenancyTypes} The corresponding UI home tenancy type.
 */
function mapApiToUiTenancyType(apiType: ApiHomeTenancyTypes): HomeTenancyTypes {
  switch (apiType) {
    case ApiHomeTenancyTypes.JOINT:
      return HomeTenancyTypes.JOINT
    case ApiHomeTenancyTypes.SOLE:
      return HomeTenancyTypes.SOLE
    case ApiHomeTenancyTypes.COMMON:
      return HomeTenancyTypes.COMMON
    case ApiHomeTenancyTypes.NA:
      return HomeTenancyTypes.NA
    default:
      throw new Error(`Unknown API tenancy type: ${apiType}`)
  }
}

/**
 * Maps an API status to a UI status.
 *
 * @param {string} status - The API status to map.
 * @returns {string} The corresponding UI status.
 */
function mapApiToUiStatus(status: string): string {
  switch (status) {
    case 'ACTIVE':
      return 'Active'
    case 'PREVIOUS':
      return 'Historical'
    default:
      return status
  }
}

/**
 * Maps the `type` and `groupTenancyType` properties in each owner object to the UI tenancy types.
 *
 * @param {Array<any>} owners - The array of owner objects.
 * @returns {Array<any>} The new array with updated tenancy types.
 */
function mapOwnersApiToUi(owners: Array<any>): Array<any> {
  return owners.map(owner => ({
    ...owner,
    type: mapApiToUiTenancyType(owner.type),
    groupTenancyType: owner.groupTenancyType ? mapApiToUiTenancyType(owner.groupTenancyType) : undefined,
    status: mapApiToUiStatus(owner.status)
  }))
}

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
.person-executor-icon {
  margin-top: -3px !important;
  height: 22px !important;
  width: 22px !important;
}

.business-executor-icon {
  margin-top: -8px !important;
  margin-left: -4px !important;
  height: 29px !important;
  width: 28px !important;
}
.v-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 140px;
  background-color: #333;
}
</style>
