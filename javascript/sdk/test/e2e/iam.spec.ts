import * as uuid from "uuid";
import { describe, expect, expectTypeOf, it } from "vitest";
import { Permissions, Service } from "../../lib/main";

const serviceURL = import.meta.env.VITE_PRELUDE_SERVICE_URL;

describe("iam", () => {
  let service = new Service({ host: serviceURL });

  it("creates a new account", async () => {
    const credentials = await service.iam.newAccount("internal-test-iam");
    expectTypeOf(credentials.account).toBeString();
    expectTypeOf(credentials.token).toBeString();
    service.setCredentials(credentials);
  });

  it("gets a list of users for new account", async () => {
    const users = await service.iam.getUsers();
    expectTypeOf(users).toBeArray();
    expect(users.length).toEqual(1);
  });

  const userHandle = "test-user-admin";
  let userToken = "";
  it("creates an admin user for the account", async () => {
    const user = await service.iam.createUser(Permissions.ADMIN, userHandle);

    expectTypeOf(user.token).toBeString();
    userToken = user.token;
  });

  it("gets list of the users containing the admin user", async () => {
    const users = await service.iam.getUsers();
    expectTypeOf(users).toBeArray();
    expect(users.length).toEqual(2);

    expect(users[1]).toEqual({
      handle: userHandle,
      permission: Permissions.ADMIN,
    });
  });

  it("deletes the admin user from account", async () => {
    const isDeleted = await service.iam.deleteUser(userHandle);
    expect(isDeleted).toEqual(true);
  });

  it("gets user list after delete", async () => {
    const users = await service.iam.getUsers();
    expectTypeOf(users).toBeArray();
    expect(users.length).toEqual(1);
  });

  it("purges the account", async () => {
    const message = await service.iam.purgeAccount();
    expectTypeOf(message).toBeString();
  });
});
