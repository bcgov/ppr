<template>
  <div id="mhr-home-ownership">
    <label class="generic-label">Fractional Ownership</label>
    <div v-if="isReadOnly">
      <p data-test-id="readonly-interest-info">Interest: {{ fractionalInterest }}</p>
    </div>
    <div v-else>
      <p class="mt-3 mb-6">
        Enter the interest type and fraction of the total ownership owned by Group 1. For example,
        if there are four owner groups, this group could have 1/4 ownership.
      </p>
      <v-text-field
        :id="`interest-type-group-${groupId}`"
        label="Interest Type (Optional)"
        v-model="fractionalData.interest"
        :data-test-id="`interest-type-field-group-${groupId}`"
      />
      <div class="owner-fractions">
        <v-text-field
          :id="`fraction-amount-group-${groupId}`"
          label="Amount Owned by this Group"
          filled
          v-model.number="fractionalData.interestNumerator"
          :rules="fractionalAmountRules"
          :data-test-id="`fraction-amount-field-group-${groupId}`"
          ref="interestNumerator"
          @blur="$refs.interestTotal.validate()"
        />
        <span> </span>
        <v-text-field
          :id="`total-fractions-group-${groupId}`"
          label="Total Available"
          filled
          v-model.number="fractionalData.interestTotal"
          :rules="totalAmountRules"
          :data-test-id="`total-fractions-field-group-${groupId}`"
          ref="interestTotal"
          @blur="$refs.interestNumerator.validate()"
        />
      </div>
      <label class="generic-label" for="tenancy-type">Tenancy</label>
      <v-checkbox :id="`tenancy-type-group-${groupId}`" v-model="fractionalData.tenancySpecified">
        <template v-slot:label>
          <p class="ma-0">
            Tenancy not specified
          </p>
        </template>
      </v-checkbox>
    </div>
  </div>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { MhrRegistrationHomeOwnersIF } from '@/interfaces'
/* eslint-enable no-unused-vars */

import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useInputRules } from '@/composables/useInputRules'

let DEFAULT_OWNER_ID = 1

export default defineComponent({
  name: 'FractionalOwnership',
  props: {
    groupId: {
      type: String,
      required: true
    },
    editHomeOwner: {
      type: Object as () => MhrRegistrationHomeOwnersIF,
      default: null
    },
    showEditBtn: { type: Boolean, default: true },
    isReadOnly: { type: Boolean, default: false },
    fractionalData: {
      type: Object,
      default: null,
      required: true
    }
  },
  setup (props) {
    const { customRules, required, isNumber, greaterThan, lessThan } = useInputRules()

    const localState = reactive({
      id: props.editHomeOwner?.id || (DEFAULT_OWNER_ID++).toString(),
      fractionalInfo: props.fractionalData,
      fractionalInterest: computed(
        () =>
          // eslint-disable-next-line max-len
          `${props.fractionalData.interest} ${props.fractionalData.interestNumerator} / ${props.fractionalData.interestTotal}`
      ),
      fractionalAmountRules: computed(() => {
        const rules = customRules(
          required('Enter amount owned by this group'),
          isNumber(null, null, null, null), // check for numbers only
          isNumber(null, 6, null, null) // check for length (maxLength can't be used because field is numeric)
        )
        // additional validation when interest total has some value - UX feedback
        if (localState.fractionalInfo.interestTotal) {
          rules.push(
            ...greaterThan(Number(localState.fractionalInfo.interestTotal), 'Must be lesser than total available')
          )
        }
        return rules
      }),
      totalAmountRules: computed(() =>
        customRules(
          required('Enter total available'),
          isNumber(null, null, null, null), // check for numbers only
          isNumber(null, 6, null, null), // check for length (maxLength can't be used because field is numeric)
          lessThan(Number(localState.fractionalInfo.interestNumerator), 'Must be greater than amount owned by group')
        )
      )
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
#mhr-home-ownership ::v-deep {
  p {
    white-space: normal;
    font-size: 16px;
    line-height: 24px;
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
}
</style>
