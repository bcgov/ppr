export function focusOnFirstError (formName: string): void {
  setTimeout(() => {
    const firstErrorField = document
      .getElementById(formName)
      .getElementsByClassName('error--text')
      .item(0)
      .getElementsByTagName('input')
      .item(0) as HTMLElement | null

    firstErrorField.focus()
  }, 50)
}
