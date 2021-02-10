<template>
  <v-container fluid no-gutters>
    <v-row class="mt-4" no-gutters>
      <v-col cols="4">
        <v-select :items="searchOptions"
                  label="TBD"
                  filled
                  v-model="selected">
        </v-select>
      </v-col>
      <v-col cols="4">
        <v-text-field autocomplete="chrome-off"
                      filled
                      v-model="searchValue">
        </v-text-field>
      </v-col>
      <v-col cols="4">
        <v-btn>
          Search
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component({})
export default class Search extends Vue {
  // Local Properties
  private searchOptions: Array<string> = [
    'Serial Number',
    '...'
  ]

  private selected: string = null
  private searchValue: string = null
}
</script>

<style lang="scss" scoped>

</style>
