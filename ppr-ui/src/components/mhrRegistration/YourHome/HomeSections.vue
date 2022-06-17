<template>
  <div id="mhr-home-sections-shim">
    <v-btn
      outlined
      class="add-home-section-btn"
      color="primary"
      :ripple="false"
      :disabled="showAddEditHomeSections || isEditingHomeSection"
      @click="showAddEditHomeSections = true"
    >
      <v-icon class="pr-1">mdi-home-plus</v-icon> Add a Section
    </v-btn>

    <!-- Add New Home Section Form -->
    <v-expand-transition>
      <AddEditHomeSections
        v-if="showAddEditHomeSections"
        :isNewHomeSection="isNewHomeSection"
        @close="showAddEditHomeSections = false"
        @submit="addHomeSection($event)"
      />
    </v-expand-transition>

    <!-- Home Sections Table -->
    <article class="mt-6">
      <p>Number of Sections: {{getMhrHomeSections.length}}</p>
      <HomeSectionsTable
        :isAdding="showAddEditHomeSections"
        :homeSections="getMhrHomeSections"
        @isEditing="isEditingHomeSection = $event"
        @edit="editHomeSection($event)"
        @remove="removeHomeSection($event)"
      />
    </article>
  </div>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import {
  IndividualNameIF,
  HomeSectionIF
} from '@/interfaces'
import AddEditHomeSections from '@/components/mhrRegistration/YourHome/AddEditHomeSections.vue'
import HomeSectionsTable from '@/components/tables/mhr/HomeSectionsTable.vue'
export default defineComponent({
  name: 'HomeSections',
  components: {
    AddEditHomeSections,
    HomeSectionsTable
  },
  props: {
    defaultDebtor: {
      type: Object as () => IndividualNameIF
    },
    defaultFolioNumber: {
      type: String,
      default: ''
    }
  },
  setup () {
    const {
      setHomeSections
    } = useActions<any>([
      'setHomeSections'
    ])
    const {
      getMhrHomeSections
    } = useGetters<any>([
      'getMhrHomeSections'
    ])
    const localState = reactive({
      isEditingHomeSection: false,
      isNewHomeSection: true,
      showAddEditHomeSections: false
    })
    const addHomeSection = (homeSection: HomeSectionIF): void => {
      const homeSections = [...getMhrHomeSections.value]
      // Add new home section to array
      homeSections.push(homeSection)
      setHomeSections(homeSections)
    }
    const editHomeSection = (homeSection: HomeSectionIF): void => {
      const homeSections = [...getMhrHomeSections.value]
      // Create edited homeSection without id
      const { id, ...editedSection } = homeSection
      // Apply edited section to temp array
      homeSections[homeSection.id] = editedSection

      setHomeSections(homeSections)
    }
    const removeHomeSection = (homeSection: HomeSectionIF): void => {
      const homeSections = [...getMhrHomeSections.value]
      // Remove home section from array
      homeSections.splice(homeSections.indexOf(homeSection), 1)
      setHomeSections(homeSections)
    }
    return {
      addHomeSection,
      editHomeSection,
      removeHomeSection,
      getMhrHomeSections,
      ...toRefs(localState)
    }
  }
})
/* eslint-enable no-unused-vars */
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
