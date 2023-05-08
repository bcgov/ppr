import { HomeOwnerPartyTypes } from '@/enums'
import { OwnerRoleConfigIF } from '@/interfaces'

export const HomeOwnerRoles: Array<OwnerRoleConfigIF> = [
  {
    id: 'owner-option',
    class: 'owner-radio pr-2',
    model: HomeOwnerPartyTypes.OWNER_IND,
    label: 'Owner',
    tooltipContent: 'An Owner is the legal and beneficial owner of the home. If the owner is a trustee of a trust, ' +
      'this home ownership structure must be registered by BC Registries staff. '
  },
  {
    id: 'executor-option',
    class: 'executor-radio px-4',
    model: HomeOwnerPartyTypes.EXECUTOR,
    label: 'Executor',
    tooltipContent: 'An Executor is the personal representative named in the will or appointed by court to carry out ' +
      'the requirements of a will. They are also referred to as trustee or liquidator (in Quebec).'
  },
  {
    id: 'administrator-option',
    class: 'administrator-radio px-4',
    model: HomeOwnerPartyTypes.ADMINISTRATOR,
    label: 'Administrator',
    tooltipContent: '\n' +
      'An Administrator is the personal representative appointed by the court through a Grant of Administration to' +
      ' handle and distribute the estate of the deceased owner.'
  },
  {
    id: 'trustee-option',
    class: 'trustee-radio pl-2',
    model: HomeOwnerPartyTypes.TRUSTEE,
    label: 'Bankruptcy Trustee',
    tooltipContent: 'A Bankruptcy Trustee is a professional who is licensed by the Government of Canada to administer' +
      ' a bankruptcy. '
  }
]
