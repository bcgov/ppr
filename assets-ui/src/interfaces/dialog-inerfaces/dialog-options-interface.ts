// dialog options interface
export interface DialogOptionsIF {
  acceptText: string
  cancelText: string
  hasContactInfo?: boolean // if not set it will default to false
  label?: string
  text: string
  textExtra?: string[]
  title: string
}
