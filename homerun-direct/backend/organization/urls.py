from django.urls import path, include
from rest_framework.routers import DefaultRouter
from organization.viewsets import OrganizationViewSet,BrandViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importing all your viewsets
from .viewsets import (
    BrandViewSet,
    BrandFootersViewSet,
    BrandHeadersViewSet,
    BrandHomePagesViewSet,
    BrandInfosViewSet,
    BrandPagesViewSet,
    BrandPageSliceHeadlineViewSet,
    BrandPageSliceAmenitiesViewSet,
    BrandPageSliceFeaturedListingsViewSet,
    BrandPageSliceGridContentBlocksViewSet,
    BrandPageSliceHeadlineViewSet,
    BrandPageSliceHomepageHerosViewSet,
    BrandPageSliceLocalActivitiesViewSet,
    BrandPageSliceMediaContentBlocksViewSet,
    BrandPageSlicePhotoGalleriesViewSet,
    BrandPageSlicePullQuotesViewSet,
    BrandPageSliceReviewsViewSet,
    BrandPageSliceSingleImagesViewSet,
    BrandPageSliceVideoEmbedsViewSet,
    BrandPageSlicesViewSet,
    BrandsEmployeesViewSet
)

# Initialize the router
router = DefaultRouter()

# Register all the viewsets with the router
router.register(r'api/brands', BrandViewSet, basename='brand')
router.register(r'api/brand-footers', BrandFootersViewSet, basename='brandfooter')
router.register(r'api/brand-headers', BrandHeadersViewSet, basename='brandheader')
router.register(r'api/brand-homepages', BrandHomePagesViewSet, basename='brandhomepage')
router.register(r'api/brand-infos', BrandInfosViewSet, basename='brandinfo')
router.register(r'api/brand-pages', BrandPagesViewSet, basename='brandpage')
router.register(r'api/brand-page-slice-headers', BrandPageSliceHeadlineViewSet, basename='brandpagesliceheader')
router.register(r'api/brand-page-slice-amenities', BrandPageSliceAmenitiesViewSet, basename='brandpagesliceamenity')
router.register(r'api/brand-page-slice-featured-listings', BrandPageSliceFeaturedListingsViewSet, basename='brandpageslicefeaturedlisting')
router.register(r'api/brand-page-slice-grid-content-blocks', BrandPageSliceGridContentBlocksViewSet, basename='brandpageslicegridcontentblock')
router.register(r'api/brand-page-slice-headlines', BrandPageSliceHeadlineViewSet, basename='brandpagesliceheadline')
router.register(r'api/brand-page-slice-homepage-heros', BrandPageSliceHomepageHerosViewSet, basename='brandpageslicehomepagehero')
router.register(r'api/brand-page-slice-local-activities', BrandPageSliceLocalActivitiesViewSet, basename='brandpageslicelocalactivity')
router.register(r'api/brand-page-slice-media-content-blocks', BrandPageSliceMediaContentBlocksViewSet, basename='brandpageslicemediacontentblock')
router.register(r'api/brand-page-slice-photo-galleries', BrandPageSlicePhotoGalleriesViewSet, basename='brandpageslicephotogallery')
router.register(r'api/brand-page-slice-pull-quotes', BrandPageSlicePullQuotesViewSet, basename='brandpageslicepullquote')
router.register(r'api/brand-page-slice-reviews', BrandPageSliceReviewsViewSet, basename='brandpageslicereview')
router.register(r'api/brand-page-slice-single-images', BrandPageSliceSingleImagesViewSet, basename='brandpageslicesingleimage')
router.register(r'api/brand-page-slice-video-embeds', BrandPageSliceVideoEmbedsViewSet, basename='brandpageslicevideoembed')
router.register(r'api/brand-page-slices', BrandPageSlicesViewSet, basename='brandpageslice')
router.register(r'api/brands-employees', BrandsEmployeesViewSet, basename='brandemployee')

router.register(r"api/organization", OrganizationViewSet, basename="organization")
urlpatterns = [
    path("", include(router.urls)),
]
