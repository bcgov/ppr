<template>
  <v-card flat rounded id="add-edit-home-sections-form" class="mt-8 pa-8">
    <v-form ref="addEditHomeSectionsForm" v-model="addEditValid">
      <v-row no-gutters>
        <v-col cols="12" sm="2">
          <label class="generic-label">{{ isNewHomeSection ? 'Add' : 'Edit' }} Section</label>
        </v-col>
        <v-col cols="12" sm="10" class="pl-2">
          <!-- Add Edit Form -->
          <label class="generic-label">Serial Number</label>
          <v-text-field
            filled
            id="serial-number"
            class="pt-4"
            label="Serial Number"
            v-model="serialNumber"
            :rules="hasSubmit ? required('Enter a serial number') : []"
            persistent-hint
          />

          <label class="generic-label">Length</label>
          <v-row no-gutters class="pt-4">
            <v-text-field
              filled
              id="length-feet"
              class="numberInput pr-2"
              label="Feet"
              v-model.number="lengthFeet"
              :rules="hasSubmit ? lengthFeetRules : []"
              persistent-hint
            />
            <v-text-field
              filled
              id="length-inches"
              class="numberInput pl-2"
              label="Inches (Optional)"
              v-model.number="lengthInches"
              :rules="hasSubmit ? customRules(invalidSpaces(), isNumber()) : []"
              persistent-hint
            />
          </v-row>

          <label class="generic-label">Width</label>
          <v-row no-gutters class="pt-4">
            <v-text-field
              filled
              id="width-feet"
              class="numberInput pr-2"
              label="Feet"
              v-model.number="widthFeet"
              :rules="hasSubmit ? widthFeetRules : []"
              persistent-hint
            />
            <v-text-field
              filled
              id="numberInput width-inches"
              class="pl-2"
              label="Inches (Optional)"
              v-model.number="widthInches"
              :rules="hasSubmit ? customRules(invalidSpaces(), isNumber()) : []"
              persistent-hint
            />
          </v-row>

          <!-- Action buttons -->
          <v-row>
            <v-col>
              <div class="form__row form__btns">
                <v-btn
                  large
                  outlined
                  color="error"
                  id="remove-btn-party"
                  class="remove-btn"
                  :disabled="isNewHomeSection"
                  @click="remove()"
                >
                  Remove
                </v-btn>

                <v-btn
                  large
                  id="done-btn-party"
                  class="ml-auto"
                  color="primary"
                  @click="submit()"
                >
                  Done
                </v-btn>

                <v-btn
                  id="cancel-btn-party"
                  large
                  outlined
                  color="primary"
                  @click="close()"
                >
                  Cancel
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { HomeSectionIF } from '@/interfaces'
import { useInputRules } from '@/composables/useInputRules'
/* eslint-disable no-unused-vars */

export default defineComponent({
  name: 'AddEditHomeSections',
  props: {
    isNewHomeSection: { type: Boolean, default: true },
    editHomeSection: { type: Object as () => HomeSectionIF, default: () => {} }
  },
  setup (props, context) {
    const {
      required,
      invalidSpaces,
      isNumber,
      customRules
    } = useInputRules()

    const localState = reactive({
      addEditValid: false,
      serialNumber: props.editHomeSection?.serialNumber || '',
      lengthFeet: props.editHomeSection?.lengthFeet || null,
      lengthInches: props.editHomeSection?.lengthInches || null,
      widthFeet: props.editHomeSection?.widthFeet || null,
      widthInches: props.editHomeSection?.widthInches || null,
      hasSubmit: false,
      lengthFeetRules: computed((): Array<Function> => {
        return customRules(required('Enter a foot length'), invalidSpaces(), isNumber())
      }),
      widthFeetRules: computed((): Array<Function> => {
        return customRules(required('Enter a foot width'), invalidSpaces(), isNumber())
      })
    })

    const close = (): void => { context.emit('close') }
    const remove = (): void => { context.emit('remove') }
    const submit = async (): Promise<void> => {
      localState.hasSubmit = true
      // @ts-ignore - function exists
      await context.refs.addEditHomeSectionsForm.validate()

      if (localState.addEditValid) {
        context.emit('submit', {
          serialNumber: localState.serialNumber,
          lengthFeet: localState.lengthFeet,
          lengthInches: localState.lengthInches,
          widthFeet: localState.widthFeet,
          widthInches: localState.widthInches
        })
        close()
      }
    }

    return {
      close,
      remove,
      submit,
      required,
      invalidSpaces,
      isNumber,
      customRules,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
