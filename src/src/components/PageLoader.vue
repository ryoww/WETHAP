<template>
    <div class="loader">
        <div class="loadingItem">
            <!-- <img src="../assets/3Dlogo3.gif" width="250"> -->
            <img src="../assets/logo.png" width="250">
        </div>
    </div>
</template>

<style scoped>
.loader {
    position: fixed;
    top: 0; /* !?!?!? */
    left: 0; /* これすごいかも */
    width: 100%;
    height: 100%;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    background-color: #e7efff;
}
.loadingItem {
    color: black;
    position: absolute;
    top: 50%;
    left: 50%;
}
</style>