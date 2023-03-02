<template>
  <div id="mhr-home-ownership">
    <label class="generic-label">Fractional Ownership</label>
    <div v-if="isReadOnly">
      <p data-test-id="readonly-interest-info">Interest: {{ fractionalInterest }}</p>
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
        label="Interest Type"
        filled
        class="background-white"
        v-model="interestText"
        disabled
        readonly
        :data-test-id="`interest-type-field-group-${groupId}`"
        @mousedown.prevent
        @mousemove.prevent
        @dblclick.prevent
      />
      <div class="owner-fractions">
        <v-text-field
          :id="`fraction-amount-group-${groupId}`"
          label="Amount Owned by this Group"
          filled
          class="background-white"
          v-model.number="fractionalData.interestNumerator"
          :rules="fractionalAmountRules"
          :data-test-id="`fraction-amount-field-group-${groupId}`"
          ref="interestNumerator"
          @blur="$refs.interestDenominator.validate()"
        />
        <span> </span>
        <v-text-field
          :id="`total-fractions-group-${groupId}`"
          label="Total Available"
          filled
          class="background-white"
          v-model.number="fractionalData.interestDenominator"
          :rules="totalAmountRules"
          :data-test-id="`total-fractions-field-group-${groupId}`"
          ref="interestDenominator"
          @blur="$refs.interestNumerator.validate()"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
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
      default: {
        type: '',
        interest: 'Undivided',
        interestNumerator: null,
        interestDenominator: null,
        tenancySpecified: null
      },
      required: true
    },
    isMhrTransfer: { type: Boolean, default: false }
  },
  setup (props) {
    const { customRules, required, isNumber, greaterThan, lessThan, isLettersOnly } = useInputRules()
    const { getGroupNumberById } = useHomeOwners(props.isMhrTransfer)

    const localState = reactive({
      interestText: computed(() =>
        toTitleCase(props.fractionalData.interest)
      ),
      fractionalInterest: computed(
        () =>
          // eslint-disable-next-line max-len
          `${props.fractionalData.interest} ${props.fractionalData.interestNumerator}/${props.fractionalData.interestDenominator}`
      ),
      fractionalAmountRules: computed(() => {
        let rules = customRules(
          required('Enter amount owned by this group'),
          isNumber(null, null, null, null), // check for numbers only
          isNumber(null, 6, null, null) // check for length (maxLength can't be used because field is numeric)
        )
        // additional validation when interest total has some value - UX feedback
        if (props.fractionalData.interestDenominator) {
          rules = customRules(
            required('Enter amount owned by this group'),
            isNumber(null, null, null, null), // check for numbers only
            isNumber(null, 6, null, null), // check for length (maxLength can't be used because field is numeric)
            greaterThan(Number(props.fractionalData.interestDenominator - 1),
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
          lessThan(Number(props.fractionalData.interestNumerator), 'Must be greater than amount owned by group')
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

#mhr-home-ownership ::v-deep {
  p {
    white-space: normal;
    font-size: 16px;
    line-height: 24px;
    color: #495057
  }
  .owner-fractions {
    display: flex;
    flex-direction: row;

    span {
      height: 40px;
      border-right: 1px solid black;
      width: 30px;
      transform: rotate(20deg);
      right: 13px;
      top: 3px;
      position: relative;
    }
  }

  .theme--light.v-text-field--filled.v-input--is-disabled > .v-input__control > .v-input__slot {
    border-bottom: 1px dotted;
    cursor: default!important;
  }
  .theme--light.v-input--is-disabled input {
    pointer-events: none!important;
    user-select: none!important;
    -webkit-user-select: none; /* webkit (safari, chrome) browsers */
    -moz-user-select: none; /* mozilla browsers */
    -ms-user-select: none; /* IE10+ */
  }

  .theme--light.v-label--is-disabled {
    color: $gray7!important;
  }
}

</style>
