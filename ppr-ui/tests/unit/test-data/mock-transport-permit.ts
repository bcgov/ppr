import { HomeLocationTypes, MhApiStatusTypes } from "@/enums";
import { MhrRegistrationHomeLocationIF } from "@/interfaces";

export const mockTransportPermitNewLocation: MhrRegistrationHomeLocationIF = {
  address: {
    city: "KELOWNA",
    country: "CA",
    postalCode: "",
    region: "BC",
    street: "123-720 COMMONWEALTH RD",
    streetAdditional: ''
  },
  leaveProvince: false,
  locationType: HomeLocationTypes.HOME_PARK,
  pad: '147',
  parkName: 'Fort York',
  permitWithinSamePark: false,
  taxCertificate: true,
  taxExpiryDate: "2024-02-06T08:01:00+00:00"
}
