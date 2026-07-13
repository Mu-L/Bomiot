from django.urls import path
from bomiot.server.function import example

urlpatterns = [
    path(r'example/', example.ExampleList.as_view({"get": "list"}), name="Get Example List"),
    path(r'example/create/', example.ExampleCreate.as_view({"post": "create"}), name="Create Example"),
    path(r'example/update/', example.ExampleUpdate.as_view({"post": "update"}), name="Update Example"),
    path(r'example/delete/', example.ExampleDelete.as_view({"post": "delete"}), name="Delete Example")
]
