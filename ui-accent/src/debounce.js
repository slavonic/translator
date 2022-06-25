

export class Debounce {
    constructor(engine) {
        this.engine = engine;
        this.pending = [];
        this.idle = new EventDispatcher();
        this.call = this.call.bind(this);
    }

    async call() {
        this.pending.push(arguments);
        if (this.pending.length === 1) {
            this.idle.dispatchEvent({ idle: false });
            while (this.pending.length > 0) {
                if (this.pending.length > 1) {
                    this.pending.splice(0, this.pending.length - 1);
                }
                try {
                    await this.engine.apply(null, this.pending[0]);
                } finally {
                    this.pending.splice(0, 1);
                }
            }
            this.idle.dispatchEvent({ idle: true });
        }
    }

    addIdleStateListener(listener) {
        return this.idle.addEventListener(listener);
    }
}

class EventDispatcher {
    constructor() {
        this.id = 0;
        this.listeners = {};
    }

    addEventListener(listener) {
        this.id += 1;
        const listenerId = '' + this.id;
        this.listeners[listenerId] = listener;
        return () => {
            delete this.listeners[listenerId];
        }
    }

    dispatchEvent(event) {
        for (const key of Object.keys(this.listeners)) {
            try {
                this.listeners[key](event);
            } catch (err) {
                console.error(err);
            }
        }
    }
}
