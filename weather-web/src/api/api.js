import {get, post} from '@/api/api.js'


export default {
    fetchAllCities() {
        return get('/api/cities')
    }
}


