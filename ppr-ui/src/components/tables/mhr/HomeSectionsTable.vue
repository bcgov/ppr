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
      <template v-slot:item="row">
        <!-- Edit Form -->
        <tr v-if="isActiveIndex(homeSections.indexOf(row.item))">
          <td class="add-edit-form-cell" :colspan="headers.length">
            <v-expand-transition>
              <AddEditHomeSections
                :editHomeSection="row.item"
                :isNewHomeSection="false"
                @close="activeIndex = -1"
                @remove="remove(row.item)"
                @submit="edit($event)"
              />
            </v-expand-transition>
          </td>
        </tr>
        <!-- Table Rows -->
        <tr v-else :key="row.item.id">
          <td>{{ homeSections.indexOf(row.item) + 1 }}</td>
          <td>{{ row.item.serialNumber }}</td>
          <td>{{ row.item.lengthFeet }} feet {{ row.item.lengthInches ? row.item.lengthInches + ' inches' : '' }}</td>
          <td>{{ row.item.widthFeet }} feet {{ row.item.widthInches ? row.item.widthInches + ' inches' : '' }}</td>
          <td>
            <v-btn
              text small
              color="primary"
              class="ml-n2"
              :disabled="isAdding || isEditing"
              @click="activeIndex = homeSections.indexOf(row.item)"
            >
              <v-icon small>mdi-pencil</v-icon>
              <span class="ml-1">Edit</span>
            </v-btn>

            <!-- Actions drop down menu -->
            <v-menu offset-y left nudge-bottom="4">
              <template v-slot:activator="{ on }">
                <v-btn
                  text
                  small
                  v-on="on"
                  color="primary"
                  class="smaller-actions actions__more-actions__btn"
                  :disabled="isAdding || isEditing"
                >
                  <v-icon>mdi-menu-down</v-icon>
                </v-btn>
              </template>

              <!-- More actions drop down list -->
              <v-list class="actions-dropdown actions__more-actions">
                <v-list-item class="my-n2">
                  <v-list-item-subtitle class="pa-0" @click="remove(row.item)">
                    <v-icon small>mdi-delete</v-icon>
                    <span class="ml-1">Remove</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-menu>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { BaseHeaderIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { homeSectionsTableHeaders } from '@/resources/tableHeaders'
import AddEditHomeSections from '@/components/mhrRegistration/YourHome/AddEditHomeSections.vue'
export default defineComponent({
  name: 'HomeSectionsTable',
  components: { AddEditHomeSections },
  props: {
    isAdding: { default: false },
    isReviewMode: { default: false },
    homeSections: { default: [] }
  },
  setup (props, context) {
    const localState = reactive({
      activeIndex: -1,
      isEditingHomeSection: false,
      headers: computed((): Array<BaseHeaderIF> => {
        return homeSectionsTableHeaders
      }),
      isEditing: computed((): boolean => {
        return localState.activeIndex >= 0
      })
    })

    const edit = (item): void => { context.emit('edit', { ...item, id: localState.activeIndex }) }
    const remove = (item): void => {
      localState.activeIndex = -1
      context.emit('remove', item)
    }
    const isActiveIndex = (index: number): boolean => { return index === localState.activeIndex }

    watch(() => localState.isEditing, () => { context.emit('isEditing', localState.isEditing) })

    return {
      edit,
      remove,
      isActiveIndex,
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
.actions-dropdown {
  cursor: pointer;
}
::v-deep {
  .v-data-table > .v-data-table__wrapper > table > thead > tr > th {
    padding: 15px 28px;
  }
  .v-data-table > .v-data-table__wrapper > table > tbody > tr > td {
    padding: 0 28px;
  }
  .add-edit-form-cell {
    padding: 0 !important;
  }
}
</style>
