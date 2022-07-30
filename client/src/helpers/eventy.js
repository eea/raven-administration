import mitt from 'mitt';
const emitter = mitt();

const Eventy = {
    showProgress: () => {
        emitter.emit('showProgress');
    },
    hideProgress: (ms = 500) => {
        setTimeout(() => emitter.emit('hideProgress'), ms);
    },
    failProgress: (s) => {
        emitter.emit('failProgress', s);
        Eventy.hideProgress(1000)
    },
    showMessage: (title, msg, type) => {
        emitter.emit('showMessage', { title, msg, type });
    },
    hideMessage: (ms = 0) => {
        setTimeout(() => emitter.emit('hideMessage'), ms);
    },
    showHideMessage: (title, msg, type, duration = 5000) => {
        emitter.emit('showMessage', { title, msg, type });
        Eventy.hideMessage(duration);
    },
    listen: (e, f) => {
        emitter.on(e, f);
    },
    emit: (e, f) => {
        emitter.emit(e, f);
    }

};
export default Eventy;
