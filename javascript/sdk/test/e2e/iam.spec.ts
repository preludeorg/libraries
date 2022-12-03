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

  it("gets an empty list of users for new account", async () => {
    const users = await service.iam.getUsers();
    expectTypeOf(users).toBeArray();
    expect(users.length).toEqual(0);
  });

  const userHandle = "test-user-admin";
  it("creates an admin user for the account", async () => {
    const user = await service.iam.createUser(Permissions.ADMIN, userHandle);

    expectTypeOf(user.token).toBeString();
  });

  it("gets list of the users containing the admin user", async () => {
    const users = await service.iam.getUsers();
    expectTypeOf(users).toBeArray();
    expect(users.length).toEqual(1);

    expect(users[0]).toEqual({
      handle: userHandle,
      permission: Permissions.ADMIN,
    });
  });

  it("deletes the admin user from account", async () => {
    const isDeleted = await service.iam.deleteUser(userHandle);
    expect(isDeleted).toEqual(true);
  });

  it("gets an empty user list after delete ", async () => {
    const users = await service.iam.getUsers();
    expectTypeOf(users).toBeArray();
    expect(users.length).toEqual(0);
  });

  it("updates the account token", async () => {
    const oldCreds = service.credentials!;
    const newToken = uuid.v4();
    await service.iam.updateToken(newToken);

    await expect(service.iam.getUsers()).rejects.toThrowError("Unauthorized");

    service.setCredentials({ ...oldCreds, token: newToken });

    expectTypeOf(await service.iam.getUsers()).toBeArray();
  });

  it("purges the account", async () => {
    const message = await service.iam.purgeAccount();
    expectTypeOf(message).toBeString();
  });
});
