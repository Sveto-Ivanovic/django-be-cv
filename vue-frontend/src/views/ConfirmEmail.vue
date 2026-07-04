<template>
    <div class="root">  
    <div class="confirm-root">
        <div class="header">Congradulations !</div>
        <div class="icon">
            <n-icon size="40">
            <CheckMarkIcon></CheckMarkIcon>
            </n-icon>
        </div>
        <div class="text_1">
            We have sent verification email to <a :href="`mailto:{email}`">
                {{ email }}
            </a>
        </div>
        <div class="text_2">Please check email for further instructions.</div>

    </div>
 </div>
</template>


<script setup lang="ts">
import {
    CheckmarkDoneOutline as CheckMarkIcon
} from '@vicons/ionicons5'
import { useUserStore } from '../stores/user_store';
import { computed } from 'vue';

const userStore = useUserStore()
let email = computed(()=>{
    return userStore.email
})


</script>


<style scoped>
.root {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 64px;
}
.confirm-root{
    height: 400px;
    width: max(400px, 40%);
    box-shadow: 3px 3px 8px 8px rgba(0, 0, 0, 0.2);
    border: 2px solid gray;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 32px;
    background-color: var(--confirm-bg-color);
}

.header{
    font-size: 32px;
    font-weight: 700;
    letter-spacing: 0.01em;
    font-family: 'Times New Roman', Times, serif;

}

.icon{
    border-radius: 32px;
    background-color: rgb(113, 231, 113);
    padding: 5px 8px;
}

.text_1{
    font-weight: 600;
    font-size: 16px;
}

.text_1 a {
      text-decoration: none;
}

.text_2 {
    font-weight: 300;
    font-size: 14px;
}

</style>