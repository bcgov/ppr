<template>
  <v-row no-gutters>
    <v-col v-if="isStaff" class="staff-header" cols="1"></v-col>
    <v-col :cols="isStaff? '11' : '12'" :class="isStaff? 'pl-4' : ''">
      <div class="ma-0 pa-0">
        <v-row no-gutters class="justify-space-between align-baseline">
          <span class="tombstone-header">
            <b>{{ header }}</b>
          </span>
          <v-tooltip top content-class="top-tooltip pa-5" nudge-left="30" transition="none">
            <template  v-slot:activator="{ on, attrs }">
              <a
              :href="'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/'
                +'permits-licences/news-updates/modernization-updates/modernization-resources#ppr'"
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
            Learn about the Personal Property Registry and how to use the application through step-by-step guides,
            online videos, and downloadable quick guides.
          </v-tooltip>
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
              <span class="font-weight-bold pr-2">Registry Time:</span>{{ date }}
            </v-row>
          </v-col>
        </v-row>
      </div>
    </v-col>
  </v-row>
</template>
<script lang="ts">
// external
import {
  computed,
  defineComponent,
  onMounted,
  reactive,
  toRefs
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { tombstoneTitles } from '@/resources'
// local
import { pacificDate, getDescriptiveUserRole } from '@/utils'

export default defineComponent({
  name: 'TombstoneDefault',
  setup (props, { root }) {
    const {
      getAccountLabel,
      getUserFirstName,
      getUserLastName,
      isRoleStaff,
      isRoleStaffBcol,
      isRoleStaffSbc,
      getUserRoles
    } = useGetters<any>([
      'getAccountLabel',
      'getUserFirstName',
      'getUserLastName',
      'isRoleStaff',
      'isRoleStaffBcol',
      'isRoleStaffSbc',
      'getUserRoles'
    ])
    const localState = reactive({
      userName: computed((): string => {
        return `${getUserFirstName.value} ${getUserLastName.value}`
      }),
      date: '',
      header: computed((): string => {
        return tombstoneTitles[getDescriptiveUserRole(getUserRoles.value)]
      }),
      isStaff: computed((): boolean => {
        return isRoleStaff.value
      }),
      isStaffBcol: computed((): boolean => {
        return isRoleStaffBcol.value
      }),
      isStaffSbc: computed((): boolean => {
        return isRoleStaffSbc.value
      }),
      accountName: computed((): string => {
        if (localState.isStaffBcol) return 'BC Online Help'
        if (localState.isStaffSbc) return 'SBC Staff'
        if (localState.isStaff) return 'BC Registries Staff'
        return getAccountLabel.value
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
