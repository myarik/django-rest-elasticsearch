from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'example_project.blog'

    def ready(self):
        import example_project.blog.signals  # noqa
