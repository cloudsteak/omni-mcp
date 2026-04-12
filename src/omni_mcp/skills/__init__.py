"""Skill registration for built-in MCP tools/resources/prompts."""

from omni_mcp.skills.builtin import register_builtin_skills
from omni_mcp.skills.rss_digest import register_rss_digest_skills

__all__ = ["register_builtin_skills", "register_rss_digest_skills"]
