<template>
    <div class="header">
        <RouterLink to="/"><img src="../assets/banner2.png"></RouterLink>
        <nav>
            <RouterLink to="/" class="nav-link">Home</RouterLink>
            <RouterLink to="about" class="nav-link">About</RouterLink>
            <RouterLink to="/" class="nav-link">Contact</RouterLink>
            <div class="nav-link">
                <RouterLink to="/api" class="nav-link">
                    <span class="tryButton">
                        Try&nbsp;API
                    </span>
                </RouterLink>
            </div>
        </nav>
    </div>
</template>

<style scoped>
img {
    width: 200px;
}

.tryButton {
    height: 50px;
    padding: 10px 20px;
    color: rgb(255, 255, 255);
    margin-top: 10px;
    border-radius: 8px;
    border: 1px solid transparent;
    border-color: #ffffff;
    font-size: 20px;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
    cursor: pointer;
    transition: 0.25s;
}

.tryButton:hover {
    border-color: #646cff;
}


.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 80px;
}

nav {
    display: flex;
    justify-content: flex-end;
    height: 25px;
}

.nav-link {
    text-align: center;
    text-decoration: none;
    color: #ffffff;
    margin-right: 50%;
    vertical-align: middle;
    transition: 0.25s;
}

.nav-link:last-child {
    margin-right: 0;
}

.nav-link:hover {
    color: #919191;
}

@media screen and (max-width: 400px) {
    img {
        width: 100px;
    }
    
    nav {
        height: auto;
    }

    .tryButton {
        /* height: 50px; */
        padding: 3px 7px;
        color: rgb(255, 255, 255);
        /* margin-top: 10px; */
        border-radius: 5px;
        border: 1px solid transparent;
        border-color: #ffffff;
        font-size: 10px;
        font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
        cursor: pointer;
        transition: 0.25s;
    }

    .nav-link {
        text-align: center;
        text-decoration: none;
        color: #ffffff;
        font-size: 60%;
        font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
        margin-right: 12%;
        vertical-align: middle;
        transition: 0.25s;
    }
}
</style>