<script>
import axios from 'axios';
import MenuBar from '../components/MenuBar.vue'
import PageLoader from '../components/PageLoader.vue';
export default {
    components: {
        MenuBar,
        PageLoader
    },
    data() {
        return {
            isLoading: true,
            searchFilter: {
                location: '',
                date: '',
                time: '',
                weather: ''
            },
            items: [],
            rooms: [],
            sortBy: 1,
            ascending: false,
            exportString: '場所, 日付, 時限, 気温, 湿度, 気圧, 天気\n'
        }
    },
    computed: {
        filteredItems() {
            let filteredItems = []
            let ascending = this.ascending
            let sortBy = this.sortBy
            filteredItems = this.items.filter(item => {
                if (this.searchFilter.location && item[0] !== this.searchFilter.location) {
                    return false
                }
                if (this.searchFilter.date && item[1] !== this.searchFilter.date) {
                    return false
                }
                if (this.searchFilter.time && item[2] !== Number(this.searchFilter.time)) {
                    return false
                }
                if (this.searchFilter.weather && item[6] !== this.searchFilter.weather) {
                    return false
                }
                return true
            })
            filteredItems = filteredItems.sort(function (a, b) {
                if (sortBy === 1) {
                    return (ascending ? (a[1] < b[1] ? -1 : 1) : (a[1] > b[1] ? -1 : 1))
                } else {
                    return (ascending ? (a[sortBy] - b[sortBy]) : (b[sortBy] - a[sortBy]));
                }
            });

            return filteredItems;
        },

    },
    methods: {
        fetchAllData() {
            // axios.get('https://192.168.3.2/previewData')
            //     .then(response => {
            //         this.items = response.data;
            //         this.isLoading = false
            //     })
            //     .catch(error => {
            //         console.log(error);
            //     });
            axios.get('https://solithv7247.duckdns.org/WETHAP/api/previewData')
                .then(response => {
                    this.items = response.data;
                    this.isLoading = false
                })
                .catch(error => {
                    console.log(error);
                });
            // axios.get('https://192.168.3.2/registeredRooms')
            //     .then(response => {
            //         this.rooms = response.data;
            //         this.isLoading = false
            //     })
            //     .catch(error => {
            //         console.log(error);
            //     });
            axios.get('https://solithv7247.duckdns.org/WETHAP/api/registeredRooms')
                .then(response => {
                    this.rooms = response.data;
                    this.isLoading = false
                })
                .catch(error => {
                    console.log(error);
                });
        },
        exportCSV() {
            for (let i = 0; i < this.filteredItems.length; i++) {
                for (let j = 0; j < 7; j++) {
                    if (j === 6) {
                        this.exportString += this.filteredItems[i][j] + '\n'
                    } else {
                        this.exportString += this.filteredItems[i][j] + ', '
                    }
                }
            }
            const blob = new Blob([this.exportString], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "data.csv";
            link.click();
            URL.revokeObjectURL(url);
        }
    },
    mounted() {
        this.fetchAllData()
    }
}
</script>

<template>
    <MenuBar />
    <main>
        <h1>全データから検索する</h1>
        <div v-if="isLoading">
            <h2>取得中...</h2>
        </div>
        <div class="container" v-else>
            <div class="left-column">
                <table>
                    <thead>
                        <tr class="head">
                            <th>場所</th>
                            <th>日付</th>
                            <th>時限</th>
                            <th>気温</th>
                            <th>湿度</th>
                            <th>気圧</th>
                            <th>天気</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in filteredItems">
                            <td v-for="value in item">{{ value }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="right-column">
                <h2>条件</h2>
                <div>
                    場所: <br><input type="text" v-model="searchFilter.location" list="rooms">
                    <datalist id="rooms">
                        <option v-for="room in rooms">{{ room }}</option>
                    </datalist>
                </div>
                <div>
                    日付: <br><input type="date" v-model="searchFilter.date">
                </div>
                <div>
                    時限: <br><input type="text" v-model="searchFilter.time">
                </div>
                <div>
                    天気: <br><input type="text" v-model="searchFilter.weather">
                </div>
                <br>
                <div>
                    <select v-model="sortBy">
                        <option value="1">日付</option>
                        <option value="2">時限</option>
                        <option value="3">気温</option>
                        <option value="4">湿度</option>
                        <option value="5">気圧</option>
                    </select>
                    で
                    <button @click="ascending = true" class="sortButton">昇順</button>
                    <button @click="ascending = false" class="sortButton">降順</button>
                </div>
                <br>
                <br>
                <br>
                <div>
                    <button @click="fetchAllData" class="button">更新</button>
                </div>
                <div>
                    <button @click="exportCSV" class="button">CSVにエクスポート</button>
                </div>
            </div>
        </div>
    </main>
</template>

<style scoped>
.container {
    display: flex;
    flex-direction: row;
}

.left-column {
    flex: 70%;
}

.right-column {
    flex: 30%;
    flex-direction: column;
}

.head {
    background-color: #646cff;
}

.sortButton {
    width: 18%;
    margin-bottom: 2.5%;
    margin-left: 2%;
    padding: 5px 10px;
    color: #11244a;
    background-color: #e1e1e1;
    border-radius: 8px;
    border: 2.5px solid transparent;
    border-color: white;
    font-size: 18px;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
    cursor: pointer;
    transition: 0.25s;
}

.sortButton:hover {
    color: #646cff;
    background-color: white;
    border-color: #646cff;
}

.button {
    width: 75%;
    margin-bottom: 2.5%;
    padding: 5px 10px;
    color: white;
    background-color: #6c7bff;
    border-radius: 8px;
    border: 2.5px solid transparent;
    border-color: white;
    font-size: 20px;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
    cursor: pointer;
    transition: 0.25s;
}

.button:hover {
    color: #646cff;
    background-color: white;
    border-color: #646cff;
}

select {
    font-size: 20px;
}

input {
    width: 68%;
    height: 1.5em;
    margin-bottom: 2.5%;
    padding: 5px 10px;
    border-radius: 8px;
    border: 2.5px solid transparent;
    border-color: rgb(255, 255, 255);
    font-size: 20px;
    font-family: Arial, Helvetica, sans-serif;
    background-color: #e1e1e1;
    transition: 0.5s;
}

table {
    width: 90%;
    text-align: center;
    border-collapse: collapse;
}

tr:nth-child(even) {
    background: #162d5c;
}

td {
    padding: 10px;
    border-bottom: solid 1px #748ca5;
}

@media screen and (max-width: 450px) {
    h1 {
        font-size: 25px;
    }

    h2 {
        font-size: 20px;
    }

    .container {
        /* display: flex; */
        flex-direction: column-reverse;
    }

    input {
        width: 75%;
        height: 1.5em;
        /* text-align: center; */
        margin-bottom: 2.5%;
        padding: 5px 10px;
        border-radius: 8px;
        border: 2.5px solid transparent;
        border-color: rgb(255, 255, 255);
        font-size: 20px;
        font-family: Arial, Helvetica, sans-serif;
        background-color: #e1e1e1;
        transition: 0.5s;
    }

    table {
        width: 90%;
        text-align: center;
        font-size: 10px;
        border-collapse: collapse;
    }

    tr:nth-child(even) {
        background: #162d5c;
    }

    td {
        padding: 10px;
        border-bottom: solid 1px #748ca5;
    }
}
</style>
