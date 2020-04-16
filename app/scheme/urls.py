from django.urls import path

from scheme import views

app_name = 'scheme'
urlpatterns = [
    path('fibers/', views.FiberList.as_view()),
    path('fibers/<int:fiber_pk>', views.Fiber.as_view()),
    path('inputs/', views.InputPigTailList.as_view()),
    path('inputs/<int:input_pk>', views.InputPigTail.as_view()),
    path('outputs/', views.OutputPigTailList.as_view()),
    path('outputs/<int:output_pk>', views.OutputPigTail.as_view()),
    path('splitters/', views.SplitterList.as_view()),
    path('splitters/<str:splitter_lbl>', views.Splitter.as_view()),
]
