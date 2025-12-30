from discord import app_commands


# -------------------------
# CUSTOM ERRORS
# -------------------------
class NotOwnerError(app_commands.AppCommandError):
    """Raised when a user tries to run an owner-only command."""
    pass

class NotAdminError(app_commands.AppCommandError):
    """Raised when a user tries to run an admin-only command."""
    pass
