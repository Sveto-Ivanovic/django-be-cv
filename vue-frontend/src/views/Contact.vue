<template>
  <div class="contact-page-wrapper">
    <div class="contact-header">Contact us</div>

    <form v-on:submit.prevent="submitForm">
      <div class="form-div-wrapper">

        <div>
          <label class="label-class" for="fname">Name:</label><br>
          <input type="text" id="fname" name="fname" required v-model="name">
        </div>

        <div>
          <label class="label-class" for="email">Email:</label><br>
          <input type="text" id="email" name="email" v-model="email" required>
        </div>

        <div>
          <label class="label-class" for="phone">Phone Number:</label><br>
          <input type="text" id="phone" name="phone" v-model="phone">
        </div>

        <div>
          <label class="label-class" for="message">Message:</label><br>
          <textarea name="message" id="message" v-model="message" required></textarea>
        </div>

        <div class="submit-button-div">
          <button class="submit-button-class" type="submit">Submit</button>
        </div>
      </div>
    </form>




  </div>





</template>



<script setup lang="ts">
import { ref } from "vue";
import contactApi from '../services/contact'

const name = ref("");
const email = ref("");
const phone = ref("");
const message = ref("");
const { mutateAsync, isPending } = contactApi.useSendContactMessage()


async function submitForm() {
  if (!name.value.trim()) {
    alert("Please enter your name.");
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value.trim())) {
    alert("Please enter a valid email address.");
    return;
  }

  const phoneRegex = /^[\d+\-()\s]{7,20}$/;
  if (phone.value.trim() && !phoneRegex.test(phone.value.trim())) {
    alert("Please enter a valid phone number.");
    return;
  }

  if (!message.value.trim()) {
    alert("Please enter a message.");
    return;
  }

  console.log("Name:", name.value);
  console.log("Email:", email.value);
  console.log("Phone:", phone.value);
  console.log("Message:", message.value);

  try {
    const response = await mutateAsync({
      phone: phone.value,
      email: email.value,
      message: message.value,
    });
    console.log("Response:", response);
    alert("Form submitted!");
  } catch (error) {
    console.error(error);
    alert("Something went wrong.");
  }
}
</script>



<style scoped>
.contact-page-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 32px;
  padding-bottom: 32px;
}

.contact-header {
  font-size: clamp(1.5rem, 3vw, 2.5rem);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  color: var(--hero-headline-color);
}

.contact-page-wrapper form {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-div-wrapper {
  width: 50%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--button-background-border-color);
  border-radius: 16px;
}

.label-class {
  font-size: clamp(0.8rem, 2vw, 1.3rem);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  color: var(--hero-headline-color);
}

input {
  border-radius: 16px;
  min-height: 20px;
  min-width: 400px;
  padding: 8px;
  font-size: clamp(0.6rem, 2vw, 1rem);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  color: var(--hero-headline-color);
}

textarea {
  border-radius: 16px;
  min-height: 20px;
  width: 80%;
  min-height: 300px;
  padding: 8px;
  font-size: clamp(0.6rem, 2vw, 1rem);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  color: var(--hero-headline-color);
}

.submit-button-class {
  background-color: var(--button-background-color);
  color: var(--text-color);
  padding: 16px;
  font-size: clamp(0.8rem, 2vw, 1.3rem);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  border-radius: 16px;
  width: 60%;
}

.submit-button-div {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 16px;
}

.submit-button-class {
  background-color: var(--button-background-color-hover);
  cursor: pointer;
  box-shadow: 3px 3px 16px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease-in-out;

}

.submit-button-class:hover {
  transform: translateY(-4px)
}

.submit-button-class:active {
  transform: scale(1.05)
}

@media(max-width:900px) {

  .form-div-wrapper {
    width: 95%;
    border: none;
  }

  textarea {
    width: 80%;
    font-size: clamp(0.8rem, 2vw, 1rem);
    font-family: Arial, Helvetica, sans-serif;
    font-weight: 500;
  }

  input {
    min-width: auto;
    width: 90%;
  }

}
</style>