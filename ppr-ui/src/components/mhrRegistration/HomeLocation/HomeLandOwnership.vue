<template>
  <v-card
    id="mhr-home-land-ownership"
    flat
    rounded
    class="mhr-home-land-ownership pa-8 pb-0 mt-8"
  >
    <v-form ref="leaseOrOwnForm">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
        >
          <h4
            class="fs-16 lh-22"
            :class="{'error-text': validate}"
          >
            Land Lease or Ownership
          </h4>
          <UpdatedBadge
            v-if="updatedBadge"
            :action="updatedBadge.action"
            :baseline="updatedBadge.baseline"
            :current-state="updatedBadge.currentState"
            is-case-sensitive
          />
        </v-col>
        <v-col
          cols="12"
          sm="9"
        >
          <p>
            {{ content.description }}
          </p>

          <v-radio-group
            id="lease-own-option"
            v-model="isOwnLand"
            class="mt-10 mb-5"
            inline
            data-test-id="ownership-radios"
          >
            <v-radio
              id="yes-option"
              class="radio-one"
              label="Yes"
              :class="{'selected-radio': isOwnLand === true}"
              :value="true"
              data-test-id="yes-ownership-radio-btn"
            />
            <v-radio
              id="no-option"
              class="radio-two"
              label="No"
              :class="{'selected-radio': isOwnLand === false}"
              :value="false"
              data-test-id="no-ownership-radio-btn"
            />
          </v-radio-group>

          <div v-if="isOwnLand">
            <v-divider class="mx-0 divider-mt" />
            <p
              class="py-10"
              data-test-id="yes-paragraph"
            >
              <b>Note:</b> Land ownership or registered lease of the land for 3 years or more
              must be verifiable through the BC Land Title and Survey Authority (LTSA)
              or other authorized land authority.
            </p>
          </div>

          <div v-if="!isOwnLand && isOwnLand!=null">
            <v-divider class="mx-0 divider-mt" />
            <p
              class="py-10"
              data-test-id="no-paragraph"
            >
              <b>Note:</b> Written permission and tenancy agreements from the landowner
              may be required for the home to remain on the land.
              <br><br>
              Relocation of the home onto land that the homeowner does not own or hold a
              registered lease of 3 years or more may require additional permits from
              authorities such as the applicable Municipality, Regional District, First
              Nation, or Provincial Crown Land Office.
            </p>
          </div>
        </v-col>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import type { ContentIF, FormIF, UpdatedBadgeIF } from '@/interfaces'
import { UpdatedBadge } from '@/components/common'

export default defineComponent({
  name: 'HomeLandOwnership',
  components: {
    UpdatedBadge
  },
  props: {
    ownLand: {
      type: Boolean,
      default: undefined
    },
    validate: {
      type: Boolean,
      default: false
    },
    content: {
      type: Object as () => ContentIF,
      default: () => {}
    },
    updatedBadge: {
      type: Object as () => UpdatedBadgeIF,
      default: () => null
    }
  },
  emits: ['isValid', 'setStoreProperty'],
  setup (props, { emit }) {
    const leaseOrOwnForm = ref(null) as FormIF

    const localState = reactive({
      isOwnLand: props.ownLand,
      isValidHomeLandOwnership: computed((): boolean => {
        return localState.isOwnLand !== null
      })
    })

    const validateForm = (): void => {
      if (props.validate) {
        leaseOrOwnForm.value?.validate()
      }
    }

    watch(() => localState.isOwnLand, (val: boolean) => {
      emit('setStoreProperty', val)
    })

    watch(() => localState.isValidHomeLandOwnership, async (val: boolean) => {
      emit('isValid', val)
    }, { immediate: true })

    watch(() => props.validate, () => {
      validateForm()
    })

    return {
      leaseOrOwnForm,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.divider-mt {
  margin-top: 14px;
}
</style>
