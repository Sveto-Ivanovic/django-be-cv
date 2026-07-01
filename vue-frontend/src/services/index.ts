import contactEndpointController from "./contact";
import userManagementEndpointController from "./usermanagement";

export const globalAPI = {
  contact: contactEndpointController,
  userManagment: userManagementEndpointController,
};