import click

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.iam_controller import (
    IAMAccountController,
    IAMUserController,
)
from prelude_sdk.models.codes import Mode, Permission


@click.group()
@click.pass_context
def iam(ctx):
    """Prelude account management"""
    ctx.obj = IAMAccountController(account=ctx.obj)


@iam.command("account")
@click.pass_obj
@pretty_print
def describe_account(controller):
    """Get account details"""
    with Spinner(description="Fetching account details"):
        return controller.get_account()


@iam.command("purge-account")
@click.confirmation_option(prompt="Are you sure?")
@click.pass_obj
@pretty_print
def purge_account(controller):
    """Delete your account"""
    with Spinner(description="Purging account from existence"):
        return controller.purge_account()


@iam.command("update-account")
@click.option(
    "-m",
    "--mode",
    help="provide a mode",
    default=None,
    show_default=False,
    type=click.Choice([m.name for m in Mode], case_sensitive=False),
)
@click.option(
    "-c",
    "--company",
    help="provide your associated company",
    default=None,
    show_default=False,
    type=str,
)
@click.option(
    "-s",
    "--slug",
    help="provide a unique human-readable identifier for your account",
    default=None,
    show_default=False,
    type=str,
)
@click.pass_obj
@pretty_print
def update_account(controller, mode, company, slug):
    """Update an account"""
    with Spinner(description="Updating account information"):
        return controller.update_account(
            mode=Mode[mode] if mode else None, company=company, slug=slug
        )


@iam.command("attach-oidc")
@click.argument(
    "issuer", type=click.Choice(["google", "azure", "okta"], case_sensitive=False)
)
@click.option("--client_id", required=True, help="Client ID")
@click.option("--client_secret", required=True, help="Client secret")
@click.option("--oidc_config_url", required=True, help="Configuration endpoint")
@click.pass_obj
@pretty_print
def attach_oidc(controller, issuer, client_id, client_secret, oidc_config_url):
    """Attach OIDC to an account"""
    with Spinner(description="Attaching OIDC"):
        return controller.attach_oidc(
            client_id=client_id,
            client_secret=client_secret,
            issuer=issuer,
            oidc_url=oidc_config_url,
        )


@iam.command("detach-oidc")
@click.confirmation_option(prompt="Are you sure?")
@click.pass_obj
@pretty_print
def detach_oidc(controller):
    """Detach OIDC to an account"""
    with Spinner(description="Detaching OIDC"):
        return controller.detach_oidc()


@iam.command("invite-user")
@click.option(
    "-p",
    "--permission",
    help="user permission level",
    default=Permission.EXECUTIVE.name,
    type=click.Choice(
        [
            p.name
            for p in Permission
            if p not in [Permission.INVALID, Permission.SERVICE, Permission.SUPPORT]
        ],
        case_sensitive=False,
    ),
    show_default=True,
)
@click.option(
    "-n", "--name", help="name of user", default=None, show_default=False, type=str
)
@click.option(
    "-o",
    "--oidc",
    help="OIDC app name, or 'none' to login via a password",
    required=True,
    type=str,
)
@click.argument("email")
@click.pass_obj
@pretty_print
def invite_user(controller, permission, name, oidc, email):
    """Invite a new user to your account"""
    with Spinner(description="Inviting new user"):
        data = controller.invite_user(
            email=email,
            oidc="" if oidc.lower() == "none" else oidc,
            permission=Permission[permission],
            name=name,
        )
    msg = "New non-oidc users must check their email to get their temporary password"
    return data, msg


@iam.command("create-service-user")
@click.argument("name")
@click.pass_obj
@pretty_print
def create_service_user(controller, name):
    """Create a new service user in your account"""
    with Spinner(description="Creating new service user"):
        return controller.create_service_user(name=name)


@iam.command("delete-service-user")
@click.argument("handle")
@click.pass_obj
@pretty_print
def delete_service_user(controller, handle):
    """Delete a service user from all accounts"""
    with Spinner(description="Deleting service user"):
        return controller.delete_service_user(handle=handle)


@iam.command("update-account-user")
@click.option(
    "-p",
    "--permission",
    help="user permission level",
    default=Permission.EXECUTIVE.name,
    type=click.Choice(
        [
            p.name
            for p in Permission
            if p not in [Permission.INVALID, Permission.SERVICE, Permission.SUPPORT]
        ],
        case_sensitive=False,
    ),
    show_default=True,
)
@click.option(
    "-o",
    "--oidc",
    help="OIDC app name, or 'none' for non-OIDC users",
    required=True,
    type=str,
)
@click.argument("email")
@click.pass_obj
@pretty_print
def update_account_user(controller, permission, oidc, email):
    """Update a user in your account"""
    with Spinner(description="Updating account user"):
        return controller.update_account_user(
            email=email,
            oidc="" if oidc.lower() == "none" else oidc,
            permission=Permission[permission],
        )


