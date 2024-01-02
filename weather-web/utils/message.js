import { ElMessage } from "element-plus";

const defaultDuration = 2500;

function error(message, duration) {
    if (!duration) {
        duration = defaultDuration
    }
    ElMessage({
        message: message,
        type: 'error',
        duration: duration
    });
}

function info(message, duration) {
    if (!duration) {
        duration = defaultDuration
    }
    ElMessage({
        message: message,
        type: 'info',
        duration: duration
    });
}

function warn(message, duration) {
    if (!duration) {
        duration = defaultDuration
    }
    ElMessage({
        message: message,
        type: 'warning',
        duration: duration
    });
}

function success(message, duration) {
    if (!duration) {
        duration = defaultDuration
    }
    ElMessage({
        message: message,
        type: 'success',
        duration: duration
    });
}

export default {
    success,
    warn,
    error,
    info
};
