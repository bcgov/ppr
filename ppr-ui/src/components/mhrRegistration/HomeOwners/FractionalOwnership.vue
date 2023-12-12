<template>
  <div id="mhr-home-ownership">
    <label class="generic-label">Fractional Ownership</label>
    <div v-if="isReadOnly">
      <p data-test-id="readonly-interest-info">
        Interest: {{ fractionalInterest }}
      </p>
    </div>
    <div v-else>
      <p class="mt-3 mb-6">
        Enter the fraction of the total ownership owned by Group {{ getGroupNumberById(groupId) }}.
        <br>For example, if there are four owner groups, this group could have 1/4 ownership.
        The Interest Type is automatically set to "Undivided" for each group of owners.
      </p>
      <p class="mt-3 mb-6">
        <strong>Note:</strong> It is recommended that all groups use the same denominator for Total Available
        (preferably using the lowest common denominator).
      </p>
      <v-text-field
        :id="`interest-type-group-${groupId}`"
        v-model="interestText"
        label="Interest Type"
        variant="filled"
        color="primary"
        class="background-white"
        disabled
        readonly
        :data-test-id="`interest-type-field-group-${groupId}`"
      />
      <div class="owner-fractions">
        <v-row noGutters>
          <v-col class="pr-1">
            <v-text-field
              :id="`fraction-amount-group-${groupId}`"
              ref="interestNumerator"
              v-model.number="fractionalDataState.interestNumerator"
              label="Amount Owned by this Group"
              variant="filled"
              color="primary"
              class="background-white"
              :rules="fractionalAmountRules"
              :data-test-id="`fraction-amount-field-group-${groupId}`"
              @blur="$refs.interestDenominator.validate()"
            />
          </v-col>
          <span class="division-span" />
          <v-col class="pl-1">
            <v-text-field
              :id="`total-fractions-group-${groupId}`"
              ref="interestDenominator"
              v-model.number="fractionalDataState.interestDenominator"
              label="Total Available"
              variant="filled"
              color="primary"
              class="background-white"
              :rules="totalAmountRules"
              :data-test-id="`total-fractions-field-group-${groupId}`"
              @blur="$refs.interestNumerator.validate()"
            />
          </v-col>
        </v-row>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useInputRules } from '@/composables/useInputRules'
import { toTitleCase } from '@/utils'
import { useHomeOwners } from '@/composables'

export default defineComponent({
  name: 'FractionalOwnership',
  props: {
    groupId: {
      type: Number,
      required: true
    },
    isReadOnly: { type: Boolean, default: false },
    fractionalData: {
      type: Object,
      default: () => {
        return {
          type: '',
          interest: 'Undivided',
          interestNumerator: null,
          interestDenominator: null
        }
      },
      required: true
    },
    isMhrTransfer: { type: Boolean, default: false }
  },
  setup (props) {
    const { customRules, required, isNumber, greaterThan, lessThan, isLettersOnly } = useInputRules()
    const { getGroupNumberById } = useHomeOwners(props.isMhrTransfer)

    const localState = reactive({
      fractionalDataState: props.fractionalData,
      interestText: computed(() =>
        toTitleCase(localState.fractionalDataState.interest)
      ),
      fractionalInterest: computed(
        () =>
          // eslint-disable-next-line max-len
          `${localState.fractionalDataState.interest} ${localState.fractionalDataState.interestNumerator}/${localState.fractionalDataState.interestDenominator}`
      ),
      fractionalAmountRules: computed(() => {
        let rules = customRules(
          required('Enter amount owned by this group'),
          isNumber(null, null, null, null), // check for numbers only
          isNumber(null, 6, null, null) // check for length (maxLength can't be used because field is numeric)
        )
        // additional validation when interest total has some value - UX feedback
        if (localState.fractionalDataState.interestDenominator) {
          rules = customRules(
            required('Enter amount owned by this group'),
            isNumber(null, null, null, null), // check for numbers only
            isNumber(null, 6, null, null), // check for length (maxLength can't be used because field is numeric)
            greaterThan(Number(localState.fractionalDataState.interestDenominator - 1),
              'Must be less than total available'
            )
          )
        }
        return rules
      }),
      totalAmountRules: computed(() =>
        customRules(
          required('Enter total available'),
          isNumber(null, null, null, null), // check for numbers only
          isNumber(null, 6, null, null), // check for length (maxLength can't be used because field is numeric)
          lessThan(Number(
            localState.fractionalDataState.interestNumerator),
          'Must be greater than amount owned by group'
          )
        )
      )
    })

    return {
      isLettersOnly,
      getGroupNumberById,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.division-span {
  height: 40px;
  border-right: 1px solid black;
  width: 30px;
  transform: rotate(20deg);
  right: 13px;
  top: 3px;
  position: relative;
}
</style>
