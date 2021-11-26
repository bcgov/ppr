<template>
  <v-row no-gutters>
    <v-col v-if="isStaff" class="staff-header" cols="1"></v-col>
    <v-col :cols="isStaff? '11' : '12'" :class="isStaff? 'pl-4' : ''">
      <div class="ma-0 pa-0">
        <span class="tombstone-header">
          <b>{{ header }}</b>
        </span>
        <v-row id="tombstone-user-info" class="tombstone-sub-header" no-gutters>
          <v-col cols="10">
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
          <v-col cols="2">
            <v-row no-gutters justify="end">
              {{ date }}
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
import { convertDate } from '@/utils'

export default defineComponent({
  name: 'TombstoneDefault',
  setup (props, { root }) {
    const {
      getAccountLabel,
      getUserFirstName,
      getUserLastName,
      isRoleStaff,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc
    } = useGetters<any>([
      'getAccountLabel',
      'getUserFirstName',
      'getUserLastName',
      'isRoleStaff',
      'isRoleStaffBcol',
      'isRoleStaffReg',
      'isRoleStaffSbc'
    ])
    const localState = reactive({
      userName: computed((): string => {
        if (!localState.isStaff) return `${getUserFirstName.value} ${getUserLastName.value}`
        if (localState.isStaffBcolReg) return 'BC Registries Staff'
        if (localState.isStaffSbc) return 'SBC Staff'
      }),
      date: '',
      header: computed((): string => {
        if (isRoleStaff.value) {
          return 'Staff Personal Property Registry'
        }
        return 'My Personal Property Registry'
      }),
      isStaff: computed((): boolean => {
        return isRoleStaff.value
      }),
      isStaffBcolReg: computed((): boolean => {
        return isRoleStaffBcol.value || isRoleStaffReg.value
      }),
      isStaffSbc: computed((): boolean => {
        return isRoleStaffSbc.value
      }),
      accountName: computed((): string => {
        return getAccountLabel.value
      })
    })
    onMounted(() => {
      const newDate = new Date()
      localState.date = convertDate(newDate, false, false)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
