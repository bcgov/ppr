<template>
  <v-card
    flat
    rounded
    class="mt-2"
  >
    <v-table
      id="mh-home-sections-table"
      class="home-sections-table"
      fixedHeader
    >
      <template #default>
        <!-- Table Headers -->
        <thead>
          <tr>
            <th
              v-for="header in headers"
              :key="header.value"
              :class="[header.class, (isReviewMode && header == headers[0]) ? 'pl-0' : '']"
            >
              {{ header.text }}
            </th>
          </tr>
        </thead>

        <!-- Table Body -->
        <tbody v-if="homeSections.length > 0">
          <tr
            v-for="(item, index) in homeSections"
            :key="`${item}: ${index}`"
          >
            <!-- Edit Form -->
            <template v-if="isActiveIndex(homeSections.indexOf(item))">
              <td
                class="add-edit-form-cell"
                :colspan="headers.length"
              >
                <AddEditHomeSections
                  :editHomeSection="item"
                  :isNewHomeSection="false"
                  :validate="validate"
                  @close="activeIndex = -1"
                  @remove="remove(item)"
                  @submit="edit($event)"
                />
              </td>
            </template>

            <!-- Table Rows -->
            <template v-else>
              <td :class="{ 'pl-0': isReviewMode }">
                {{ homeSections.indexOf(item) + 1 }}
                <InfoChip
                  class="ml-2"
                  :action="item.action"
                />
              </td>
              <td>{{ item.serialNumber }}</td>
              <td>
                {{ item.lengthFeet }} <span class="pr-1">feet</span>
                {{ item.lengthInches ? item.lengthInches + ' inches' : '0 inches' }}
              </td>
              <td>
                {{ item.widthFeet }} <span class="pr-1">feet</span>
                {{ item.widthInches ? item.widthInches + ' inches' : '0 inches' }}
              </td>
              <td
                v-if="!isReviewMode"
                class="text-right pr-2"
              >
                <v-btn
                  v-if="isMhrCorrection && showCorrectUndoOptions(item)"
                  variant="plain"
                  color="primary"
                  :ripple="false"
                  :data-test-id="`undo-btn-section-${index}`"
                  @click="undoHomeSectionChanges(item)"
                >
                  <v-icon size="small">
                    mdi-undo
                  </v-icon>
                  <span>Undo</span>
                  <v-divider
                    class="ma-0 pl-3 mr-n5"
                    vertical
                  />
                </v-btn>

                <v-btn
                  v-else
                  variant="plain"
                  color="primary"
                  class="px-0"
                  :disabled="isAdding || isEditing"
                  :data-test-id="`edit-btn-section-${index}`"
                  @click="activeIndex = homeSections.indexOf(item)"
                >
                  <v-icon size="small">
                    mdi-pencil
                  </v-icon>
                  <span v-if="isMhrCorrection && item.action !== 'ADDED'">Correct</span>
                  <span v-else>Edit</span>
                  <v-divider
                    class="ma-0 pl-3"
                    vertical
                  />
                </v-btn>
                <!-- Actions drop down menu -->
                <v-menu
                  location="bottom right"
                >
                  <template #activator="{ props }">
                    <v-btn
                      variant="plain"
                      size="small"
                      color="primary"
                      :disabled="isAdding || isEditing"
                      v-bind="props"
                    >
                      <v-icon class="ml-n1">
                        mdi-menu-down
                      </v-icon>
                    </v-btn>
                  </template>

                  <!-- More actions drop down list -->
                  <v-list class="actions-dropdown actions__more-actions">
                    <v-list-item
                      v-if="showCorrectUndoOptions(item)"
                      class="my-n2"
                    >
                      <v-list-item-subtitle
                        class="pa-0"
                        @click="activeIndex = homeSections.indexOf(item)"
                      >
                        <v-icon size="small">
                          mdi-delete
                        </v-icon>
                        <span class="ml-1 edit-btn-text">Correct</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item class="my-n2">
                      <v-list-item-subtitle
                        class="pa-0"
                        @click="remove(item)"
                      >
                        <v-icon size="small">
                          mdi-delete
                        </v-icon>
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
          <tr>
            <td
              class="text-center"
              :colspan="headers.length"
            >
              No sections added yet
            </td>
          </tr>
        </tbody>
      </template>
    </v-table>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { BaseHeaderIF, HomeSectionIF } from '@/interfaces'
import { homeSectionsTableHeaders, homeSectionsReviewTableHeaders } from '@/resources/tableHeaders'
import AddEditHomeSections from '@/components/mhrRegistration/YourHome/AddEditHomeSections.vue'
import { useMhrCorrections } from '@/composables'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { InfoChip } from '@/components/common'
import { ActionTypes } from '@/enums'

export default defineComponent({
  name: 'HomeSectionsTable',
  components: { AddEditHomeSections, InfoChip },
  props: {
    isAdding: {
      type: Boolean,
      default: false
    },
    isReviewMode: {
      type: Boolean,
      default: false
    },
    homeSections: { type: Array as () => HomeSectionIF[], default: () => [] },
    validate: { type: Boolean, default: false }
  },
  emits: ['edit', 'remove', 'undo', 'isEditing'],
  setup (props, context) {
    const {
      getMhrBaseline,
      getMhrRegistration
    } = storeToRefs(useStore())

    const { isMhrCorrection } = useMhrCorrections()

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

    const showCorrectUndoOptions = (item: HomeSectionIF): boolean => {
      return [ActionTypes.REMOVED, ActionTypes.CORRECTED].includes(item?.action)
    }

    const undoHomeSectionChanges = (item: HomeSectionIF): void => {
      const baselineHomeSection = getMhrBaseline.value.description.sections[item.id]
      context.emit('undo', { ...baselineHomeSection, id: item.id, action: null })
    }

    watch(() => localState.isEditing, () => { context.emit('isEditing', localState.isEditing) })

    return {
      edit,
      remove,
      isActiveIndex,
      isMhrCorrection,
      getMhrBaseline,
      getMhrRegistration,
      showCorrectUndoOptions,
      undoHomeSectionChanges,
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
:deep(.v-table__wrapper) {
  overflow-x: hidden;
}
:deep() {
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
