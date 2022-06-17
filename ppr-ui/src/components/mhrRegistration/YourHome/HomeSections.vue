<template>
  <div id="mhr-home-sections-shim">
    <v-btn
      outlined
      class="add-home-section-btn"
      color="primary"
      :ripple="false"
      :disabled="showAddEditHomeSections"
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
        @submit="addEditHomeSection($event)"
      />
    </v-expand-transition>

    <!-- Home Sections Table -->
    <article class="mt-6">
      <p>Number of Sections: 0</p>
      <HomeSectionsTable />
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
  setup (props, { emit }) {
    const {
      setIsStaffClientPayment
    } = useActions<any>([
      'setHomeSection'
    ])
    const {
      getUserSettings
    } = useGetters<any>([
      'getUserSettings'
    ])
    const localState = reactive({
      isNewHomeSection: true,
      showAddEditHomeSections: false
    })

    const addEditHomeSection = (homeSection: HomeSectionIF): void => {
      // Add Section to store array
      console.log(homeSection)
    }

    return {
      addEditHomeSection,
      ...toRefs(localState)
    }
  }
})
/* eslint-enable no-unused-vars */
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
