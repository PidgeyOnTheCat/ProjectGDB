import discord
from discord.ext import commands
from aiohttp import web
import asyncio
import secrets
from colorama import Fore as f

from BotExtensions.functions import Functions 

# -------------------------
# CONFIGURATION
# -------------------------
WEB_PORT = 7420
USERNAME = "admin"
PASSWORD = "password"

# -------------------------
# HTML TEMPLATES
# -------------------------
CSS = """
<style>
    body { background-color: #2c2f33; color: #ffffff; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .container { background-color: #23272a; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 500px; }
    h1 { text-align: center; color: #7289da; }
    input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin: 10px 0; background: #2c2f33; border: 1px solid #7289da; color: white; border-radius: 4px; box-sizing: border-box; }
    button { width: 100%; padding: 10px; background-color: #7289da; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s; }
    button:hover { background-color: #5b6eae; }
    .btn-red { background-color: #f04747; margin-top: 20px; }
    .btn-red:hover { background-color: #d03030; }
    .logs { background: #000; color: #0f0; padding: 10px; height: 300px; overflow-y: scroll; font-family: 'Consolas', monospace; font-size: 12px; border-radius: 4px; margin-top: 20px; border: 1px solid #444; display: flex; flex-direction: column-reverse; }
    .log-line { border-bottom: 1px solid #222; padding: 2px 0; white-space: pre-wrap; }
    a { color: #7289da; text-decoration: none; display: block; text-align: center; margin-top: 15px; }
</style>
"""

LOGIN_HTML = f"""
<!DOCTYPE html>
<html>
<head><title>Bot Login</title>{CSS}</head>
<body>
    <div class="container">
        <h1>Bot Control Panel</h1>
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

def render_dashboard(bot_name):
    # READ LOGS FROM FUNCTIONS CLASS
    current_logs = list(Functions.web_logs)
    
    # Format them for HTML
    log_html = "".join([f"<div class='log-line'>{line}</div>" for line in reversed(current_logs)])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard</title>
        {CSS}
        <meta http-equiv="refresh" content="3"> </head>
    <body>
        <div class="container" style="width: 700px;">
            <h1>{bot_name} Dashboard</h1>
            
            <div class="logs">
                {log_html}
            </div>

            <form action="/shutdown" method="post" onsubmit="return confirm('Are you sure you want to kill the bot?');">
                <button type="submit" class="btn-red">SHUTDOWN BOT</button>
            </form>
            
            <a href="/logout">Logout</a>
        </div>
    </body>
    </html>
    """

# -------------------------
# COG CLASS
# -------------------------
class Website(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.site = None
        self.runner = None
        self.session_token = secrets.token_hex(16)

    async def web_login_page(self, request):
        return web.Response(text=LOGIN_HTML, content_type='text/html')

    async def web_do_login(self, request):
        data = await request.post()
        if data.get("username") == USERNAME and data.get("password") == PASSWORD:
            response = web.HTTPFound('/dashboard')
            response.set_cookie('session', self.session_token, max_age=3600)
            return response
        return web.Response(text="Invalid Credentials <a href='/'>Try Again</a>", content_type='text/html')

    async def web_dashboard(self, request):
        cookie = request.cookies.get('session')
        if cookie != self.session_token:
            return web.HTTPFound('/')

        html = render_dashboard(self.bot.user.name)
        return web.Response(text=html, content_type='text/html')

    async def web_shutdown(self, request):
        cookie = request.cookies.get('session')
        if cookie != self.session_token:
            return web.HTTPFound('/')

        Functions.Log(1, "WebAdmin", "Shutdown command received via Website.")
        asyncio.create_task(self.kill_bot())
        return web.Response(text="Bot is shutting down...", content_type='text/html')

    async def web_logout(self, request):
        response = web.HTTPFound('/')
        response.del_cookie('session')
        return response

    async def kill_bot(self):
        await asyncio.sleep(1)
        await self.bot.close()

    async def cog_load(self):
        self.app = web.Application()
        self.app.add_routes([
            web.get('/', self.web_login_page),
            web.post('/login', self.web_do_login),
            web.get('/dashboard', self.web_dashboard),
            web.post('/shutdown', self.web_shutdown),
            web.get('/logout', self.web_logout),
        ])
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', WEB_PORT)
        await self.site.start()
        print(f"{f.GREEN}[EXT] Website running on http://localhost:{WEB_PORT}{f.RESET}")

    async def cog_unload(self):
        if self.runner:
            await self.runner.cleanup()

async def setup(bot):
    await bot.add_cog(Website(bot))