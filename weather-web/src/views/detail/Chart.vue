<script setup>
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
// import 'echarts/theme/macarons'
// import resize from './mixins/resize'

const props = defineProps({
    className: {
        type: String,
        default: 'chart'
    },
    width: {
        type: String,
        default: '100%'
    },
    height: {
        type: String,
        default: '600px'
    },
    chartData: {
        type: Object,
        default: () => ({})
    }
})

const chartRef = ref(null)
const chart = ref(null)

onMounted(() => {
    if (chartRef.value) {
        initChart();
    }
});

onBeforeUnmount(() => {
    if (chart.value) {
        chart.value.dispose()
        chart.value = null
    }
})

watch(
    () => props.chartData,
    (val) => {
        if (chart.value && val && val !== null) {
            setOptions(val)
            console.log(val);
        }
    },
    { deep: true }
)

const initChart = () => {
    chart.value = echarts.init(chartRef.value)
    if (!props.chartData && props.chartData === null) return
    setOptions(props.chartData)
}

const setOptions = (data) => {
    const upColor = '#00da3c';
    const downColor = '#ec0000';
    const xdata = []
    const aqi = []
    const hight_temp = []
    const low_temp = []
    const wind_level = []
    
    const len = data.length
    for (let i = 0; i < len; i ++) {
        const item = data[i]
        xdata.push(item.timestamp)
        hight_temp.push(item.high_temp)
        low_temp.push(item.low_temp)
        wind_level.push(parseInt(item.w_level))
        aqi.push(item.aqi)
    }
    const options = {
        title: {
            text: '历史数据',
            left: 'center'
        },
        animation: false,
        // 数据类型
        legend: {
            bottom: 10,
            left: 'center',
            data: ['空气质量指数', '最高温度', '最低温度', '空气质量', '风级']
        },
        // 信息框
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross', // 坐标线交叉显示
            },
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 10,
            textStyle: {
                color: '#000'
            },
            // position: function (pos, params, el, elRect, size) {
            //     const obj = {
            //         top: 10
            //     };
            //     obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
            //     return obj;
            // }
        },
        // 全局坐标指示器
        axisPointer: {
            link: [{
                xAxisIndex: 'all'
            }],
            label: {
                backgroundColor: '#777'
            }
        },
        // 工具栏
        toolbox: {
            feature: {
                dataZoom: {
                    yAxisIndex: false
                },
                brush: {
                    type: ['lineX', 'clear']
                }
            }
        },

        brush: {
            xAxisIndex: 'all',
            brushLink: 'all',
            outOfBrush: {
                colorAlpha: 0.1
            }
        },

        // 坐标映射
        visualMap: {
          show: false,
          seriesIndex: 5,
          dimension: 2,
          pieces: [
            {
              value: 0,
              color: downColor
            },
            {
              value: 0,
              color: upColor
            }
          ]
        },

        grid: [
            {
                left: '10%',
                right: '8%',
                height: '50%'
            },
            {
                left: '10%',
                right: '8%',
                top: '63%',
                height: '16%'
            }
        ],
        // 横坐标
        xAxis: [
            {
                type: 'category',
                data: xdata,
                boundaryGap: false,
                axisLine: { onZero: false },
                splitLine: { show: false },
                min: 'dataMin',
                max: 'dataMax',
                axisPointer: {
                    z: 100
                }
            },
            {
                type: 'category',
                gridIndex: 1,
                data: xdata,
                boundaryGap: false,
                axisLine: { onZero: false },
                axisTick: { show: false },
                splitLine: { show: false },
                axisLabel: { show: false },
                min: 'dataMin',
                max: 'dataMax'
            }
        ],
        // 纵坐标
        yAxis: [
            {
                name: '温度',
                scale: true,
                splitArea: {
                    show: true
                }
            },
            {
                name: '风速',
                scale: true,
                gridIndex: 1,
                splitNumber: 2,
                axisLabel: { show: false },
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { show: false }
            },
            {
                name: '空气质量指数',
                scale: true,
                splitArea: {
                    show: true
                }
            }
        ],
        // 下方缩放轴
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: [0, 1],
                start: 0,
                end: 100
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                top: '85%',
                start: 98,
                end: 100
            }
        ],
        series: [
            {
                name: '空气质量指数',
                type: 'line',
                data: aqi,
                itemStyle: {
                    color: upColor,
                    color0: downColor,
                    borderColor: undefined,
                    borderColor0: undefined
                },
                yAxisIndex: 2,
                xAxisIndex: 0,
                
            },
            {
                name: '最高温度',
                type: 'line',
                data: hight_temp,
                smooth: true,
                lineStyle: {
                    opacity: 0.5
                },
                
            },
            {
                name: '最低温度',
                type: 'line',
                // yAxisIndex: 1,
                // xAxisIndex: 1,
                data: low_temp,
                smooth: true,
                lineStyle: {
                    opacity: 0.5
                }
            },
            {
                name: '风级',
                type: 'line',
                yAxisIndex: 1,
                xAxisIndex: 1,
                data: wind_level,
                smooth: true,
                lineStyle: {
                    opacity: 0.5
                }
            },
            // {
            //     name: 'rate',
            //     type: 'bar',
            //     xAxisIndex: 1,
            //     yAxisIndex: 1,
            //     data: rateData,
            // },
            // {
            //     name: 'time',
            //     data: timeData,
            //     xAxisIndex: 1,
            //     yAxisIndex: 1,
            //     show: false
            // }
        ]
    };

    chart.value.setOption(options, true)

    chart.value.dispatchAction({
        type: 'brush',
        areas: [
            {
                brushType: 'lineX',
                coordRange: ['2016-6-2', '2016-6-20'],
                xAxisIndex: 0
            }
        ]
    });

    const unwrap = (obj) => obj && (obj.__v_raw || obj.valueOf() || obj)
    unwrap(chart.value).setOption(options, true)
}
</script>

<template>
    <div :class="className" ref="chartRef" :style="{ height: props.height, width: props.width }" />
</template>

<style scoped></style>