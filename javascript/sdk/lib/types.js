/**
 * Represents authentication credentials.
 *
 * @interface Credentials
 * @property {string} account - The account name.
 * @property {string} token - The account token.
 */

/**
 * @callback RequestInterceptor
 * @param {Request} request - The original request object.
 * @returns {Request} The modified request object.
 */

/**
 * Represents the configuration for the service.
 *
 * @interface ServiceConfig
 * @property {string} host - The host for the service.
 * @property {Credentials} [credentials] - Optional authentication credentials.
 * @property {RequestInterceptor} [requestInterceptor] - Function to modify the request before sending.
 */

/**
 * Represents request options excluding "method" and "body" properties.
 *
 * @typedef {Omit<RequestInit, "method" | "body">} RequestOptions
 */

/**
 * Represents a Test.
 *
 * @interface Test
 * @property {string} account_id
 * @property {string} id
 * @property {string} name
 * @property {string} unit
 * @property {string[]} techniques
 * @property {string} advisory
 */

/**
 * Represents a User.
 *
 * @interface User
 * @property {string} handle - The user's handle (email).
 * @property {Permission} permission - The user's permission level.
 * @property {string} expires - The expiration date of the user's account.
 * @property {string} name - The name of the user.
 */

/**
 * Represents an Account.
 *
 * @interface Account
 * @property {string} account_id - The account ID.
 * @property {string} whoami
 * @property {string[]} controls - The EDR partners associated with the account.
 * @property {User[]} users - The users associated with the account.
 * @property {Mode} mode - The mode of the account.
 * @property {Queue[]} queue - The queue associated with the account.
 * @property {string} company - The company associated with the account.
 */

/**
 * Represents the parameters for creating an account.
 *
 * @interface CreateAccountParams
 * @property {string} email - The email for the account.
 * @property {string} [name] - Optional name for the account.
 * @property {string} [company] - Optional company for the account.
 */

/**
 * Represents the parameters for creating a users.
 */
