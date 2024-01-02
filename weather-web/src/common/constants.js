
// 配置信息
const CONFIG = {
    development: {
        baseUrl: 'http://localhost:8080',
      },
      production: {
        baseUrl: 'https://121.37.9.218:8080',
      }
}

export default CONFIG[process.env.NODE_ENV];
