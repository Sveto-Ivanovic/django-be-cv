<template>
  <div v-if="isMobile === true" class="contact-page-wrapper">
    <form v-on:submit.prevent="submitForm">
      <div class="form-div-wrapper">
        <div class="contact-header">Contact us</div>
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

    <div class="contact-info-card">
      <div class="contact-info-title">Get in touch</div>

      <a
        v-if="contactInfo.email"
        class="contact-info-row"
        :href="`mailto:${contactInfo.email}`"
      >
        <span class="icon-wrapper" v-html="icons.email"></span>
        <span>{{ contactInfo.email }}</span>
      </a>

      <a
        v-if="contactInfo.phone"
        class="contact-info-row"
        :href="`tel:${contactInfo.phone}`"
      >
        <span class="icon-wrapper" v-html="icons.phone"></span>
        <span>{{ contactInfo.phone }}</span>
      </a>

      <a
        v-if="contactInfo.linkedin"
        class="contact-info-row"
        :href="contactInfo.linkedin"
        target="_blank"
        rel="noopener noreferrer"
      >
        <span class="icon-wrapper" v-html="icons.linkedin"></span>
        <span>LinkedIn</span>
      </a>
    </div>
  </div>

  <div v-else class="contact-page-wrapper-big-screen">
    <form class="form-class" v-on:submit.prevent="submitForm">
      <div class="form-div-wrapper">
        <div class="contact-header">Contact us</div>
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

    <div class="image-bg-clip">
      <img class="image-class" src="/contactus.jpg" alt="Contact Us" />
    </div>

    <div class="contact-info-panel">
      <div class="contact-info-card">
        <div class="contact-info-title">Get in touch</div>

        <a
          v-if="contactInfo.email"
          class="contact-info-row"
          :href="`mailto:${contactInfo.email}`"
        >
          <span class="icon-wrapper" v-html="icons.email"></span>
          <span>{{ contactInfo.email }}</span>
        </a>

        <a
          v-if="contactInfo.phone"
          class="contact-info-row"
          :href="`tel:${contactInfo.phone}`"
        >
          <span class="icon-wrapper" v-html="icons.phone"></span>
          <span>{{ contactInfo.phone }}</span>
        </a>

        <a
          v-if="contactInfo.linkedin"
          class="contact-info-row"
          :href="contactInfo.linkedin"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span class="icon-wrapper" v-html="icons.linkedin"></span>
          <span>LinkedIn</span>
        </a>
      </div>
    </div>
  </div>
</template>



<script setup lang="ts">
import { ref, watchEffect } from "vue";
import contactApi from '../services/contact'
import { useWindowSize } from "@vueuse/core";

const name = ref("");
const email = ref("");
const phone = ref("");
const message = ref("");
const { mutateAsync, isPending } = contactApi.useSendContactMessage()

const contactInfo = ref({
  email: "svetoivanovic788@gmail.com",
  phone: "+38267 243 849",
  linkedin: "https://www.linkedin.com/in/svetozar-ivanovi%C4%87-ab7261334/",
});

const icons = {
  email: `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v16H4z" opacity="0"/><path d="M22 6l-10 7L2 6"/><path d="M2 6h20v12H2z"/></svg>`,
  phone: `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>`,
  linkedin: `<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 1 1 0-4.124 2.062 2.062 0 0 1 0 4.124zM7.114 20.452H3.558V9h3.556v11.452z"/></svg>`,
};

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



  try {
    const response = await mutateAsync({
      phone: phone.value,
      email: email.value,
      message: message.value,
    });
    alert("Form submitted!");
  } catch (error) {
    console.error(error);
    alert("Something went wrong.");
  }
}

let isMobile = ref(false)
const { width, height } = useWindowSize()


watchEffect(() => {
  if (width.value < 1200) {
    isMobile.value = true
  } else {
    isMobile.value = false
  }
})
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

.form-class {
  width: 50%;
  display: flex;
  justify-content: center;
  align-items: stretch;
}

.contact-page-wrapper-big-screen {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: stretch;
  justify-content: center;
  gap: 48px;
  padding: 48px 24px;
}

.contact-header {
  font-size: clamp(1.5rem, 3vw, 2.5rem);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  color: var(--hero-headline-color);
  text-align: center;
}

.contact-page-wrapper form {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-div-wrapper {
  width: 80%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--button-background-border-color);
  box-shadow: 3px 3px 16px 4px rgba(0, 0, 0, 0.2);
  background-color: aliceblue;
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
  background-color: var(--button-background-color-hover);
  color: var(--text-color);
  padding: 16px;
  font-size: clamp(0.8rem, 2vw, 1.3rem);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  border-radius: 16px;
  width: 60%;
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

.submit-button-div {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 16px;
}

.image-bg-clip {
  position: fixed;
  top: 0;
  right: 0;
  width: 45%;
  height: 100vh;
  overflow: hidden;
  z-index: -1;
}

.image-class {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 30%;
  filter: blur(10px);
  transform: scale(1.1);
}

.contact-info-panel {
  position: relative;
  width: 40%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.contact-info-card {
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 32px;
  border-radius: 16px;
  background: linear-gradient(145deg, var(--button-background-color), var(--button-background-color-hover));
  box-shadow: 3px 3px 16px 4px rgba(0, 0, 0, 0.15);
}

.contact-info-title {
  font-size: clamp(1.2rem, 2.5vw, 1.6rem);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 4px;
}

.contact-info-row {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  color: var(--text-color);
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 600;
  font-size: clamp(0.85rem, 2vw, 1.05rem);
  padding: 12px 14px;
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.15);
  transition: transform 0.2s ease-in-out, background-color 0.2s ease-in-out;
  word-break: break-word;
}

.contact-info-row:hover {
  transform: translateX(4px);
  background-color: rgba(255, 255, 255, 0.28);
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Mobile version of the card, stacked below the form */
.contact-page-wrapper .contact-info-card {
  width: 90%;
  max-width: 500px;
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

@media(max-width:1400px) {
  .contact-page-wrapper-big-screen {
    flex-direction: column;
  }

  .form-class,
  .contact-info-panel {
    width: 90%;
  }
}
</style>