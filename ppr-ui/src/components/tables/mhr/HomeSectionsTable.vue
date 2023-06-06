<template>
  <v-card flat rounded class="mt-2">
    <v-simple-table
      id="mh-home-sections-table"
      class="home-sections-table"
      fixed-header
    >
      <template v-slot:default>
        <!-- Table Headers -->
        <thead>
          <tr>
            <th v-for="header in headers" :key="header.value" :class="header.class">
              {{ header.text }}
            </th>
          </tr>
        </thead>

        <!-- Table Body -->
        <tbody v-if="homeSections.length > 0">
          <tr v-for="(item, index) in homeSections" :key="`${item}: ${index}`">
            <!-- Edit Form -->
            <template v-if="isActiveIndex(homeSections.indexOf(item))">
              <td class="add-edit-form-cell" :colspan="headers.length">
                <AddEditHomeSections
                    :editHomeSection="item"
                    :isNewHomeSection="false"
                    @close="activeIndex = -1"
                    @remove="remove(item)"
                    @submit="edit($event)"
                />
              </td>
            </template>

            <!-- Table Rows -->
            <template v-else>
              <td :class="{ 'pl-0': isReviewMode }">{{ homeSections.indexOf(item) + 1 }}</td>
              <td>{{ item.serialNumber }}</td>
              <td>
                {{ item.lengthFeet }} <span class="pr-1">feet</span>
                {{ item.lengthInches ? item.lengthInches + ' inches' : '0 inches' }}
              </td>
              <td>
                {{ item.widthFeet }} <span class="pr-1">feet</span>
                {{ item.widthInches ? item.widthInches + ' inches' : '0 inches' }}
              </td>
              <td v-if="!isReviewMode" class="text-right pr-2">
                <v-btn
                    text
                    color="primary"
                    class="px-0"
                    :disabled="isAdding || isEditing"
                    @click="activeIndex = homeSections.indexOf(item)"
                >
                  <v-icon small>mdi-pencil</v-icon>
                  <span>Edit</span>
                  <v-divider class="ma-0 pl-3" vertical />
                </v-btn>
                <!-- Actions drop down menu -->
                <v-menu offset-y left nudge-bottom="4">
                  <template v-slot:activator="{ on }">
                    <v-btn
                        text
                        small
                        v-on="on"
                        color="primary"
                        :disabled="isAdding || isEditing"
                    >
                      <v-icon class="ml-n1">mdi-menu-down</v-icon>
                    </v-btn>
                  </template>

                  <!-- More actions drop down list -->
                  <v-list class="actions-dropdown actions__more-actions">
                    <v-list-item class="my-n2">
                      <v-list-item-subtitle class="pa-0" @click="remove(item)">
                        <v-icon small>mdi-delete</v-icon>
                        <span class="ml-1 remove-btn-text">Remove</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </td>
            </template>
          </tr>
        </tbody>
        <!-- No Data Message -->
        <tbody v-else>
          <tr class="text-center">
            <td :colspan="headers.length">No sections added yet</td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue-demi'
import { BaseHeaderIF, HomeSectionIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { homeSectionsTableHeaders, homeSectionsReviewTableHeaders } from '@/resources/tableHeaders'
import AddEditHomeSections from '@/components/mhrRegistration/YourHome/AddEditHomeSections.vue'
export default defineComponent({
  name: 'HomeSectionsTable',
  components: { AddEditHomeSections },
  props: {
    isAdding: { default: false },
    isReviewMode: { default: false },
    homeSections: { type: Array as () => HomeSectionIF[], default: () => [] }
  },
  setup (props, context) {
    const localState = reactive({
      activeIndex: -1,
      isEditingHomeSection: false,
      headers: computed((): Array<BaseHeaderIF> => {
        return props.isReviewMode ? homeSectionsReviewTableHeaders : homeSectionsTableHeaders
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
  .v-data-table--fixed-header > .v-data-table__wrapper {
    border-top-left-radius: 4px !important;
    border-top-right-radius: 4px !important;
  }
  .v-data-table > .v-data-table__wrapper > table > thead > tr > th {
    padding: 15px 28px;
  }
  .v-data-table > .v-data-table__wrapper > table > tbody > tr > td {
    padding: 20px 28px;
  }
  .add-edit-form-cell {
    padding: 0 !important;
  }
  .v-btn.v-btn--disabled {
    color: $app-blue !important;
    opacity: .4;
  }
  .v-list-item .v-list-item__title, .v-list-item .v-list-item__subtitle {
    line-height: 1.6 !important;
  }
}
</style>
