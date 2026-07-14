import { defineStore } from "pinia";
import { ref } from 'vue';
import type { SendContactInfo } from "../../services/contact/types";

export const useContactStore = defineStore("contactStore", () => {

  let contact = ref<SendContactInfo>();

  function initContact(data: SendContactInfo) {
    contact.value = data;
  }

  function removeContact() {
    contact.value = {
        message: ""
    }
  }

  return {
    contact,
    initContact,
    removeContact,
  };
});