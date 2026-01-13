"""GitHub webhook server for receiving push notifications."""

import asyncio
import hashlib
import hmac
import json
from aiohttp import web
from utils.logger import get_logger

logger = get_logger("webhook.server")


class WebhookServer:
    """HTTP server for receiving GitHub webhooks."""

    def __init__(self, bot, config, git_handler):
        """
        Initialize the webhook server.

        Args:
            bot: DocsBot instance
            config: Configuration object
            git_handler: GitHandler instance
        """
        self.bot = bot
        self.config = config
        self.git_handler = git_handler
        self.app = web.Application()
        self.runner = None
        self.site = None

        # Setup routes
        self.app.router.add_post("/webhook", self.handle_webhook)
        self.app.router.add_get("/health", self.health_check)

    async def start(self):
        """Start the webhook server."""
        port = self.config.webhook_port

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, "0.0.0.0", port)
        await self.site.start()

        logger.info(f"Webhook server started on port {port}")
        logger.info(f"Webhook URL: http://your-vps-ip:{port}/webhook")

    async def stop(self):
        """Stop the webhook server."""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Webhook server stopped")

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "ok",
            "bot_connected": self.bot.is_ready() if self.bot else False
        })

    async def handle_webhook(self, request: web.Request) -> web.Response:
        """
        Handle incoming GitHub webhook.

        Args:
            request: aiohttp request object

        Returns:
            HTTP response
        """
        try:
            # Get headers
            event_type = request.headers.get("X-GitHub-Event", "")
            signature = request.headers.get("X-Hub-Signature-256", "")

            # Read body
            body = await request.read()

            # Verify signature if secret is configured
            if self.config.webhook_secret:
                if not self._verify_signature(body, signature):
                    logger.warning("Invalid webhook signature")
                    return web.json_response(
                        {"error": "Invalid signature"}, status=401
                    )

            # Parse JSON
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in webhook payload")
                return web.json_response(
                    {"error": "Invalid JSON"}, status=400
                )

            # Handle different event types
            if event_type == "push":
                await self._handle_push(payload)
                return web.json_response({"status": "processing"})

            elif event_type == "ping":
                logger.info("Received GitHub ping - webhook configured correctly!")
                return web.json_response({"status": "pong"})

            else:
                logger.debug(f"Ignoring event type: {event_type}")
                return web.json_response({"status": "ignored"})

        except Exception as e:
            logger.error(f"Error handling webhook: {e}", exc_info=True)
            return web.json_response(
                {"error": "Internal server error"}, status=500
            )

    def _verify_signature(self, body: bytes, signature: str) -> bool:
        """
        Verify GitHub webhook signature.

        Args:
            body: Request body
            signature: X-Hub-Signature-256 header

        Returns:
            True if valid, False otherwise
        """
        if not signature.startswith("sha256="):
            return False

        secret = self.config.webhook_secret.encode()
        expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
        received = signature[7:]  # Remove "sha256=" prefix

        return hmac.compare_digest(expected, received)

    async def _handle_push(self, payload: dict):
        """
        Handle push event from GitHub.

        Args:
            payload: GitHub push event payload
        """
        ref = payload.get("ref", "")
        branch = ref.replace("refs/heads/", "")

        # Only process pushes to main/master branch
        if branch not in ("main", "master"):
            logger.debug(f"Ignoring push to branch: {branch}")
            return

        # Get list of modified files
        commits = payload.get("commits", [])
        modified_files = set()

        for commit in commits:
            modified_files.update(commit.get("added", []))
            modified_files.update(commit.get("modified", []))

        # Filter for markdown files in docs/
        md_files = [
            f for f in modified_files
            if f.startswith("docs/") and f.endswith(".md")
        ]

        if not md_files:
            logger.info("No markdown files modified in docs/")
            return

        logger.info(f"Push received - {len(md_files)} markdown file(s) modified")

        # Pull changes and process files
        await self.git_handler.pull_and_process(md_files)
