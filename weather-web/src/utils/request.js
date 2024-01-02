import axios from "axios";
import msg from "@/utils/message";
import constants from "@/common/constants";

// 单例 axios 实例
const service = axios.create({
    timeout: 5000,
});



// 响应拦截器
service.interceptors.response.use(
    (response) => {
        // 文件下载
        if (response.config.responseType === "blob") {
            return response;
        }
    
        const res = response.data;
        // debug
        console.log(response.config.url, response.statusCode, response.data);

        // 响应码不是 200
        if (res.code !== 200) {
            msg.error(res.msg, 2500)
        } else {
            return res.data;
        }
    },
    (error) => {
        console.log("err" + error); // for debug
        msg.error(error.message, 5000);
        return Promise.reject(error);
    }
);

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

