<script>
import MenuBar from '../components/MenuBar.vue'
import PageLoader from '../components/PageLoader.vue';
export default {
    components: {
        MenuBar,
        PageLoader
    },
    data() {
        return {
            isLoading: true
        }
    },
    created() {
        // setTimeout(() => {
        //     this.isLoading = false
        // }, 1500)
        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/');
        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                this.isLoading = false;
            } else {
                this.isLoading = true;
            }
        };
        xhr.send();
    }
}
</script>

<template>
    <PageLoader v-if="isLoading" />
    <div v-else>
        <div class="background">
            <MenuBar />
            <main>
                <h1>WETHAP</h1>
                <h2>Elevate your lab experience with WETHAP.</h2>
                <p>Soreppoi koto kaite mita. Demo jitsu ha tadano administrator gamen ni naru yotei.</p>
                <div class="link">
                    <RouterLink to="/api">
                        <span class="largeButton">
                            Try API
                        </span>
                    </RouterLink>
                </div>
            </main>
        </div>
    </div>
</template>

<style scoped>
.link {
    margin-top: 90px;
}

.largeButton {
    padding: 18px 30px;
    color: white;
    background: linear-gradient(to bottom right, #f09e41, #e6488f, #4ab1d0);
    background-size: 150% auto;
    border-radius: 8px;
    border: 2.5px solid transparent;
    border-color: #ffffff;
    font-size: 35px;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
    cursor: pointer;
    transition: 0.5s;
}

.largeButton:hover {
    background-position: right;
    border-color: #646cff;
}

main {
    padding: 5%;
}

h1 {
    font-size: 100px;
    font-family: Arial, sans-serif;
}

h2 {
    font-size: 40px;
    font-family: Arial, sans-serif;
    /* mix-blend-mode: difference;
    color: rgb(255, 255, 255); */

    color: #ACB6E5;
    background: -webkit-linear-gradient(0deg, #84c1ff, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

p {
    font-family: system-ui;
    color: rgba(255, 255, 255, 0.725);
}

.background {
    background-image: url('../assets/3Dlogo.gif');
    background-repeat: no-repeat;
    background-attachment: fixed;
    /* background-size: 1350px; */
    background-size: 75%;
    background-position: center;
    height: 100vh;

}

@media screen and (max-width: 450px) {
    h1 {
        font-size: 50px;
        font-family: Arial, sans-serif;
    }

    h2 {
        font-size: 20px;
        font-family: Arial, sans-serif;
        color: #ACB6E5;
        background: -webkit-linear-gradient(0deg, #84c1ff, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    p {
        font-size: 10px;
        font-family: system-ui;
        color: rgba(255, 255, 255, 0.725);
    }

    .link {
        margin-top: 45px;
    }

    .largeButton {
        padding: 9px 15px;
        color: white;
        background: linear-gradient(to bottom right, #f09e41, #e6488f, #4ab1d0);
        background-size: 150% auto;
        border-radius: 8px;
        border: 1.25px solid transparent;
        border-color: #ffffff;
        font-size: 20px;
        font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
        cursor: pointer;
        transition: 0.5s;
    }

}
</style>