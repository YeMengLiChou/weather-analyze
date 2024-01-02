import {get, post} from '@/utils/request'


export default {
    fetchAllCities() {
        return get('/api/cities')
    },
    getRealDataByCityId(id) {
        return get('/api/real/' + id)
    },
    getHistoryDataByCityId(id, year, month) {
        return get('/api/history/', {
            city_id: id,
            month,
            year
        })
    },
    getCityNameById(id) {
        return get('/api/cityname/'+id)
    }
}


