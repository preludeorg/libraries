class Routes {
    constructor(host, account, token) {
        this.host = host;
        this.headers = {
            'account': account,
            'token': token,
            'content-type': 'application/json'
        }
    }
    async handleRoute(route, options, json=true) {
        options['headers'] = this.headers;
        const promise = fetch(route, options).catch(err => {
            console.error(`Error fetching ${route}: ${err}`);
            return {};
        });
        if (json) {
            return await promise.then(res => res.json());
        }
        return await promise;
    }
}

class ManifestRoutes extends Routes {
    constructor(creds) {
        super(creds.host, creds.account, creds.token);
    }
    async print() {
        return await this.handleRoute(`${this.host}/manifest`, {});
    }
    async get(id) {
        return await this.handleRoute(`${this.host}/manifest/${id}`, {});
    }
    async save(procedure) {
        const data = JSON.stringify(procedure);
        return await this.handleRoute(`${this.host}/manifest`, {method: 'PUT', body: data});
    }
    async delete(id) {
        return await this.handleRoute(`${this.host}/manifest/${id}`, {
            method: 'DELETE',
            body: JSON.stringify({}),
        }, false);
    }
}

class CodeRoutes extends Routes {
    constructor(creds) {
        super(creds.host, creds.account, creds.token);
    }
    async get(name) {
        return await this.handleRoute(`${this.host}/code/${name}`, {});
    }
    async save(name, code) {
        const data = JSON.stringify({code: code});
        return await this.handleRoute(`${this.host}/code/${name}`, {
            method: 'POST',
            body: data
        }, false);
    }
    async delete(name) {
        return await this.handleRoute(`${this.host}/dcf/${name}`, {method: 'DELETE'}, false);
    }
}

class IAMRoutes extends Routes {
    constructor(creds) {
        super(creds.host, creds.account, creds.token);
    }
    async register(email) {
        const data = {email: email};
        return await this.handleRoute(`${this.host}/account`, {method: 'POST', body: data}, true);
    }
}

let Service = {
    routes: {},
    credentials: () => {
        const host = localStorage.getItem('PRELUDE_SERVER');
        const account = localStorage.getItem('PRELUDE_ACCOUNT_ID');
        const token = localStorage.getItem('PRELUDE_ACCOUNT_TOKEN');
        return {
            host: host || 'https://detect.dev.prelude.org',
            account: account || '',
            token: token || ''
        };
    },
    setCredentials: (host, account, token) => {
        localStorage.setItem('PRELUDE_SERVER', host);
        localStorage.setItem('PRELUDE_ACCOUNT_ID', account);
        localStorage.setItem('PRELUDE_ACCOUNT_TOKEN', token);
        return Service.credentials();
    },
    login: (host, account, token, callback) => {
        const creds = Service.setCredentials(host, account, token);
        Service.routes.iam = new IAMRoutes(creds);
        Service.routes.manifest = new ManifestRoutes(creds);
        Service.routes.code = new CodeRoutes(creds);
        callback();
    }
};

export default Service;