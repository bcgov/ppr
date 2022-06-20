import { Component, Vue } from 'vue-property-decorator'
import { Getter } from 'vuex-class'
import { StateModelIF } from '@/interfaces'
import { get, find } from 'lodash'
import { mhrRegistrationValidation } from '@/utils/validators/mhr-registration-validation'

/**
 * Mixin for handing field validation and error messages retrieval
 */

@Component({})
export default class ErrorMixin extends Vue {
  @Getter getStateModel!: StateModelIF

  // Get message for field id
  // Field id should match the state model
  getMessage (fieldId: string) {
    return this.validateFieldAndGetErrorMessage(fieldId)
  }

  private validateFieldAndGetErrorMessage (fieldId) {
    // Find validation rules for specific field id
    const fieldValidations = find(mhrRegistrationValidation.fields, {
      id: fieldId
    })
    // Get value of the field from the model
    const filedValue = get(this.getStateModel, fieldId)
    // Validate field based on its validations and get the error message
    return fieldValidations.validations(filedValue)
  }
}