@iam.command("remove-user")
@click.confirmation_option(prompt="Are you sure?")
@click.option(
    "-o",
    "--oidc",
    help="OIDC app name, or 'none' for non-OIDC users",
    required=True,
    type=str,
)
@click.argument("email")
@click.pass_obj
@pretty_print
def remove_user(controller, oidc, email):
    """Remove a user from your account"""
    with Spinner(description="Removing user"):
        return controller.remove_user(
            email=email, oidc="" if oidc.lower() == "none" else oidc
        )


@iam.command("logs")
@click.option(
    "-d", "--days", help="days back to search from today", default=7, type=int
)
@click.option(
    "-l", "--limit", help="limit the number of results", default=1000, type=int
)
@click.pass_obj
@pretty_print
def logs(controller, days, limit):
    """Get audit logs"""
    with Spinner(description="Fetching logs"):
        return controller.audit_logs(days=days, limit=limit)


@iam.command("sign-up", hidden=True)
@click.option("-c", "--company", type=str, required=True)
@click.option("-n", "--name", type=str, required=True)
@click.argument("email", type=str, required=True)
@click.pass_obj
@pretty_print
def sign_up(controller, company, name, email):
    """(NOT AVAIABLE IN PRODUCTION) Create a new user and account"""
    with Spinner(description="Creating new user and account"):
        return controller.sign_up(company=company, email=email, name=name)


@click.group()
@click.pass_context
def user(ctx):
    """Prelude user management"""
    ctx.obj = IAMUserController(account=ctx.obj.account)


@user.command("accounts")
@click.pass_obj
@pretty_print
def list_accounts(controller):
    """List all accounts for your user"""
    with Spinner(description="Fetching all accounts for your user"):
        return controller.list_accounts()


@user.command("purge-user")
@click.confirmation_option(prompt="Are you sure?")
@click.pass_obj
@pretty_print
def purge_user(controller):
    """Remove your user from all accounts and purge user data"""
    with Spinner(description="Purging user"):
        return controller.purge_user()


@user.command("update-user")
@click.option("-n", "--name", help="name of user", type=str)
@click.pass_obj
@pretty_print
def update_user(controller, name):
    """Update your user information"""
    with Spinner(description="Updating user"):
        return controller.update_user(name=name)


@user.command("forgot-password")
@click.pass_obj
@pretty_print
def forgot_password(controller):
    """Send a password reset email"""
    with Spinner(description="Sending password reset email"):
        return (
            controller.forgot_password(),
            "Please check your email for a confirmation code",
        )


@user.command("confirm-forgot-password")
@click.option("-c", "--code", help="confirmation code", required=True)
@click.option(
    "-n",
    "--new_password",
    help="new password",
    required=True,
    hide_input=True,
    prompt=True,
)
@click.option(
    "-r",
    "--confirm_new_password",
    help="confirm new password",
    required=True,
    hide_input=True,
    prompt=True,
)
@click.pass_obj
@pretty_print
def confirm_forgot_password(controller, code, new_password, confirm_new_password):
    """Change your password using a confirmation code"""
    if new_password != confirm_new_password:
        raise ValueError("New password and confirmation do not match")
    with Spinner(description="Changing password"):
        return (
            controller.confirm_forgot_password(
                confirmation_code=code, new_password=new_password
            ),
            "Password changed successfully",
        )


@user.command("change-password")
@click.option(
    "-c",
    "--current_password",
    help="current password",
    required=True,
    hide_input=True,
    prompt=True,
)
@click.option(
    "-n",
    "--new_password",
    help="new password",
    required=True,
    hide_input=True,
    prompt=True,
)
@click.option(
    "-r",
    "--confirm_new_password",
    help="confirm new password",
    required=True,
    hide_input=True,
    prompt=True,
)
@click.pass_obj
@pretty_print
def change_password(controller, current_password, new_password, confirm_new_password):
    """Change your password"""
    if new_password != confirm_new_password:
        raise ValueError("New password and confirmation do not match")
    with Spinner(description="Changing password"):
        return (
            controller.change_password(
                current_password=current_password, new_password=new_password
            ),
            "Password changed successfully",
        )


iam.add_command(user)
