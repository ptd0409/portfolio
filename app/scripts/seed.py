import asyncio
from sqlalchemy import select
from app.db.session import async_session_factory
from app.models.project import Project
from app.models.project_translation import ProjectTranslation
from app.models.tag_translation import TagTranslation
from app.models.tag import Tag
from app.models.project_tag import ProjectTag

async def main():
    async with async_session_factory() as db:
        tag_slug = "fastapi"
        tag = (await db.execute(select(Tag).where(Tag.slug == tag_slug))).scalar_one_or_none()
        if not tag:
            tag = Tag(slug=tag_slug)
            db.add(tag)
            await db.flush()
        
            db.add_all([
                TagTranslation(tag_id=tag.id, lang="en", name="FastAPI"),
                TagTranslation(tag_id=tag.id, lang="vi", name="FastAPI")
            ])
        
        slug = "some-slug"
        project = (await db.execute(select(Project).where(Project.slug == slug))).scalar_one_or_none()
        if not project:
            project = Project(
                slug=slug,
                status="published",
                cover_image_url=None,
                repo_url="https://github.com/ptd0409",
                demo_url="None",
            )
            db.add(project)
            await db.flush()

            db.add_all([
                ProjectTranslation(
                    project_id=project.id,
                    lang="vi",
                    title="Dự án portfolio",
                    summary="FastAPI + PostgreSQL",
                    content_markdown="# Xin chào\n\nĐây là bài viết Markdown tiếng Việt."

                ),
                ProjectTranslation(
                    project_id=project.id,
                    lang="en",
                    title="Portfolio project",
                    summary="FastAPI + PostgreSQL",
                    content_markdown="# Hello\n\nThis is the English Markdown post."
                )
            ])

            db.add(ProjectTag(project_id=project.id, tag_id=tag.id))

        await db.commit()
        print("Seeding OK")

if __name__ == "__main__":
    asyncio.run(main())