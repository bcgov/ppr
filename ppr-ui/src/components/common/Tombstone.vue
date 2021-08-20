<template>
  <v-container class="view-container px-15 py-0" fluid style="background-color: white;">
    <div class="container pa-0 pt-6">
      <span :class="$style['tombstone-header']">
        <b>{{ header }}</b>
      </span>
      <v-row id="tombstone-user-info" :class="[$style['tombstone-sub-header'], 'px-0', 'pt-4', 'pb-6']" no-gutters>
        <v-col cols="10">
          <v-row no-gutters>
            <v-col cols="auto" class="pr-3" style="border-right: thin solid #dee2e6">
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
  </v-container>
</template>
<script lang="ts">
// external
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { convertDate } from '@/utils'

export default defineComponent({
  props: {
    backURL: {
      type: String,
      default: ''
    }
  },
  setup (props, { root }) {
    const { getAccountLabel, getUserFirstName, getUserLastName } =
      useGetters<any>(['getAccountLabel', 'getUserFirstName', 'getUserLastName'])
    const localState = reactive({
      userName: computed((): string => {
        return `${getUserFirstName.value} ${getUserLastName.value}`
      }),
      date: '',
      header: computed((): string => {
        if ((root.$route.name === 'dashboard') || (root.$route.name === 'signin') ||
        (root.$route.name === 'search')) {
          return 'My PPR Dashboard'
        } else {
          return 'My Personal Property Registry'
        }
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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.tombstone-header {
  color: $gray9;
  font-size: 1.25rem;
  font-weight: bold;
}
.tombstone-sub-header {
  color: $gray7;
  font-size: 0.95rem;
}
</style>
