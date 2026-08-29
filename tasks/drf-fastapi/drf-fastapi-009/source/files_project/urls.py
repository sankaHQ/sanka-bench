from typing import ClassVar

from artifacts.views import ArtifactViewSet
from rest_framework.routers import DynamicRoute, Route, SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns


class FileRouter(SimpleRouter):
    routes: ClassVar[list[Route | DynamicRoute]] = [
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={"get": "list", "post": "create"},
            name="{basename}-list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        Route(
            url=r"^{prefix}/{lookup}{trailing_slash}$",
            mapping={"get": "retrieve"},
            name="{basename}-detail",
            detail=True,
            initkwargs={"suffix": "Instance"},
        ),
        DynamicRoute(
            url=r"^{prefix}/{lookup}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=True,
            initkwargs={},
        ),
    ]

    def get_urls(self):  # type: ignore[no-untyped-def]
        return format_suffix_patterns(super().get_urls(), allowed=["json", "api"])


router = FileRouter()
router.register("api/files", ArtifactViewSet, basename="artifact")
urlpatterns = router.urls
