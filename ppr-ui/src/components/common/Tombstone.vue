<template>
  <div id="tombstone" class="white">
      <div :class="$style['breadcrumb-row']">
      <v-container fluid class="pt-2 pb-2">
        <v-row no-gutters>
          <v-col cols="auto" class="pr-3" style="border-right: thin solid #ced4da">
        <v-btn id="tombstone-back-btn" :class="$style['back-btn']" exact :href="backURL" icon small>
          <v-icon>mdi-arrow-left</v-icon>
        </v-btn>
          </v-col>
            <v-col cols="auto" class="pl-3 pt-1">
        <v-breadcrumbs class="pa-0" :items="breadcrumbs">
          <v-breadcrumbs-item slot="item" slot-scope="{ item }" exact :href="item.href">
            <span v-if="!item.disabled" :class="[$style['underlined'], $style['breadcrumb-text']]">
              {{ item.text }}
            </span>
            <span v-else :class="$style['breadcrumb-text']">{{ item.text }}</span>
          </v-breadcrumbs-item>
          <v-breadcrumbs-divider class="px-1" slot="divider">
            <v-icon color="white">mdi-chevron-right</v-icon>
          </v-breadcrumbs-divider>
        </v-breadcrumbs>
            </v-col>
        </v-row>
      </v-container>
      </div>

      <v-container id="tombstone-header" fluid class="pt-6 pb-0">
      <span :class="$style['tombstone-header']"><b>{{ header }}</b></span>
      </v-container>
      <v-container fluid id="tombstone-user-info" :class="[$style['tombstone-sub-header'], 'pt-4', 'pb-6']">
        <v-row no-gutters>
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
      </v-container>

  </div>
</template>
<script lang="ts">
// external
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { BreadcrumbIF } from '@/interfaces' // eslint-disable-line
import { convertDate } from '@/utils'
import { tombstoneBreadcrumbRegistration, tombstoneBreadcrumbDashboard } from '@/resources'

export default defineComponent({
  props: {
    backURL: {
      type: String,
      default: ''
    }
  },
  setup (props, { root }) {
    const { getAccountLabel, getUserFirstName, getUserLastName, getRegistrationType } =
      useGetters<any>(['getAccountLabel', 'getUserFirstName', 'getUserLastName',
        'getRegistrationType'])
    const localState = reactive({
      userName: computed((): string => {
        return `${getUserFirstName.value} ${getUserLastName.value}`
      }),
      date: '',
      breadcrumbs: computed((): Array<BreadcrumbIF> => {
        if ((root.$route.name === 'dashboard') || (root.$route.name === 'signin') ||
        (root.$route.name === 'search')) {
          return tombstoneBreadcrumbDashboard
        } else {
          const registrationBreadcrumb = tombstoneBreadcrumbRegistration
          registrationBreadcrumb[2].text = getRegistrationType.value?.registrationTypeUI || 'New Registration'
          return registrationBreadcrumb
        }
      }),
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
.back-btn {
  background-color: white;
  color: $primary-blue !important;
}
.breadcrumb-row {
  background-color: $BCgovBlue4;
  color: white;
}
.breadcrumb-text {
  color: white !important;
  font-size: 0.75rem !important;
}
.tombstone-header {
  color: $gray9;
  font-size: 1.25rem;
  font-weight: bold;
}
.tombstone-sub-header {
  color: $gray7;
  font-size: 0.95rem;
}
.underlined {
  color: white !important;
  text-decoration: underline;
}
</style>
