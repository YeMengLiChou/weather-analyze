// 单例 axios 实例
const service = axios.create({
    baseURL: constants.baseUrl,
    timeout: 5000,
});


/**
 * get方法请求
 * @param {string} url
 * @param {object} data
 * @returns
 */
export function post(url, data) {
    return service({
        url,
        data,
        method: "post",
    });
}

/**
 * post方法请求
 * @param {string} url
 * @param {object} data
 * @returns
 */
export function get(url, params) {
    return service({
        url,
        params,
        method: "get",
    });
}

/**
 * delete方法请求
 * @param {string} url
 * @param {object} data
 * @returns
 */
export function del(url, data) {
    return service({
        url,
        data,
        method: "delete",
    });
}

export function put(url, data) {
    return service({
        url,
        data,
        method: "put",
    });
}

/**
 * 路径参数的delete方法请求
 * @param {*} url 
 * @param {*} data 
 * @returns 
 */
export function delParam(url, data) {
    return service({
        url, 
        params: data,
        method: 'delete'
    })
}

/**
 * 路径参数的put方法请求
 * @param {*} url 
 * @param {*} data 
 * @returns 
 */
export function putParam(url, data) {
    return service({
        url, 
        params: data,
        method: 'put'
    })
}

