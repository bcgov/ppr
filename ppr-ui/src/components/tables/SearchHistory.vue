<template>
  <v-container :class="[$style['main-results-div'], 'pa-0', 'white']">
    <v-row v-if="historyLength !== 0" no-gutters class="pt-4">
      <v-col cols="12">
        <v-data-table v-if="searchHistory"
                      id="search-history-table"
                      hide-default-footer
                      fixed
                      fixed-header
                      :headers="headers"
                      height="20rem"
                      :items="searchHistory"
                      item-key="searchId"
                      sort-by="searchDateTime"
                      sort-desc
                      return-object>
          <template v-slot:[`item.searchQuery.criteria.value`]="{ item }">
            {{ displaySearchValue(item.searchQuery) }}
          </template>
          <template v-slot:[`item.UISearchType`]="{ item }">
            {{ displayType(item.searchQuery.type) }}
          </template>
          <template v-slot:[`item.searchDateTime`]="{ item }">
            {{ displayDate(item.searchDateTime) }}
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row v-else no-gutters id="no-history-info" justify="center" :class="[$style['no-results-info'], 'pt-3']">
      <v-col cols="auto">
        Your search history will display here
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs, useCssModule } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { SearchCriteriaIF, SearchResponseIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { searchHistroyTableHeaders, SearchTypes } from '@/resources'
import { convertDate } from '@/utils'

export default defineComponent({
  setup () {
    const style = useCssModule()
    const { getSearchHistory } = useGetters<any>(['getSearchHistory'])
    const localState = reactive({
      headers: searchHistroyTableHeaders,
      historyLength: computed((): number => {
        return localState.searchHistory?.length || 0
      }),
      searchHistory: computed((): Array<SearchResponseIF> => {
        let searchHistory = null
        searchHistory = getSearchHistory.value
        return searchHistory
      })
    })
    const displayDate = (searchDate: string): string => {
      const date = new Date(searchDate)
      return convertDate(date, false)
    }
    const displaySearchValue = (query: SearchCriteriaIF): string => {
      const first = query?.criteria?.debtorName?.first
      const second = query?.criteria?.debtorName?.second
      const last = query?.criteria?.debtorName?.last
      const business = query?.criteria?.debtorName?.business
      if (first && last) {
        if (second) {
          return `${first} ${second} ${last}`
        }
        return `${first} ${last}`
      }
      return business || query?.criteria?.value || ''
    }
    const displayType = (APISearchType: string): string => {
      let UISearchType = ''
      for (let i = 0; i < SearchTypes.length; i++) {
        if (APISearchType === SearchTypes[i].searchTypeAPI) {
          UISearchType = SearchTypes[i].searchTypeUI
          break
        }
      }
      return UISearchType
    }
    return {
      ...toRefs(localState),
      displayDate,
      displaySearchValue,
      displayType,
      style
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.main-results-div {
  width: 100%;
}
.no-history-info {
  color: $gray9 !important;
  font-size: 0.825rem;
}
</style>
