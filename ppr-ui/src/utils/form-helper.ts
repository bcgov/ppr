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

// Scroll to first designated error on Information or Review page
export async function scrollToFirstErrorComponent (): Promise<void> {
  setTimeout(() => {
    document.getElementsByClassName('border-error-left').length > 0 &&
      document
        .getElementsByClassName('border-error-left')[0]
        .scrollIntoView({ behavior: 'smooth' })
  }, 500)
}
