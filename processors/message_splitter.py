"""Smart message splitting for Discord's 2000 character limit."""

import re
from typing import List
from utils.logger import get_logger

logger = get_logger("message_splitter")


class MessageSplitter:
    """Splits long messages intelligently while preserving formatting."""

    def __init__(self, max_length: int = 1900):
        """
        Initialize the message splitter.

        Args:
            max_length: Maximum length per chunk (default 1900 to leave room for embed overhead)
        """
        self.max_length = max_length
        self.code_block_pattern = re.compile(r"```(\w*)\n", re.MULTILINE)

    def split(self, content: str) -> List[str]:
        """
        Split content into chunks that fit within Discord's limits.

        Priority for split points:
        1. End of code block
        2. Double newline (paragraph break)
        3. Single newline
        4. Sentence end (. ! ?)
        5. Space (word boundary)
        6. Hard cut (last resort)

        Args:
            content: Content to split

        Returns:
            List of content chunks
        """
        if len(content) <= self.max_length:
            return [content]

        chunks = []
        remaining = content

        while remaining:
            if len(remaining) <= self.max_length:
                # Last chunk
                chunks.append(remaining)
                break

            # Find the best split point
            chunk, remaining = self._find_split_point(remaining)
            chunks.append(chunk)

        logger.debug(f"Split content into {len(chunks)} chunks")
        return chunks

    def _find_split_point(self, content: str) -> tuple[str, str]:
        """
        Find the best point to split the content.

        Returns:
            Tuple of (chunk, remaining_content)
        """
        max_pos = self.max_length

        # Check if we're inside a code block
        code_block_info = self._get_code_block_state(content[:max_pos])

        if code_block_info["inside"]:
            # We're inside a code block, need to close it
            chunk, remaining = self._split_inside_code_block(
                content, max_pos, code_block_info
            )
            return chunk, remaining

        # Try to find good split points in order of priority
        search_start = max(0, max_pos - 500)  # Look back up to 500 chars

        # 1. Try double newline (paragraph break)
        pos = content.rfind("\n\n", search_start, max_pos)
        if pos != -1:
            return content[: pos + 2].rstrip(), content[pos + 2 :].lstrip()

        # 2. Try single newline
        pos = content.rfind("\n", search_start, max_pos)
        if pos != -1:
            return content[: pos + 1].rstrip(), content[pos + 1 :].lstrip()

        # 3. Try sentence end
        for punct in (".", "!", "?"):
            pos = content.rfind(f"{punct} ", search_start, max_pos)
            if pos != -1:
                return (
                    content[: pos + 2].rstrip(),
                    content[pos + 2 :].lstrip(),
                )

        # 4. Try word boundary
        pos = content.rfind(" ", search_start, max_pos)
        if pos != -1:
            return content[:pos].rstrip(), content[pos + 1 :].lstrip()

        # 5. Hard cut (last resort)
        logger.warning(f"Had to perform hard cut at position {max_pos}")
        return content[:max_pos], content[max_pos:]

    def _get_code_block_state(self, content: str) -> dict:
        """
        Determine if we're currently inside a code block.

        Returns:
            Dict with 'inside' (bool) and 'language' (str) keys
        """
        # Count code fence markers (```)
        fence_markers = content.count("```")

        # Odd number means we're inside a code block
        inside = fence_markers % 2 == 1

        language = ""
        if inside:
            # Find the last opening fence to get the language
            last_fence = content.rfind("```")
            if last_fence != -1:
                # Extract language from the line with the fence
                line_end = content.find("\n", last_fence)
                if line_end != -1:
                    fence_line = content[last_fence:line_end]
                    language = fence_line[3:].strip()  # Remove ```

        return {"inside": inside, "language": language}

    def _split_inside_code_block(
        self, content: str, max_pos: int, code_block_info: dict
    ) -> tuple[str, str]:
        """
        Split content when we're inside a code block.

        This will:
        1. Close the code block at the split point
        2. Reopen it in the next chunk
        """
        language = code_block_info["language"]

        # Try to split at a newline within the code block
        search_start = max(0, max_pos - 500)
        pos = content.rfind("\n", search_start, max_pos)

        if pos == -1:
            # No newline found, split at max_pos
            pos = max_pos

        # Create chunk with closing fence
        chunk = content[:pos].rstrip() + "\n```"

        # Create remaining with opening fence
        remaining = f"```{language}\n" + content[pos:].lstrip()

        logger.debug(
            f"Split inside code block (language: {language or 'none'})"
        )

        return chunk, remaining

    def split_with_metadata(
        self, content: str, file_name: str
    ) -> List[dict]:
        """
        Split content and return chunks with metadata.

        Args:
            content: Content to split
            file_name: Name of the file

        Returns:
            List of dicts with 'content', 'part', 'total' keys
        """
        chunks = self.split(content)

        result = []
        for i, chunk in enumerate(chunks, 1):
            result.append(
                {
                    "content": chunk,
                    "part": i,
                    "total": len(chunks),
                    "file_name": file_name,
                }
            )

        return result
