"""Login command - Authenticate with GitHub OAuth."""

import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional

import click

from ..api import exchange_code, API_BASE_URL, APIError, NetworkError
from ..config import set_token, set_user, is_authenticated, get_user


# OAuth callback settings
CALLBACK_PORT = 8765
CALLBACK_TIMEOUT = 120  # 2 minutes


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from GitHub."""
    
    code: Optional[str] = None
    error: Optional[str] = None
    
    def do_GET(self):
        """Handle GET request from OAuth callback."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if "code" in params:
            OAuthCallbackHandler.code = params["code"][0]
            self._send_success()
        elif "error" in params:
            OAuthCallbackHandler.error = params.get("error_description", ["Unknown error"])[0]
            self._send_error()
        else:
            self._send_error()
    
    def _send_success(self):
        """Send success response."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LLMLab - Login Successful</title>
            <style>
                body { font-family: -apple-system, system-ui, sans-serif; display: flex; 
                       justify-content: center; align-items: center; height: 100vh; 
                       margin: 0; background: #0a0a0a; color: #fff; }
                .container { text-align: center; }
                .success { color: #22c55e; font-size: 48px; margin-bottom: 20px; }
                h1 { margin: 0 0 10px; }
                p { color: #888; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✓</div>
                <h1>Login Successful!</h1>
                <p>You can close this window and return to your terminal.</p>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _send_error(self):
        """Send error response."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LLMLab - Login Failed</title>
            <style>
                body { font-family: -apple-system, system-ui, sans-serif; display: flex; 
                       justify-content: center; align-items: center; height: 100vh; 
                       margin: 0; background: #0a0a0a; color: #fff; }
                .container { text-align: center; }
                .error { color: #ef4444; font-size: 48px; margin-bottom: 20px; }
                h1 { margin: 0 0 10px; }
                p { color: #888; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">✗</div>
                <h1>Login Failed</h1>
                <p>Please try again or check the terminal for details.</p>
            </div>
        </body>
        </html>
        """
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress HTTP logs."""
        pass


def wait_for_callback() -> Optional[str]:
    """Start local server and wait for OAuth callback."""
    # Reset state
    OAuthCallbackHandler.code = None
    OAuthCallbackHandler.error = None
    
    server = HTTPServer(("localhost", CALLBACK_PORT), OAuthCallbackHandler)
    server.timeout = 1  # Check every second
    
    start_time = time.time()
    while time.time() - start_time < CALLBACK_TIMEOUT:
        server.handle_request()
        if OAuthCallbackHandler.code or OAuthCallbackHandler.error:
            break
    
    server.server_close()
    return OAuthCallbackHandler.code


@click.command()
@click.option("--force", "-f", is_flag=True, help="Force re-login even if already authenticated")
def login(force: bool):
    """Authenticate with GitHub OAuth.
    
    Opens your browser to login with GitHub. After authorization,
    your credentials will be securely stored locally.
    """
    # Check if already authenticated
    if is_authenticated() and not force:
        user = get_user()
        username = user.get("username", "user") if user else "user"
        click.echo(click.style(f"✓ Already logged in as {username}", fg="green"))
        click.echo("  Use --force to re-login")
        return
    
    # Build OAuth URL
    redirect_uri = f"http://localhost:{CALLBACK_PORT}/callback"
    auth_url = f"{API_BASE_URL}/auth/github?redirect_uri={redirect_uri}"
    
    click.echo("Opening browser for GitHub authentication...")
    click.echo(click.style(f"  {auth_url}", fg="blue", dim=True))
    click.echo()
    
    # Try to open browser
    if not webbrowser.open(auth_url):
        click.echo(click.style("Could not open browser automatically.", fg="yellow"))
        click.echo(f"Please open this URL manually:\n  {auth_url}")
    
    # Wait for callback
    click.echo("Waiting for authentication...")
    with click.progressbar(length=CALLBACK_TIMEOUT, label="", show_eta=False, 
                          show_percent=False, fill_char="▓", empty_char="░") as bar:
        code = None
        # Start server in background
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(wait_for_callback)
            for i in range(CALLBACK_TIMEOUT):
                if future.done():
                    code = future.result()
                    bar.update(CALLBACK_TIMEOUT - i)
                    break
                bar.update(1)
                time.sleep(1)
    
    if OAuthCallbackHandler.error:
        click.echo()
        click.echo(click.style(f"✗ Login failed: {OAuthCallbackHandler.error}", fg="red"))
        raise click.Abort()
    
    if not code:
        click.echo()
        click.echo(click.style("✗ Login timed out. Please try again.", fg="red"))
        raise click.Abort()
    
    # Exchange code for token
    click.echo()
    click.echo("Authenticating...")
    
    try:
        result = exchange_code(code)
        token = result.get("token")
        user = result.get("user", {})
        
        if not token:
            click.echo(click.style("✗ No token received from server", fg="red"))
            raise click.Abort()
        
        # Store credentials
        set_token(token)
        set_user(user)
        
        username = user.get("username", user.get("name", "user"))
        click.echo()
        click.echo(click.style(f"✓ Successfully logged in as {username}", fg="green"))
        click.echo()
        click.echo("Next steps:")
        click.echo("  llmlab configure    Add your API keys")
        click.echo("  llmlab proxy-key    Get your unified proxy key")
        
    except NetworkError as e:
        click.echo(click.style(f"✗ {e.message}", fg="red"))
        raise click.Abort()
    except APIError as e:
        click.echo(click.style(f"✗ {e.message}", fg="red"))
        raise click.Abort()
