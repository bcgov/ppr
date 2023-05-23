<template>
  <v-row no-gutters>
    <v-col v-if="isStaff" class="staff-header" cols="1"></v-col>
    <v-col :cols="isStaff? '11' : '12'" :class="isStaff? 'pl-4' : ''">
      <div class="ma-0 pa-0">
        <v-row no-gutters class="justify-space-between align-baseline">
          <span class="tombstone-header">
            <b>{{ header }}</b>
          </span>
        </v-row>
        <v-row id="tombstone-user-info" class="tombstone-sub-header" no-gutters>
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
            <v-row no-gutters justify="end">
              <v-tooltip top content-class="top-tooltip pa-5" nudge-left="30" transition="fade-transition">
                <template  v-slot:activator="{ on, attrs }">
                  <a :href="'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/'
                           +'permits-licences/news-updates/modernization-updates/modernization-resources#userguideacct'"
                    class="text-decoration-none"
                    target="_blank"
                    rel="noopener noreferrer">
                    <div v-bind="attrs" v-on="on">
                      <v-row no-gutters class="align-center">
                        <v-icon left color="primary">mdi-help-circle-outline</v-icon>
                        <span class="primary--text">Help</span>
                        <v-icon right color="primary" small>mdi-open-in-new</v-icon>
                      </v-row>
                    </div>
                  </a>
                </template>
                Learn how to use the BC Registries applications through step-by-step
                downloadable user guides and online help videos,
                or contact us to recieve help by email or phone.
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

export default defineComponent({
  name: 'TombstoneDefault',
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
    } = useStore()
    const localState = reactive({
      userName: computed((): string => {
        return `${getUserFirstName} ${getUserLastName}`
      }),
      date: '',
      header: computed((): string => {
        return tombstoneTitles[getRoleProductCode(getUserRoles, getUserProductSubscriptionsCodes)]
      }),
      isStaff: computed((): boolean => {
        return isRoleStaff
      }),
      isStaffBcol: computed((): boolean => {
        return isRoleStaffBcol
      }),
      isStaffSbc: computed((): boolean => {
        return isRoleStaffSbc
      }),
      accountName: computed((): string => {
        if (localState.isStaffBcol) return 'BC Online Help'
        if (localState.isStaffSbc) return 'SBC Staff'
        if (localState.isStaff) return 'BC Registries Staff'
        return getAccountLabel
      })
    })
    onMounted(() => {
      const newDate = new Date()
      localState.date = pacificDate(newDate)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
@media print {
  .staff-header {
    background-image: none;
    width: 0px;
    display: none;
  }
}
</style>
