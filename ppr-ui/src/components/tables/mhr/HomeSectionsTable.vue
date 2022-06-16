<template>
  <v-card flat rounded>
    <v-data-table
      id="mh-home-sections-table"
      class="home-sections-table"
      disable-sort
      fixed
      fixed-header
      :headers="headers"
      hide-default-footer
      :items="homeSections"
      item-key="id"
      no-data-text="No sections added yet"
    >
      <template v-slot:[`item.edit`]>
        <v-btn text small color="primary" class="ml-n2">
          <v-icon small>mdi-pencil</v-icon>
          <span class="ml-1">Edit</span>
        </v-btn>
        <v-menu offset-y left nudge-bottom="4">
          <template v-slot:activator="{ on }">
            <v-btn
              text
              small
              v-on="on"
              color="primary"
              class="smaller-actions actions__more-actions__btn"
            >
              <v-icon>mdi-menu-down</v-icon>
            </v-btn>
          </template>
          <v-list class="actions__more-actions">
            <v-list-item class="my-n2">
              <v-list-item-subtitle class="pa-0">
                <v-icon small>mdi-delete</v-icon>
                <span class="ml-1">Remove</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { BaseHeaderIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { homeSectionsTableHeaders } from '@/resources/tableHeaders'

export default defineComponent({
  name: 'HomeSectionsTable',
  components: {},
  props: {
    isReviewMode: { default: false }
  },
  setup (props, context) {
    // const {} = useGetters<any>([])
    // const {} = useActions<any>([])
    // const router = context.root.$router

    const localState = reactive({
      headers: computed((): Array<BaseHeaderIF> => {
        return homeSectionsTableHeaders
      }),
      homeSections: computed((): Array<any> => {
        return [
          {
            section: 1,
            serialNumber: 212345,
            length: 22,
            width: 11
          }
        ]
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
th {
  font-size: 0.875rem !important;
  color: $gray9 !important;
}
td {
  font-size: 0.875rem !important;
  color: $gray7 !important;
}

::v-deep {
  .v-data-table > .v-data-table__wrapper > table > thead > tr > th {
    padding: 15px 28px;
  }
  .v-data-table > .v-data-table__wrapper > table > tbody > tr > td {
    padding: 0 28px;
  }
}
</style>
