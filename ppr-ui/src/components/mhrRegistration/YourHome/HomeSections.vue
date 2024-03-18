<template>
  <div id="mhr-home-sections-shim">
    <v-row
      v-if="!isReviewMode"
      noGutters
    >
      <v-btn
        variant="outlined"
        class="mt-3 add-home-section-btn"
        color="primary"
        :ripple="false"
        :disabled="showAddEditHomeSections || isEditingHomeSection"
        @click="openAddNewHomeSectionForm()"
      >
        <v-icon class="pr-1">
          mdi-home-plus
        </v-icon> Add a Section
      </v-btn>
      <span
        v-if="displayHomeSectionsError && isMaxHomeSections"
        class="pl-7 pt-4 error-text"
      >
        Your registration cannot contain more than four sections
      </span>
    </v-row>

    <v-row
      noGutters
      class="mt-6"
    >
      <p
        v-if="!isReviewMode"
        id="section-count"
      >
        Number of Sections: {{ getMhrHomeSections.length }}
      </p>
      <span
        v-if="validate && !hasMinimumHomeSections"
        class="pl-4 error-text"
      >
        Your registration must contain at least one section
      </span>
    </v-row>

    <!-- Add New Home Section Form -->
    <v-expand-transition>
      <AddEditHomeSections
        v-if="showAddEditHomeSections"
        :isNewHomeSection="isNewHomeSection"
        :validate="validate"
        @close="showAddEditHomeSections = false"
        @submit="addHomeSection($event)"
      />
    </v-expand-transition>

    <!-- Home Sections Table -->
    <HomeSectionsTable
      :class="{ 'border-error-left': validate }"
      :validate="validate"
      :isAdding="showAddEditHomeSections"
      :homeSections="getMhrHomeSections"
      :isReviewMode="isReviewMode"
      @isEditing="isEditingHomeSection = $event"
      @edit="editHomeSection($event)"
      @remove="removeHomeSection($event)"
      @undo="undoHomeSection($event)"
    />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { HomeSectionIF } from '@/interfaces'
import AddEditHomeSections from '@/components/mhrRegistration/YourHome/AddEditHomeSections.vue'
import HomeSectionsTable from '@/components/tables/mhr/HomeSectionsTable.vue'
import { useMhrCorrections, useMhrValidations } from '@/composables'
import { ActionTypes } from '@/enums'

export default defineComponent({
  name: 'HomeSections',
  components: {
    AddEditHomeSections,
    HomeSectionsTable
  },
  props: {
    isReviewMode: {
      type: Boolean,
      default: false
    },
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const {
      // Actions
      setMhrHomeDescription
    } = useStore()
    const {
      // Getters
      getMhrHomeSections,
      getMhrRegistrationValidationModel,
      getMhrBaseline
    } = storeToRefs(useStore())

    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const { isMhrCorrection, correctHomeSection } = useMhrCorrections()

    const localState = reactive({
      isEditingHomeSection: false,
      isNewHomeSection: true,
      displayHomeSectionsError: false,
      showAddEditHomeSections: false,
      isMaxHomeSections: computed((): boolean => {
        return getMhrHomeSections.value.length === 4
      }),
      hasMinimumHomeSections: computed((): boolean => {
        return getMhrHomeSections.value.length >= 1
      })
    })

    const openAddNewHomeSectionForm = (): void => {
      if (!localState.isMaxHomeSections) {
        localState.showAddEditHomeSections = true
        localState.displayHomeSectionsError = false
      } else localState.displayHomeSectionsError = true
    }

    const addHomeSection = (homeSection: HomeSectionIF): void => {
      const homeSections = [...getMhrHomeSections.value]
      if (isMhrCorrection.value) {
        homeSection.action = ActionTypes.ADDED
      }
      // Add new home section to array
      homeSections.push(homeSection)
      setMhrHomeDescription({ key: 'sections', value: homeSections })
    }

    const editHomeSection = (homeSection: HomeSectionIF): void => {
      const homeSections = [...getMhrHomeSections.value]
      // Create edited homeSection without id
      const { ...editedSection } = homeSection

      if (isMhrCorrection.value) {
        correctHomeSection(editedSection)
      }
      // Apply edited section to temp array
      homeSections[homeSection.id] = editedSection

      setMhrHomeDescription({ key: 'sections', value: homeSections })
    }

    const removeHomeSection = (homeSection: HomeSectionIF): void => {
      const homeSections = [...getMhrHomeSections.value]
      const homeSectionIndex = homeSections.indexOf(homeSection)

      if (isMhrCorrection.value) {
        if (homeSection.action === ActionTypes.ADDED) {
          // for newly Added section - remove section completely
          homeSections.splice(homeSectionIndex, 1)
        } else {
          // for existing sections - mark as removed/deleted
          homeSections[homeSectionIndex].action = ActionTypes.REMOVED
        }
      } else {
        // Remove home section from array
        homeSections.splice(homeSectionIndex, 1)
      }
      setMhrHomeDescription({ key: 'sections', value: homeSections })
    }

    const undoHomeSection = (homeSection: HomeSectionIF): void => {
      const homeSections = [...getMhrHomeSections.value]
      homeSections[homeSection.id] = homeSection
      setMhrHomeDescription({ key: 'sections', value: homeSections })
    }

    watch(() => localState.hasMinimumHomeSections, (val: boolean) => {
      setValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.HOME_SECTION_VALID, val)
    }, { immediate: true })

    watch(() => localState.showAddEditHomeSections, () => {
      setValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.HOME_SECTION_VALID,
        !localState.showAddEditHomeSections && localState.hasMinimumHomeSections)
    })

    watch(() => localState.isEditingHomeSection, () => {
      setValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.HOME_SECTION_VALID,
        !localState.isEditingHomeSection && localState.hasMinimumHomeSections)
    })

    return {
      addHomeSection,
      editHomeSection,
      removeHomeSection,
      undoHomeSection,
      openAddNewHomeSectionForm,
      getMhrHomeSections,
      ...toRefs(localState)
    }
  }
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
