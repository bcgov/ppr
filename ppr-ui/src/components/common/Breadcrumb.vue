<template>
  <v-container fluid :class="$style['breadcrumb-row']" class="view-container px-15 py-0">
    <div class="container pa-0">
      <v-row no-gutters class="container px-0 py-2">
        <v-col cols="auto" class="pr-3" style="border-right: thin solid #ced4da">
          <v-btn id="breadcrumb-back-btn" :class="$style['back-btn']" exact :href="backURL" icon small>
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
    </div>
  </v-container>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { BreadcrumbIF } from '@/interfaces' // eslint-disable-line
import { tombstoneBreadcrumbRegistration, tombstoneBreadcrumbDashboard } from '@/resources'

export default defineComponent({
  name: 'Breadcrumb',
  props: {
    backURL: {
      type: String,
      default: ''
    }
  },
  setup (props, { root }) {
    const { getRegistrationType } = useGetters<any>(['getRegistrationType'])
    const localState = reactive({
      breadcrumbs: computed((): Array<BreadcrumbIF> => {
        if ((root.$route.name === 'dashboard') || (root.$route.name === 'signin') ||
        (root.$route.name === 'search')) {
          return tombstoneBreadcrumbDashboard
        } else {
          const registrationBreadcrumb = tombstoneBreadcrumbRegistration
          registrationBreadcrumb[2].text = getRegistrationType.value?.registrationTypeUI || 'New Registration'
          return registrationBreadcrumb
        }
      })
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
.underlined {
  color: white !important;
  text-decoration: underline;
}
</style>
