export interface FormIF extends HTMLFormElement {
  reset(): void
  validate(): boolean
  resetValidation(): void
}
