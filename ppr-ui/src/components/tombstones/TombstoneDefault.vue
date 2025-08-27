<template>
  <div>
    <div>
      <div class="flex items-start">
        <div :class="['flex-1']">
          <div class="m-0 p-0">
            <div class="flex justify-between items-baseline">
              <h1 class="tombstone-header">
                {{ header }}
              </h1>
              <div v-if="!isQsAccessEnabled" class="flex justify-end">
                <v-tooltip
                  location="top"
                  content-class="pa-5"
                  transition="fade-transition"
                >
                  <template #activator="{ props }">
                    <a
                      :href="'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/'
                      +'permits-licences/news-updates/modernization-updates/modernization-resources#userguideacct'"
                      class="text-decoration-none"
                      target="_blank"
                      rel="noopener noreferrer"
                      v-bind="props"
                    >
                      <div>
                        <v-row
                          no-gutters
                          class="align-center"
                        >
                          <v-icon
                            :start="true"
                            color="primary"
                          >mdi-help-circle-outline</v-icon>
                          <span class="text-primary">Help</span>
                          <v-icon
                            :end="true"
                            color="primary"
                            size="small"
                          >mdi-open-in-new</v-icon>
                        </v-row>
                      </div>
                    </a>
                  </template>
                  Learn how to use the BC Registries applications through step-by-step
                  downloadable user guides and online help videos,
                  or contact us to receive help by email or phone.
                </v-tooltip>
              </div>
            </div>

            <div id="tombstone-user-info" class="pt-1 tombstone-sub-header">
              <div class="flex">
                <div class="w-7/12">
                  <div class="flex">
                    <div class="pr-3" style="border-right: thin solid #dee2e6">
                      <p>{{ userName }}</p>
                    </div>
                    <div class="pl-3">
                      <p>{{ accountName }}</p>
                    </div>
                  </div>
                </div>

                <div v-if="isQsAccessEnabled" class="w-5/12 flex flex-col items-end">
                  <div class="mt-[-2rem] mb-2 w-full flex justify-end">
                    <QsAccessBtn />
                  </div>
                  <div class="flex justify-end">
                    <v-tooltip
                      location="top"
                      content-class="pa-5"
                      transition="fade-transition"
                    >
                      <template #activator="{ props }">
                        <a
                          :href="'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/'
                      +'permits-licences/news-updates/modernization-updates/modernization-resources#userguideacct'"
                          class="text-decoration-none"
                          target="_blank"
                          rel="noopener noreferrer"
                          v-bind="props"
                        >
                          <div>
                            <v-row
                              no-gutters
                              class="align-center"
                            >
                              <v-icon
                                :start="true"
                                color="primary"
                              >mdi-help-circle-outline</v-icon>
                              <span class="text-primary">Help</span>
                              <v-icon
                                :end="true"
                                color="primary"
                                size="small"
                              >mdi-open-in-new</v-icon>
                            </v-row>
                          </div>
                        </a>
                      </template>
                      Learn how to use the BC Registries applications through step-by-step
                      downloadable user guides and online help videos,
                      or contact us to receive help by email or phone.
                    </v-tooltip>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <UButton
      v-if="showPartyCodeBtn"
      class="pl-0 mt-4"
      variant="link"
      icon="mdi-file-document-edit-outline"
      @click="goToRoute(RouteNames.MANAGE_PARTY_CODES)"
    >
      View and Manage Party Codes
    </UButton>
  </div>
</template>
<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { useStore } from '@/store/store'
import { tombstoneTitles } from '@/resources'
import { pacificDate, getFeatureFlag, getRoleProductCode } from '@/utils'
import { storeToRefs } from 'pinia'
import { QsAccessBtn } from '@/components/common'
import { useUserAccess } from '@/composables/userAccess'
import { RouteNames } from '@/enums'

const {
  isRoleStaffReg,
  getAccountLabel,
  getUserFirstName,
  getUserLastName,
  isRoleStaff,
  isRoleStaffBcol,
  isRoleStaffSbc,
  getUserRoles,
  getUserProductSubscriptionsCodes
} = storeToRefs(useStore())
const { isRouteName, goToRoute } = useNavigation()
const route = useRoute()

const showPartyCodeBtn = computed((): boolean => {
  return Boolean(isRoleStaffReg?.value) && isRouteName(RouteNames.DASHBOARD) &&
    getFeatureFlag('enable-manage-party-codes')
})
const { isQsAccessEnabled } = useUserAccess()
const userName = computed((): string => {
  return `${getUserFirstName.value} ${getUserLastName.value}`
})
const date = ref('')
const header = computed((): string => {
  return tombstoneTitles[getRoleProductCode(getUserRoles.value, getUserProductSubscriptionsCodes.value)]
})
const accountName = computed((): string => {
  if (isRoleStaffBcol.value) return 'BC Online Help'
  if (isRoleStaffSbc.value) return 'SBC Staff'
  if (isRoleStaff.value) return 'BC Registries Staff'
  return getAccountLabel.value
})

onMounted(() => {
  date.value = pacificDate(new Date())
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
.staff-header-img {
  background-color: #fff;
  background-image: url('@/assets/img/AssetsRegistries_dashboard.jpg');
  background-position: center center;
  background-size: 100%;
  background-repeat: no-repeat;
  width: 150px;
}

@media print {
  .staff-header {
    background-image: none;
    width: 0px;
    display: none;
  }
}
</style>
