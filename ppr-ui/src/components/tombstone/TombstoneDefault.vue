<template>
  <v-row no-gutters>
    <v-col v-if="isStaff" class="staff-header" cols="1"></v-col>
    <v-col :cols="isStaff? '11' : '12'" :class="isStaff? 'pl-4' : ''">
      <div class="ma-0 pa-0">
        <span class="tombstone-header">
          <b>{{ header }}</b>
        </span>
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
// local
import { pacificDate } from '@/utils'

export default defineComponent({
  name: 'TombstoneDefault',
  setup (props, { root }) {
    const {
      getAccountLabel,
      getUserFirstName,
      getUserLastName,
      isRoleStaff,
      hasMhrRole,
      hasPprRole,
      isRoleStaffBcol,
      isRoleStaffSbc
    } = useGetters<any>([
      'getAccountLabel',
      'getUserFirstName',
      'getUserLastName',
      'isRoleStaff',
      'hasMhrRole',
      'hasPprRole',
      'isRoleStaffBcol',
      'isRoleStaffSbc'
    ])
    const localState = reactive({
      userName: computed((): string => {
        return `${getUserFirstName.value} ${getUserLastName.value}`
      }),
      date: '',
      header: computed((): string => {
        let header = 'My Personal Property Registry'
        if (localState.isStaffMHRandPPR) {
          header = 'Staff Manufactured Home and Personal Property Registry'
        } else if (localState.isStaffMHR) {
          header = 'Staff Manufactured Home Registry'
        } else if (localState.isStaffPPR || isRoleStaff.value) {
          header = 'Staff Personal Property Registry'
        } else if (localState.isClientMHRandPPR) {
          header = 'My Manufactured Home and Personal Property Registry'
        } else if (localState.isClientMHR) {
          header = 'My Manufactured Home Registry'
        } else if (localState.isClientPPR) {
          header = 'My Personal Property Registry'
        }
        return header
      }),
      isStaffMHR: computed((): boolean => {
        return isRoleStaff.value && hasMhrRole.value && !hasPprRole.value
      }),
      isStaffPPR: computed((): boolean => {
        return isRoleStaff.value && hasPprRole.value && !hasMhrRole.value
      }),
      isClientMHR: computed((): boolean => {
        return hasMhrRole.value && !hasPprRole.value && !isRoleStaff.value
      }),
      isClientPPR: computed((): boolean => {
        return hasPprRole.value && !hasMhrRole.value && !isRoleStaff.value
      }),
      isStaffMHRandPPR: computed((): boolean => {
        return isRoleStaff.value && hasPprRole.value && hasMhrRole.value
      }),
      isClientMHRandPPR: computed((): boolean => {
        return hasPprRole.value && hasMhrRole.value && !isRoleStaff.value
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
