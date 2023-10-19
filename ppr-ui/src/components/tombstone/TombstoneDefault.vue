<template>
  <v-row no-gutters>
    <v-col v-if="isRoleStaff" class="staff-header-img" cols="1"></v-col>
    <v-col :cols="isRoleStaff ? '11' : '12'" :class="isRoleStaff ? 'pl-4' : ''">
      <div class="ma-0 pa-0">
        <v-row no-gutters class="justify-space-between align-baseline">
          <span class="tombstone-header">
            <b>{{ header }}</b>
          </span>
        </v-row>
        <v-row id="tombstone-user-info" class="pt-1" no-gutters>
          <v-col cols="7">
            <v-row no-gutters>
              <v-col
                cols="auto"
                class="pr-3"
                style="border-right: thin solid #dee2e6"
              >
                {{ userName }}
              </v-col>
              <v-col cols="auto" class="pl-3">
                {{ accountName }}
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="5">
            <!-- Qualified Suppler Access Btn -->
            <v-row v-if="isQsAccessEnabled" no-gutters justify="end" class="mt-n8 mb-2">
              <QsAccessBtn />
            </v-row>
            <v-row no-gutters justify="end">
              <v-tooltip location="top" content-class="top-tooltip pa-5" transition="fade-transition">
                <template v-slot:activator="{ props }">
                  <a :href="'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/'
                           +'permits-licences/news-updates/modernization-updates/modernization-resources#userguideacct'"
                    class="text-decoration-none"
                    target="_blank"
                    rel="noopener noreferrer"
                    v-bind="props"
                  >
                    <div>
                      <v-row no-gutters class="align-center">
                        <v-icon :start="true" color="primary">mdi-help-circle-outline</v-icon>
                        <span class="text-primary">Help</span>
                        <v-icon :end="true" color="primary" size="small">mdi-open-in-new</v-icon>
                      </v-row>
                    </div>
                  </a>
                </template>
                Learn how to use the BC Registries applications through step-by-step
                downloadable user guides and online help videos,
                or contact us to receive help by email or phone.
              </v-tooltip>
            </v-row>
          </v-col>
        </v-row>
      </div>
    </v-col>
  </v-row>
</template>
<script lang="ts">
import {
  computed,
  defineComponent,
  onMounted,
  reactive,
  toRefs
} from 'vue'
import { useStore } from '@/store/store'
import { tombstoneTitles } from '@/resources'
import { pacificDate, getRoleProductCode } from '@/utils'
import { storeToRefs } from 'pinia'
import { QsAccessBtn } from '@/components/common'
import { useUserAccess } from '@/composables/userAccess'

export default defineComponent({
  name: 'TombstoneDefault',
  components: { QsAccessBtn },
  setup () {
    const {
      getAccountLabel,
      getUserFirstName,
      getUserLastName,
      isRoleStaff,
      isRoleStaffBcol,
      isRoleStaffSbc,
      getUserRoles,
      getUserProductSubscriptionsCodes
    } = storeToRefs(useStore())
    const { isQsAccessEnabled } = useUserAccess()

    const localState = reactive({
      userName: computed((): string => {
        return `${getUserFirstName.value} ${getUserLastName.value}`
      }),
      date: '',
      header: computed((): string => {
        return tombstoneTitles[getRoleProductCode(getUserRoles.value, getUserProductSubscriptionsCodes.value)]
      }),
      accountName: computed((): string => {
        if (isRoleStaffBcol.value) return 'BC Online Help'
        if (isRoleStaffSbc.value) return 'SBC Staff'
        if (isRoleStaff.value) return 'BC Registries Staff'
        return getAccountLabel.value
      })
    })
    onMounted(() => {
      const newDate = new Date()
      localState.date = pacificDate(newDate)
    })

    return {
      isRoleStaff,
      isQsAccessEnabled,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
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
