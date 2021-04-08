<template>
  <v-container fluid class="px-0 py-0 pb-7 white" style="max-width: none;">
    <v-row no-gutters align="center" :class="[$style['breadcrumb-row'], 'px-15', 'py-2']">
      <v-col cols="auto" class="pr-3" style="border-right: thin solid #ced4da">
        <v-btn id="tombstone-back-btn" :class="$style['back-btn']" exact :href="backURL" icon small>
          <v-icon>mdi-arrow-left</v-icon>
        </v-btn>
      </v-col>
      <v-col cols="auto" class="pl-3">
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
    <v-row no-gutters id="tombstone-header" class="px-15 pt-7">
      <span :class="$style['tombstone-header']"><b>{{ header }}</b></span>
    </v-row>
    <v-row no-gutters id="tombstone-user-info" :class="[$style['tombstone-sub-header'], 'px-15', 'pt-3']">
      <v-col cols="10">
        <v-row no-gutters>
          <v-col cols="auto" class="pr-3" style="border-right: thin solid #dee2e6">
            {{ accountName }}
          </v-col>
          <v-col cols="auto" class="pl-3">
            {{ username }}
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
</template>
<script lang="ts">
// external
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { BreadcrumbIF } from '@/interfaces' // eslint-disable-line
import { convertDate } from '@/utils'

export default defineComponent({
  props: {
    backURL: {
      type: String,
      default: ''
    },
    header: {
      type: String,
      default: ''
    },
    setItems: Array as () => Array<BreadcrumbIF>
  },
  setup (props) {
    const { getUserFirstName, getUserLastName, getUserUsername } = useGetters<any>(
      ['getUserFirstName', 'getUserLastName', 'getUserUsername'])
    const localState = reactive({
      accountName: computed((): string => {
        return `${getUserFirstName.value} ${getUserLastName.value}`
      }),
      date: '',
      breadcrumbs: props.setItems,
      username: computed((): string => {
        return getUserUsername.value
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
