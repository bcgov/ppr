<template>
  <v-container class="main-results-div pa-0 white">
    <v-row>
      <v-col id="search-meta-info" cols="8" class="pl-8 pt-8 ma-0">
          <span class="search-sub-title">{{ searchType }} - <b>"{{ searchValue }}"</b></span>
          <span class="search-info"> as of {{ searchTime }}</span>
      </v-col>
      <v-col cols="4" class="pt-8 ma-0" style="padding-left:100px;">
        <folio-number
          :defaultFolioNumber="folioNumber"
          @folio-number="folioNumber = $event"
          @folio-error="folioError = $event"
        />
      </v-col>
    </v-row>
    <v-row v-if="searched" class="result-info pl-5 mt-n8 pb-6" align="center" no-gutters>
      <v-col style="padding-right: 30px;" cols="auto">
        <v-row no-gutters>
          <v-col class="divider pr-3 mr-3" cols="auto">
            <b>{{ totalResultsLength }}</b> homes found
          </v-col>
          <v-col :class="totalResultsLength !== 0 ? 'pr-3 mr-3' : ''" cols="auto">
            <b>{{ activeMatchesLength }}</b> active homes
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row v-if="totalResultsLength !== 0" class="pt-3" no-gutters>
      <v-col cols="12">
        <v-data-table
          v-if="results"
          id="mh-search-results-table"
          class="results-table"
          disable-sort
          fixed
          fixed-header
          group-by="status"
          :headers="headers"
          hide-default-footer
          :items="results"
          item-key="id"
          :items-per-page="-1"
          mobile-breakpoint="0"
          @click:row="handleSelect($event)"
          return-object
        >

          <template v-slot:[`group.header`]="{ group }">
            <td
              class="group-header px-2"
              :colspan="headers.length"
            >
              <span v-if="group === 'ACTIVE'">
                ACTIVE ({{ activeMatchesLength }})
              </span>
              <span v-else-if="group === 'EXEMPT'">
                EXEMPT ({{ exemptMatchesLength }})
              </span>
              <span v-else-if="group === 'HISTORICAL'">
                HISTORICAL ({{ historicalMatchesLength }})
              </span>
            </td>
          </template>

          <template v-slot:[`item.ownerName`]="{ item }">
            {{ item.ownerName.last }},
            {{ item.ownerName.first }}
            {{ item.ownerName.middle }}

          </template>
          <template v-slot:[`item.registrationNumber`]="{ item }">
            {{ item.registrationNumber }}
          </template>
          <template v-slot:[`item.status`]="{ item }">
            {{ item.status }}
          </template>
          <template v-slot:[`item.year`]="{ item }">
            {{ item.year }}
          </template>
          <template v-slot:[`item.make`]="{ item }">
            {{ item.make }}
          </template>
          <template v-slot:[`item.model`]="{ item }">
            {{ item.model }}
          </template>
          <template v-slot:[`item.homeLocation`]="{ item }">
            {{ item.homeLocation }}
          </template>
          <template v-slot:[`item.serialNumber`]="{ item }">
            <span>{{ item.serialNumber }}</span>
          </template>
          <template v-slot:[`item.edit`]="{ item }">
            <span v-if="item.id === 1"><v-checkbox label="Include lien information"></v-checkbox></span>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row v-else id="search-no-results-info" class="no-results-info pb-10" justify="center" no-gutters>
      <v-col cols="8">
        <p class="no-results-title ma-0 pt-10"><b>Nil Result</b></p>
        <p class="ma-0 pt-2">
          No registered homes can be found to match the
          search criteria above.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, onMounted } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'

import { manufacturedHomeSearchTableHeaders } from '@/resources'
import { ManufacturedHomeSearchResultIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { FolioNumber } from '@/components/common'
import { pacificDate } from '@/utils'
import { RouteNames } from '@/enums'

export default defineComponent({
  components: {
    FolioNumber
  },
  setup (props, context) {
    const {
      getManufacturedHomeSearchResults,
      getFolioOrReferenceNumber,
      getSearchedType
    } = useGetters<any>(['getManufacturedHomeSearchResults', 'getFolioOrReferenceNumber', 'getSearchedType'])
    const { setSelectedManufacturedHome } = useActions<any>(['setSelectedManufacturedHome'])
    const router = context.root.$router

    const localState = reactive({
      searched: false,
      searchValue: '',
      searchTime: '',
      searchType: null,
      folioNumber: getFolioOrReferenceNumber.value,
      tooltipTxtSrchMtchs: 'One or more of the selected matches appear in ' +
        'the same registration. That registration will only be shown once in the report.',
      headers: manufacturedHomeSearchTableHeaders,
      results: [],
      totalResultsLength: 0,
      activeMatchesLength: computed((): number => {
        return localState.results.filter(item => item.status === 'ACTIVE').length
      }),
      exemptMatchesLength: computed((): number => {
        return localState.results.filter(item => item.status === 'EXEMPT').length
      }),
      historicalMatchesLength: computed((): number => {
        return localState.results.filter(item => item.status === 'HISTORICAL').length
      })
    })

    const handleSelect = (item: ManufacturedHomeSearchResultIF) => {
      setSelectedManufacturedHome(item)
      router.push({ name: RouteNames.MHRSEARCH_CONFIRM })
    }

    onMounted(() => {
      const resp = getManufacturedHomeSearchResults.value
      localState.searchValue = resp.searchQuery.criteria.value
      localState.searched = true
      localState.searchType = getSearchedType.value?.searchTypeUI || ''
      localState.results = resp.results
      localState.totalResultsLength = resp.totalResultsSize
      const date = new Date(resp.searchDateTime)
      localState.searchTime = pacificDate(date)
    })

    return {
      handleSelect,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
button {
  font-weight: normal !important;
}
td {
  font-size: 0.875rem !important;
  color: $gray7 !important;
}
th {
  font-size: 0.875rem !important;
  color: $gray9 !important;
}
.checkbox-info {
  font-size: 0.725rem !important;
  font-weight: bold;
  text-align: center;
}
.divider {
  border-right: 1px solid $gray3;
}
.group-header, .group-header:hover {
  background-color: $gray3;
  font-weight: bold;
}
.main-results-div {
  width: 100%;
}
.no-results-info {
  color: $gray7 !important;
  font-size: 1rem;
  text-align: center;
}
.no-results-title {
  font-size: 1.125rem;
}
.result-info {
  color: $gray7 !important;
  font-size: 1rem;
}
::v-deep .results-table .lien-info {
  width: 250px;
}
::v-deep .results-table .v-input--checkbox .v-input__slot .v-label {
  font-size: 0.875rem !important;
}

::v-deep .results-table .v-data-table__wrapper {
  max-height: 550px;
}
::v-deep .results-table .v-data-table__wrapper table tbody {
  tr {
    height: 54px;
  }

  tr:not(.v-data-table__selected)::before,
  tr:not(.v-data-table__selected)::after,
  tr:not(.v-data-table__selected):hover {
    // $gray1 at 75%
    background-color: #f1f3f5BF !important;
  }

  tr.v-data-table__selected::before,
  tr.v-data-table__selected::after,
  tr.v-data-table__selected:hover {
    background-color: #E4EDF7 !important;
  }
}
</style>
